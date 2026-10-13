"""Bounded, read-only CSV staging; confirmed rows use the audited registry command.

This deliberately accepts head-only, no-ID declarations. Private facts and other
members can subsequently be supplied through the ordinary permitted forms.
"""
import csv
import hashlib
import io
import json
from datetime import date
from uuid import UUID
from ..actor import require_role
from ..commands import DomainError, execute_command
from ..database import connection
from . import checks, registry

COLUMNS=('name','birth_date','address','zone','declared_barangay_id')
MAX_BYTES=256*1024
MAX_ROWS=100
MAX_CELL=1000


def row_key(actor_id, digest, index):
    return 'csv-v1-'+hashlib.sha256(f'{actor_id}:{digest}:{index}'.encode()).hexdigest()


def parse(content, context, barangays):
    require_role(context,'beneficiary','barangay','dswd')
    try:
        raw=content.encode('utf-8',errors='strict')
    except UnicodeError:raise DomainError(422,'csv_utf8_required') from None
    if len(raw)>MAX_BYTES:raise DomainError(422,'csv_file_limit_256kb')
    try:
        reader=csv.reader(io.StringIO(content.removeprefix('\ufeff'),newline=''),strict=True)
        headers=next(reader,[])
        if len(headers)!=len(set(headers)):raise DomainError(422,'csv_duplicate_headers')
        if set(headers)!=set(COLUMNS):raise DomainError(422,'csv_headers_require_name_birth_date_address_zone_declared_barangay_id_only')
        rows=[];canonical=[];seen=set()
        for cells in reader:
            # Ignore genuinely empty physical rows; row keys use logical records.
            if not cells:continue
            if len(rows)>=MAX_ROWS:raise DomainError(422,'csv_row_limit_100')
            values=dict(zip(headers,(v.strip() for v in cells)))
            errors=[];warnings=[]
            if len(cells)!=len(headers):errors.append('column_count_mismatch')
            for key in COLUMNS:
                value=values.get(key,'')
                if len(value)>MAX_CELL or any(ord(c)<32 for c in value):errors.append(key+'_invalid_text')
            for key,limit in [('name',200),('address',1000),('zone',200)]:
                if not values.get(key) or len(values[key])>limit:errors.append(key+'_required_or_too_long')
            try:
                birth=values.get('birth_date','')
                if birth and (date.fromisoformat(birth).isoformat()!=birth or date.fromisoformat(birth)>date.today()):raise ValueError()
            except ValueError:errors.append('birth_date_requires_past_YYYY_MM_DD')
            if not values.get('birth_date'):warnings.append('birth_date_missing')
            try:
                barangay=UUID(values.get('declared_barangay_id',''))
                if barangay not in barangays:errors.append('barangay_unavailable')
                if context.role=='barangay' and barangay!=context.barangay_id:errors.append('own_barangay_only')
                values['declared_barangay_id']=str(barangay)
            except ValueError:errors.append('declared_barangay_id_requires_UUID')
            fingerprint=tuple(checks.normalize(values.get(k,'')) for k in COLUMNS)
            status='invalid' if errors else 'skipped' if fingerprint in seen else 'valid'
            if status=='skipped':warnings.append('repeated_row_in_upload')
            if not errors:seen.add(fingerprint)
            canonical.append(cells if len(cells)!=len(headers) else values)
            rows.append(dict(index=len(rows)+1,values=values,status=status,errors=errors,warnings=warnings,matches=[]))
        if not rows:raise DomainError(422,'csv_no_data_rows')
        if context.role=='beneficiary' and len(rows)>1:raise DomainError(422,'csv_own_household_one_row_only')
    except csv.Error:raise DomainError(422,'csv_malformed_quoting') from None
    digest=hashlib.sha256(json.dumps(canonical,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
    return rows,digest


def candidates(db,c):
    """Only names/address/birth facts in the selected actor's existing scope."""
    require_role(c,'beneficiary','barangay','dswd')
    return db.execute('''SELECT h.id household_id,h.display_id,v.address,v.zone,v.declared_barangay_id,m.name,m.birth_date
      FROM households h JOIN household_versions v ON v.id=h.current_version_id
      JOIN member_versions m ON m.household_version_id=v.id
      WHERE h.run_id=%s AND h.office_id=%s
      AND (%s!='barangay' OR v.declared_barangay_id=%s)
      AND (%s!='beneficiary' OR h.id=%s)
      ORDER BY h.id,m.member_id''',(c.run_id,c.office_id,c.role,c.barangay_id,c.role,c.household_id)).fetchall()


def matches(values, existing):
    evidence=[]
    for other in existing:
        n=checks.name_score(values['name'],other['name'])
        a=checks.address_score(values['address'],other['address'])
        birth=bool(values.get('birth_date') and other.get('birth_date'))
        same_birth=birth and str(values['birth_date'])==str(other['birth_date'])
        if n>=.88 and (same_birth or a>=.80):
            evidence.append(dict(household_id=str(other['household_id']) if other.get('household_id') else None,
                display_id=other.get('display_id'),row_index=other.get('row_index'),
                name_similarity=format(n,'.4f'),address_similarity=format(a,'.4f'),
                birth_date_match=bool(same_birth),birth_date_comparison='match' if same_birth else 'different' if birth else 'unknown',
                reason='person_in_two_households' if same_birth else 'similar_name_and_address_review'))
    return evidence[:20]


def stage(rows,existing):
    for row in rows:
        if row['status']!='valid':continue
        peers=[dict(r['values'],row_index=r['index']) for r in rows if r['index']!=row['index'] and r['status']!='invalid' and r['values']!=row['values']]
        row['matches']=matches(row['values'],existing)+matches(row['values'],peers)
        if row['matches']:row['status']='needs_review'
    return rows


def registration(values):
    return dict(beneficiary_actor_id=None,phone=None,declared_barangay_id=UUID(values['declared_barangay_id']),
        address=values['address'],zone=values['zone'],id_type=None,id_number=None,head_photo_evidence_id=None,id_evidence_id=None,
        members=[dict(member_id=None,name=values['name'],birth_date=date.fromisoformat(values['birth_date']) if values['birth_date'] else None,relationship='head',is_head=True)])


def preview(content,c):
    with connection() as db:
        barangays={r['id'] for r in db.execute('SELECT id FROM barangays WHERE run_id=%s AND office_id=%s',(c.run_id,c.office_id)).fetchall()}
        rows,digest=parse(content,c,barangays)
        stage(rows,candidates(db,c))
        from ..projections import authorize_reference
        for row in rows:
            if row['status'] in {'invalid','skipped'}:continue
            prior=db.execute('''SELECT r.household_id FROM command_results c JOIN command_result_refs r
              ON r.actor_id=c.actor_id AND r.command_name=c.command_name AND r.idempotency_key=c.idempotency_key
              WHERE c.actor_id=%s AND c.command_name='registry.register' AND c.idempotency_key=%s
              AND c.status_code<400''',(c.actor_id,row_key(c.actor_id,digest,row['index']))).fetchall()
            resources=[]
            for ref in prior:
                if ref['household_id']:
                    authorize_reference(db,c,'household_id',ref['household_id'])
                    resources.append(dict(type='household_id',id=str(ref['household_id'])))
            if resources:row.update(status='saved',resources=resources,replayed=True,matches=[])
    return dict(digest=digest,rows=rows,limits=dict(bytes=MAX_BYTES,rows=MAX_ROWS),algorithm_version=checks.VERSION,
        duplicate_limitations='Review suggestions only: name >= 0.88 plus matching known birth date or address >= 0.80. Missing birth dates are unknown; IDs and phones are not imported or compared. Private/out-of-scope records are excluded.')


def confirm(content,digest,indices,c):
    staged=preview(content,c)
    if staged['digest']!=digest:raise DomainError(409,'csv_preview_content_changed')
    if len(indices)!=len(set(indices)) or any(i<1 or i>len(staged['rows']) for i in indices):raise DomainError(422,'csv_invalid_row_selection')
    outcomes=[]
    # Each row commits independently; retries replay even if the refreshed preview
    # now sees the previously committed household as a possible duplicate.
    for index in indices:
        row=staged['rows'][index-1]
        if row['status'] in {'invalid','skipped'}:
            outcomes.append(dict(index=index,status=row['status'],errors=row['errors'],warnings=row['warnings']));continue
        req=registration(row['values'])
        def save(tx):
            if matches(row['values'],candidates(tx.db,tx.context)) or any(m.get('row_index') for m in row['matches']):
                raise DomainError(409,'csv_duplicate_requires_manual_registry_review')
            return registry.register(tx,req)
        try:
            ack=execute_command(c.actor_id,'registry.register',row_key(c.actor_id,digest,index),req,save)
            outcomes.append(dict(index=index,status='saved',**ack))
        except DomainError as exc:outcomes.append(dict(index=index,status='needs_review' if exc.code=='csv_duplicate_requires_manual_registry_review' else 'failed',error=exc.code))
    return dict(digest=digest,outcomes=outcomes)
