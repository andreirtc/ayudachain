"""Opt-in fictional residents, residence approvals and claim responses, so barangay screens are not empty.

Additive and idempotent, and it only calls the real commands as the acting account:
  * Residents with an account register their own household; the others are registered by their barangay's
    Punong Barangay (assisted registration, so that officer cannot approve them).
  * Every household except PENDING_RESIDENCE has its residence confirmed by an independent barangay officer.
  * With --with-claims, DSWD opens intake if it is not open, account holders file claims, and officers add the
    sample responses in CLAIMS; the Punong Barangay sends the fully endorsed ones to DSWD.
Everything is synthetic. Nothing is approved by DSWD, published or anchored; those stay human and chain steps.
"""
import sys
from uuid import UUID, uuid4
from backend.app.config import load_local_environment
from backend.app.database import connection
from backend.app.commands import Transaction, execute_command
from backend.app.actor import ActorContext
from backend.app.services import registry, claims
from backend.app.services.evidence import prepare_upload, save_upload
from backend.scripts.synthetic_evidence import synthetic_pdf

# Reference beneficiary accounts -> (barangay, address, zone, members, damage category, damage description).
# People are fictional. Members are (name, birth_date, relationship); the first is the household head.
HOUSEHOLDS = {
    'Cecilia Agbayani': ('Silong', 'Purok 6, Sitio Luntian', '6', [('Cecilia Agbayani', '1975-08-21', 'head'), ('Danilo Agbayani', '1973-02-11', 'spouse')], 'Totally damaged', 'Roof and walls destroyed by the typhoon; household moved to a relative.'),
    'Marites Dalisay': ('Silong', 'Purok 2, Sitio Bagong Pag-asa', '2', [('Marites Dalisay', '1984-03-12', 'head'), ('Alfredo Dalisay', '1982-07-01', 'spouse'), ('Joy Dalisay', '2012-11-05', 'child')], 'Partially damaged', 'Roof sheets torn off and the kitchen flooded.'),
    'Rogelio Bautista': ('Silong', 'Purok 4, Calle Mabini', '4', [('Rogelio Bautista', '1971-09-20', 'head'), ('Teresita Bautista', '1974-01-15', 'spouse')], 'Totally damaged', 'House collapsed in the storm surge.'),
    'Josefina Manalo': ('Sapa', 'Purok 1, Sitio Dalampasigan', '1', [('Josefina Manalo', '1966-05-30', 'head'), ('Paolo Manalo', '1994-08-09', 'child')], 'Partially damaged', 'Fence and one wall broken by fallen trees.'),
    'Erlinda Pascual': ('Sapa', 'Purok 3, Riverside Lane', '3', [('Erlinda Pascual', '1979-12-02', 'head'), ('Ben Pascual', '2016-04-18', 'child'), ('Lea Pascual', '2019-06-27', 'child')], 'Totally damaged', 'Riverbank flooding washed away the ground floor.'),
    'Ramon Evangelista': ('Sapa', 'Purok 5, Sitio Mulawin', '5', [('Ramon Evangelista', '1958-02-14', 'head'), ('Norma Evangelista', '1960-10-03', 'spouse')], 'Partially damaged', 'Water damage to the ceiling and the family boat.'),
}

# Further residents per barangay: (address, zone, members, has_account, damage category, damage description).
# Residents with an account register themselves; the rest are assisted registrations.
RESIDENTS = {
    'Silong': [
        ('Purok 1, Calle Rizal', '1', [('Teodoro Mendoza', '1962-04-08', 'head'), ('Luzviminda Mendoza', '1965-09-17', 'spouse'), ('Carlo Mendoza', '1999-01-22', 'child')], True, 'Partially damaged', 'Flooded ground floor and spoiled rice stock.'),
        ('Purok 2, Sitio Bagong Pag-asa', '2', [('Corazon Villareal', '1955-11-30', 'head'), ('Mario Villareal', '1985-06-14', 'child'), ('Anna Villareal', '2013-03-02', 'member')], True, 'Totally damaged', 'Wooden house blown off its posts.'),
        ('Purok 3, Calle Mabini', '3', [('Efren Castillo', '1980-07-25', 'head'), ('Maricel Castillo', '1983-03-09', 'spouse'), ('Jerome Castillo', '2008-10-02', 'child'), ('Kyla Castillo', '2011-12-19', 'child')], True, 'Partially damaged', 'Roof partly collapsed over the bedrooms.'),
        ('Purok 4, Sitio Luntian', '4', [('Nenita Ramos', '1970-02-18', 'head'), ('Joel Ramos', '1996-05-06', 'child')], True, 'Partially damaged', 'Sari-sari store goods and shelves washed out.'),
        ('Purok 5, Calle Bonifacio', '5', [('Arturo Domingo', '1949-08-12', 'head'), ('Pacita Domingo', '1952-01-28', 'spouse')], True, 'Totally damaged', 'Bamboo house crushed by a fallen mango tree.'),
        ('Purok 6, Riverside Lane', '6', [('Lorna Fernandez', '1988-09-03', 'head'), ('Mikaela Fernandez', '2015-02-14', 'child'), ('Gabriel Fernandez', '2018-07-30', 'child')], False, None, None),
        ('Purok 2, Calle Aguinaldo', '2', [('Bernardo Torres', '1977-12-21', 'head'), ('Rowena Torres', '1979-06-05', 'spouse'), ('Nathan Torres', '2005-03-27', 'child')], False, None, None),
    ],
    'Sapa': [
        ('Purok 1, Sitio Dalampasigan', '1', [('Ernesto Santiago', '1960-03-14', 'head'), ('Remedios Santiago', '1963-10-08', 'spouse'), ('Dennis Santiago', '1991-09-01', 'child')], True, 'Totally damaged', 'House washed toward the shore by the surge.'),
        ('Purok 2, Calle Magsaysay', '2', [('Imelda Navarro', '1974-05-22', 'head'), ('Rafael Navarro', '2003-08-16', 'child'), ('Bea Navarro', '2007-01-11', 'child')], True, 'Partially damaged', 'Water damage to walls and school supplies.'),
        ('Purok 3, Riverside Lane', '3', [('Wilfredo Dizon', '1967-11-09', 'head'), ('Gemma Dizon', '1970-04-25', 'spouse')], True, 'Partially damaged', 'Roof leaks and a broken water pump.'),
        ('Purok 4, Sitio Mulawin', '4', [('Rosalinda Cruz', '1982-01-30', 'head'), ('Miguel Cruz', '2010-09-12', 'child')], True, 'Totally damaged', 'Kitchen and living area destroyed by fire after the storm.'),
        ('Purok 5, Calle Luna', '5', [('Feliciano Lim', '1953-06-18', 'head'), ('Aurora Lim', '1956-12-04', 'spouse'), ('Daniel Lim', '1989-02-27', 'member')], True, 'Totally damaged', 'Fishing boat and boat shed destroyed.'),
        ('Purok 6, Sitio Baybayin', '6', [('Maribel Galang', '1991-10-15', 'head'), ('Jasmine Galang', '2017-05-20', 'child')], False, None, None),
        ('Purok 1, Calle Burgos', '1', [('Domingo Tabora', '1972-08-07', 'head'), ('Elena Tabora', '1975-03-13', 'spouse'), ('Kristine Tabora', '2002-11-24', 'child'), ('Paolo Tabora', '2006-06-09', 'child')], False, None, None),
    ],
}

# Left unconfirmed so an independent officer can approve them in the Households tab.
PENDING_RESIDENCE = {'Lorna Fernandez', 'Bernardo Torres', 'Maribel Galang', 'Domingo Tabora'}

# Sample responses for account holders' claims (head name -> plan):
#   wait  - no response yet          one   - the Barangay Secretary endorses
#   split - Secretary endorses, Punong Barangay does not endorse
#   both  - both endorse, then the Punong Barangay sends the claim to DSWD (appears under History)
CLAIMS = {
    'Cecilia Agbayani': 'wait', 'Marites Dalisay': 'both', 'Rogelio Bautista': 'both', 'Teodoro Mendoza': 'one', 'Corazon Villareal': 'one', 'Efren Castillo': 'split', 'Nenita Ramos': 'wait', 'Arturo Domingo': 'wait',
    'Josefina Manalo': 'both', 'Erlinda Pascual': 'one', 'Ramon Evangelista': 'wait', 'Ernesto Santiago': 'one', 'Imelda Navarro': 'split', 'Wilfredo Dizon': 'wait', 'Rosalinda Cruz': 'wait', 'Feliciano Lim': 'one',
}
RESPONSE_HOURS = 168


def _members(people):
    return [{'name': n, 'birth_date': born, 'relationship': rel, 'is_head': i == 0} for i, (n, born, rel) in enumerate(people)]


def _registration(account, barangay_id, address, zone, people):
    return {'beneficiary_actor_id': account, 'phone': None, 'declared_barangay_id': barangay_id, 'address': address, 'zone': zone, 'id_type': None, 'id_number': None, 'head_photo_evidence_id': None, 'id_evidence_id': None, 'members': _members(people)}


def _ensure_accounts(run, names):
    """Reference-style beneficiary accounts for sample residents, created the way seed_mvp creates actors."""
    with connection(purpose='owner') as db:
        office = db.execute('SELECT office_id FROM evaluation_runs WHERE id=%s', (run,)).fetchone()['office_id']
        system = db.execute("SELECT id FROM actors WHERE run_id=%s AND role='system'", (run,)).fetchone()['id']
        have = {r['display_name'] for r in db.execute("SELECT display_name FROM actors WHERE run_id=%s AND role='beneficiary'", (run,)).fetchall()}
        tx = Transaction(db, ActorContext(system, run, office, 'system', 'Local scheduler', None, None, None, None, 'system'), uuid4())
        for name in names:
            if name in have: continue
            identity, version = uuid4(), uuid4()
            tx.insert('actors', {'id': identity, 'role': 'beneficiary', 'display_name': name, 'email': None, 'current_version_id': version, 'current_member_link_id': None, 'revision': 0})
            tx.insert('actor_versions', {'id': version, 'actor_id': identity, 'predecessor_id': None, 'status': 'active', 'barangay_id': None, 'position': None, 'nomination_id': None, 'approved_by': None, 'reason': 'Opt-in synthetic sample resident account'})
            tx.audit('reference.actor', [('actor_version_id', version)])
        db.execute('SET CONSTRAINTS ALL IMMEDIATE')


def _upload(actor, purpose, text):
    item = prepare_upload(synthetic_pdf(text), 'application/pdf')
    ack = execute_command(actor, 'evidence.upload', str(uuid4()), {'hash': item['byte_sha256'].hex()}, lambda tx: save_upload(tx, item, purpose, None))
    return UUID(str(ack['resources'][0]['id']))


def seed_households(with_claims=False):
    load_local_environment()
    log = []
    with connection() as db:
        run = db.execute("SELECT id FROM evaluation_runs WHERE state='active'").fetchone()
        if not run: raise SystemExit('No active evaluation run. Run python -m backend.scripts.setup_mvp first.')
        run = run['id']
        barangays = {r['name']: r['id'] for r in db.execute('SELECT id,name FROM barangays WHERE run_id=%s', (run,)).fetchall()}
    _ensure_accounts(run, [r[2][0][0] for rows in RESIDENTS.values() for r in rows if r[3]])

    def state():
        with connection() as db:
            return dict(
                accounts={r['display_name']: r['id'] for r in db.execute("SELECT id,display_name FROM actors WHERE run_id=%s AND role='beneficiary'", (run,)).fetchall()},
                heads={r['name']: r for r in db.execute('SELECT h.id,h.revision,v.assister_id,v.residence_state,m.name FROM households h JOIN household_versions v ON v.id=h.current_version_id JOIN member_versions m ON m.household_version_id=v.id AND m.is_head WHERE h.run_id=%s', (run,)).fetchall()},
                officers={b: [r['id'] for r in db.execute("SELECT a.id FROM actors a JOIN actor_versions v ON v.id=a.current_version_id WHERE a.run_id=%s AND a.role='barangay' AND v.status='active' AND v.barangay_id=%s ORDER BY (v.position='Punong Barangay') DESC, a.display_name", (run, bid)).fetchall()] for b, bid in barangays.items()},
                dswd=db.execute("SELECT id FROM actors WHERE run_id=%s AND role='dswd' ORDER BY display_name LIMIT 1", (run,)).fetchone()['id'])

    # 1. Registrations.
    s = state()
    for name, (barangay, address, zone, people, *_c) in HOUSEHOLDS.items():
        account = s['accounts'].get(name)
        if not account or barangay not in barangays or name in s['heads']: continue
        req = _registration(account, barangays[barangay], address, zone, people)
        execute_command(account, 'registry.register', f'sample-household-{account}', req, lambda tx, req=req: registry.register(tx, req)); log.append(f'registered {name} -> {barangay}')
    s = state()
    for barangay, rows in RESIDENTS.items():
        for address, zone, people, has_account, *_c in rows:
            head = people[0][0]
            if head in s['heads'] or barangay not in barangays: continue
            account = s['accounts'].get(head) if has_account else None
            actor = account or s['officers'][barangay][0]
            req = _registration(account, barangays[barangay], address, zone, people)
            execute_command(actor, 'registry.register', f'sample-resident-{barangay}-{head}', req, lambda tx, req=req: registry.register(tx, req)); log.append(f'registered {head} -> {barangay}' + ('' if account else ' (assisted)'))

    # 2. Residence approvals by an officer who neither lives there nor helped register the household.
    s = state()
    placed = {n: b for n, (b, *_r) in HOUSEHOLDS.items()} | {r[2][0][0]: b for b, rows in RESIDENTS.items() for r in rows}
    for head, barangay in placed.items():
        row = s['heads'].get(head)
        if not row or row['residence_state'] != 'unconfirmed' or head in PENDING_RESIDENCE: continue
        officer = next((o for o in s['officers'][barangay] if o != row['assister_id']), None)
        if not officer: continue
        req = {'expected_revision': row['revision'], 'action': 'residence_confirm', 'reason': 'Synthetic sample: the barangay roll and neighbours confirm this household lives here.'}
        execute_command(officer, 'registry.review', f"sample-residence-{row['id']}", req, lambda tx, req=req, hid=row['id']: registry.review(tx, hid, req)); log.append(f'residence approved {head}')

    if not with_claims: return log
    # 3. Intake, claims and sample responses.
    with connection() as db:
        disaster = db.execute('SELECT id FROM disasters WHERE run_id=%s ORDER BY created_at LIMIT 1', (run,)).fetchone()['id']
        operation = db.execute('SELECT business_status FROM claim_operations WHERE run_id=%s AND disaster_id=%s', (run, disaster)).fetchone()
        categories = {r['label']: r['id'] for r in db.execute('SELECT id,label FROM damage_categories WHERE run_id=%s', (run,)).fetchall()}
    s = state()
    if not operation:
        req = {'disaster_id': disaster, 'barangay_ids': list(barangays.values()), 'response_hours': RESPONSE_HOURS, 'basis_evidence_id': _upload(s['dswd'], 'operation_basis', 'OPERATION BASIS\nSynthetic sample intake for Typhoon Luntian')}
        execute_command(s['dswd'], 'intake.open', 'sample-intake', req, lambda tx: registry.open_intake(tx, req)); log.append('DSWD opened intake for all sample barangays')
    elif operation['business_status'] != 'open':
        log.append('intake is closed; no claims filed'); return log
    details = {n: (d[4], d[5]) for n, d in HOUSEHOLDS.items()} | {r[2][0][0]: (r[4], r[5]) for rows in RESIDENTS.values() for r in rows if r[3]}
    with connection() as db:
        filed = {r['household_id'] for r in db.execute('SELECT household_id FROM claims WHERE run_id=%s', (run,)).fetchall()}
    fresh = {}
    for head, plan in CLAIMS.items():
        row, account = s['heads'].get(head), s['accounts'].get(head)
        if not row or not account or row['id'] in filed: continue
        category, description = details[head]
        req = {'household_id': row['id'], 'disaster_id': disaster, 'stated_category_id': categories[category], 'damage_description': description, 'evidence_ids': [], 'new_information': None}
        ack = execute_command(account, 'claim.submit', f'sample-claim-{account}', req, lambda tx, req=req: claims.submit(tx, req))
        fresh[head] = (plan, placed[head], UUID(str(ack['resources'][0]['id']))); log.append(f'claim filed {head} ({plan})')

    def respond(officer, round_id, kind, reason):
        flags = kind == 'endorse'
        req = {'kind': kind, 'reason': reason, 'residence_attested': flags or None, 'affected_attested': flags or None, 'category_opinion_id': None, 'category_disputed': False, 'related_declared': False, 'parent_response_id': None, 'evidence_ids': []}
        execute_command(officer, 'claim.respond', f'sample-{round_id}-{officer}', req, lambda tx: claims.respond(tx, round_id, req))
    send = {}
    for head, (plan, barangay, claim_id) in fresh.items():
        if plan == 'wait': continue
        with connection() as db:
            round_id = db.execute('SELECT r.id FROM claim_rounds r JOIN claim_submissions s2 ON s2.id=r.submission_id WHERE s2.claim_id=%s ORDER BY r.created_at LIMIT 1', (claim_id,)).fetchone()['id']
        punong, secretary = s['officers'][barangay][0], s['officers'][barangay][1]
        if plan == 'one': respond(secretary, round_id, 'endorse', 'Synthetic sample: known resident whose home was damaged.')
        elif plan == 'split':
            respond(secretary, round_id, 'endorse', 'Synthetic sample: known resident whose home was damaged.')
            respond(punong, round_id, 'not_endorse', 'Synthetic sample: the stated damage does not match what was seen in the purok.')
        elif plan == 'both':
            respond(secretary, round_id, 'endorse', 'Synthetic sample: known resident whose home was damaged.')
            respond(punong, round_id, 'endorse', 'Synthetic sample: confirmed during the purok inspection.')
            send.setdefault(barangay, []).append(round_id)
        log.append(f'responses recorded {head}')
    for barangay, round_ids in send.items():
        punong = s['officers'][barangay][0]
        req = {'disaster_id': disaster, 'barangay_id': barangays[barangay], 'round_ids': round_ids, 'resolution_evidence_id': _upload(punong, 'council_resolution', f'COUNCIL RESOLUTION\nSynthetic sample resolution for {barangay}')}
        execute_command(punong, 'claim.send', f'sample-send-{barangay}', req, lambda tx, req=req: claims.send(tx, req)); log.append(f'{barangay}: Punong Barangay sent {len(round_ids)} claims to DSWD')
    return log


if __name__ == '__main__':
    for line in seed_households('--with-claims' in sys.argv) or ['nothing to add; records already exist']: print(line)
