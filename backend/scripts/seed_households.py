"""Opt-in sample households for the reference beneficiaries, so barangay screens are not empty.

Additive and idempotent. Each household is registered through the real registry command as its own
beneficiary account, declared in a reference barangay. Registration is not an aid application and
confirms no residence. With --with-claims, each new household also files a claim, but only while DSWD
has intake open for that barangay; the claims then wait for barangay responses as in a real workflow.
Nothing here is approved, endorsed, published or anchored; those stay human and chain steps.
"""
import sys
from uuid import UUID
from backend.app.config import load_local_environment
from backend.app.database import connection
from backend.app.commands import execute_command
from backend.app.services import registry, claims

# Beneficiary account -> (barangay, address, zone, members, damage category label, damage description).
# People are fictional. Members are (name, birth_date, relationship); the first is the household head.
HOUSEHOLDS = {
    'Cecilia Agbayani': ('Silong', 'Purok 6, Sitio Luntian', '6', [('Cecilia Agbayani', '1975-08-21', 'head'), ('Danilo Agbayani', '1973-02-11', 'spouse')], 'Totally damaged', 'Roof and walls destroyed by the typhoon; household moved to a relative.'),
    'Marites Dalisay': ('Silong', 'Purok 2, Sitio Bagong Pag-asa', '2', [('Marites Dalisay', '1984-03-12', 'head'), ('Alfredo Dalisay', '1982-07-01', 'spouse'), ('Joy Dalisay', '2012-11-05', 'child')], 'Partially damaged', 'Roof sheets torn off and the kitchen flooded.'),
    'Rogelio Bautista': ('Silong', 'Purok 4, Calle Mabini', '4', [('Rogelio Bautista', '1971-09-20', 'head'), ('Teresita Bautista', '1974-01-15', 'spouse')], 'Totally damaged', 'House collapsed in the storm surge.'),
    'Josefina Manalo': ('Sapa', 'Purok 1, Sitio Dalampasigan', '1', [('Josefina Manalo', '1966-05-30', 'head'), ('Paolo Manalo', '1994-08-09', 'child')], 'Partially damaged', 'Fence and one wall broken by fallen trees.'),
    'Erlinda Pascual': ('Sapa', 'Purok 3, Riverside Lane', '3', [('Erlinda Pascual', '1979-12-02', 'head'), ('Ben Pascual', '2016-04-18', 'child'), ('Lea Pascual', '2019-06-27', 'child')], 'Totally damaged', 'Riverbank flooding washed away the ground floor.'),
    'Ramon Evangelista': ('Sapa', 'Purok 5, Sitio Mulawin', '5', [('Ramon Evangelista', '1958-02-14', 'head'), ('Norma Evangelista', '1960-10-03', 'spouse')], 'Partially damaged', 'Water damage to the ceiling and the family boat.'),
}

# Residents without accounts, registered by a barangay officer's assisted registration (flagged as assisted, so
# that officer cannot endorse them). (address, zone, members); the first member is the household head.
ASSISTED_HOUSEHOLDS = {
    'Silong': [
        ('Purok 1, Calle Rizal', '1', [('Teodoro Mendoza', '1962-04-08', 'head'), ('Luzviminda Mendoza', '1965-09-17', 'spouse'), ('Carlo Mendoza', '1999-01-22', 'child')]),
        ('Purok 2, Sitio Bagong Pag-asa', '2', [('Corazon Villareal', '1955-11-30', 'head'), ('Mario Villareal', '1985-06-14', 'child'), ('Anna Villareal', '2013-03-02', 'member')]),
        ('Purok 3, Calle Mabini', '3', [('Efren Castillo', '1980-07-25', 'head'), ('Maricel Castillo', '1983-03-09', 'spouse'), ('Jerome Castillo', '2008-10-02', 'child'), ('Kyla Castillo', '2011-12-19', 'child')]),
        ('Purok 4, Sitio Luntian', '4', [('Nenita Ramos', '1970-02-18', 'head'), ('Joel Ramos', '1996-05-06', 'child')]),
        ('Purok 5, Calle Bonifacio', '5', [('Arturo Domingo', '1949-08-12', 'head'), ('Pacita Domingo', '1952-01-28', 'spouse')]),
        ('Purok 6, Riverside Lane', '6', [('Lorna Fernandez', '1988-09-03', 'head'), ('Mikaela Fernandez', '2015-02-14', 'child'), ('Gabriel Fernandez', '2018-07-30', 'child')]),
        ('Purok 2, Calle Aguinaldo', '2', [('Bernardo Torres', '1977-12-21', 'head'), ('Rowena Torres', '1979-06-05', 'spouse'), ('Nathan Torres', '2005-03-27', 'child')]),
    ],
    'Sapa': [
        ('Purok 1, Sitio Dalampasigan', '1', [('Ernesto Santiago', '1960-03-14', 'head'), ('Remedios Santiago', '1963-10-08', 'spouse'), ('Dennis Santiago', '1991-09-01', 'child')]),
        ('Purok 2, Calle Magsaysay', '2', [('Imelda Navarro', '1974-05-22', 'head'), ('Rafael Navarro', '2003-08-16', 'child'), ('Bea Navarro', '2007-01-11', 'child')]),
        ('Purok 3, Riverside Lane', '3', [('Wilfredo Dizon', '1967-11-09', 'head'), ('Gemma Dizon', '1970-04-25', 'spouse')]),
        ('Purok 4, Sitio Mulawin', '4', [('Rosalinda Cruz', '1982-01-30', 'head'), ('Miguel Cruz', '2010-09-12', 'child')]),
        ('Purok 5, Calle Luna', '5', [('Feliciano Lim', '1953-06-18', 'head'), ('Aurora Lim', '1956-12-04', 'spouse'), ('Daniel Lim', '1989-02-27', 'member')]),
        ('Purok 6, Sitio Baybayin', '6', [('Maribel Galang', '1991-10-15', 'head'), ('Jasmine Galang', '2017-05-20', 'child')]),
        ('Purok 1, Calle Burgos', '1', [('Domingo Tabora', '1972-08-07', 'head'), ('Elena Tabora', '1975-03-13', 'spouse'), ('Kristine Tabora', '2002-11-24', 'child'), ('Paolo Tabora', '2006-06-09', 'child')]),
    ],
}


def seed_households(with_claims=False):
    load_local_environment()
    created, claimed, skipped = [], [], []
    assisted = []
    with connection() as db:
        run = db.execute("SELECT id FROM evaluation_runs WHERE state='active'").fetchone()
        if not run: raise SystemExit('No active evaluation run. Run python -m backend.scripts.setup_mvp first.')
        run = run['id']
        accounts = {r['display_name']: r['id'] for r in db.execute("SELECT id,display_name FROM actors WHERE run_id=%s AND role='beneficiary'", (run,)).fetchall()}
        barangays = {r['name']: r['id'] for r in db.execute("SELECT id,name FROM barangays WHERE run_id=%s", (run,)).fetchall()}
        linked = {r['beneficiary_actor_id'] for r in db.execute('SELECT beneficiary_actor_id FROM household_links WHERE run_id=%s', (run,)).fetchall()}
        categories = {r['label']: r['id'] for r in db.execute('SELECT id,label FROM damage_categories WHERE run_id=%s', (run,)).fetchall()}
        disaster = db.execute('SELECT id FROM disasters WHERE run_id=%s ORDER BY created_at LIMIT 1', (run,)).fetchone()
        officers = {}
        for r in db.execute("SELECT a.id,b.name,v.position FROM actors a JOIN actor_versions v ON v.id=a.current_version_id JOIN barangays b ON b.id=v.barangay_id WHERE a.run_id=%s AND a.role='barangay' AND v.status='active' ORDER BY (v.position='Punong Barangay') DESC", (run,)).fetchall():
            officers.setdefault(r['name'], r['id'])
        heads = {r['name'] for r in db.execute('SELECT m.name FROM households h JOIN household_versions v ON v.id=h.current_version_id JOIN member_versions m ON m.household_version_id=v.id AND m.is_head WHERE h.run_id=%s', (run,)).fetchall()}
        claimed_households = {r['household_id'] for r in db.execute('SELECT household_id FROM claims WHERE run_id=%s', (run,)).fetchall()}
        covered = {r['barangay_id'] for r in db.execute("SELECT ob.barangay_id FROM claim_operations o JOIN operation_barangays ob ON ob.operation_version_id=o.current_version_id WHERE o.run_id=%s AND o.business_status='open'", (run,)).fetchall()}
    for name, (barangay, address, zone, people, category, description) in HOUSEHOLDS.items():
        account = accounts.get(name)
        if not account or barangay not in barangays:
            skipped.append(f'{name}: account or barangay {barangay} not in the active run'); continue
        if account not in linked:
            req = {'beneficiary_actor_id': account, 'phone': None, 'declared_barangay_id': barangays[barangay], 'address': address, 'zone': zone, 'id_type': None, 'id_number': None, 'head_photo_evidence_id': None, 'id_evidence_id': None,
                   'members': [{'name': n, 'birth_date': born, 'relationship': rel, 'is_head': i == 0} for i, (n, born, rel) in enumerate(people)]}
            ack = execute_command(account, 'registry.register', f'sample-household-{account}', req, lambda tx, req=req: registry.register(tx, req))
            household = UUID(str(ack['resources'][0]['id'])); created.append(f'{name} -> {barangay}')
        else:
            with connection() as db:
                household = db.execute('SELECT household_id FROM household_links WHERE beneficiary_actor_id=%s AND run_id=%s', (account, run)).fetchone()['household_id']
            skipped.append(f'{name}: household already registered')
        if with_claims and disaster and barangays[barangay] in covered and household not in claimed_households and category in categories:
            req = {'household_id': household, 'disaster_id': disaster['id'], 'stated_category_id': categories[category], 'damage_description': description, 'evidence_ids': [], 'new_information': None}
            execute_command(account, 'claim.submit', f'sample-claim-{account}', req, lambda tx, req=req: claims.submit(tx, req))
            claimed.append(name)
    for barangay, rows in ASSISTED_HOUSEHOLDS.items():
        officer = officers.get(barangay)
        if not officer or barangay not in barangays:
            skipped.append(f'{barangay}: no active officer or barangay in the active run'); continue
        for address, zone, people in rows:
            if people[0][0] in heads: continue
            req = {'beneficiary_actor_id': None, 'phone': None, 'declared_barangay_id': barangays[barangay], 'address': address, 'zone': zone, 'id_type': None, 'id_number': None, 'head_photo_evidence_id': None, 'id_evidence_id': None,
                   'members': [{'name': n, 'birth_date': born, 'relationship': rel, 'is_head': i == 0} for i, (n, born, rel) in enumerate(people)]}
            execute_command(officer, 'registry.register', f'sample-assisted-{barangay}-{people[0][0]}', req, lambda tx, req=req: registry.register(tx, req))
            assisted.append(f'{people[0][0]} -> {barangay}')
    return created + assisted, claimed, skipped


if __name__ == '__main__':
    made, filed, left = seed_households('--with-claims' in sys.argv)
    print(f'Registered {len(made)} households' + (f', filed {len(filed)} claims' if '--with-claims' in sys.argv else '') + '.')
    for line in made: print('  registered', line)
    for line in filed: print('  claim filed', line)
    for line in left: print('  skipped', line)
