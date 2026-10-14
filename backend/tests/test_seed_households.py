"""The opt-in sample residents only use reference barangays and fictional people, and the sample plans are consistent."""
import re
import unittest
from backend.scripts import seed_mvp, seed_households

BANNED = re.compile(r'\b(invented|demo|demonstration|static)\b', re.I)
CATEGORIES = set(dict(seed_mvp.DAMAGE_CATEGORIES).values())
RELATIONSHIPS = {'head', 'spouse', 'child', 'member'}


def residents():
    for barangay, rows in seed_households.RESIDENTS.items():
        for address, zone, members, has_account, category, description in rows:
            yield barangay, address, zone, members, has_account, category, description


class SeedHouseholdsTests(unittest.TestCase):
    def test_every_household_belongs_to_a_reference_beneficiary_and_barangay(self):
        self.assertEqual(set(seed_households.HOUSEHOLDS), set(dict(seed_mvp.ACTORS)['beneficiary']))
        for name, (barangay, *_rest) in seed_households.HOUSEHOLDS.items():
            self.assertIn(barangay, seed_mvp.BARANGAYS, name)

    def test_every_barangay_gets_residents_so_no_barangay_screen_is_empty(self):
        placed = {b for b, *_r in seed_households.HOUSEHOLDS.values()} | set(seed_households.RESIDENTS)
        self.assertEqual(placed, set(seed_mvp.BARANGAYS))
        for rows in seed_households.RESIDENTS.values(): self.assertGreaterEqual(len(rows), 5)

    def test_heads_members_and_names_are_well_formed_unique_and_fictional(self):
        households = [d[3] for d in seed_households.HOUSEHOLDS.values()] + [members for _b, _a, _z, members, *_r in residents()]
        people = []
        for members in households:
            self.assertEqual([m[2] for m in members].count('head'), 1)
            self.assertEqual(members[0][2], 'head')
            self.assertTrue(all(m[2] in RELATIONSHIPS for m in members))
            people += [m[0] for m in members]
        self.assertEqual(len(people), len(set(people)))
        self.assertEqual([p for p in people if BANNED.search(p)], [])
        staff = {n for role, names in seed_mvp.ACTORS if role != 'beneficiary' for n in names}
        self.assertEqual(staff & set(people), set())

    def test_account_holders_claim_with_a_known_category_and_description(self):
        for name, d in seed_households.HOUSEHOLDS.items(): self.assertIn(d[4], CATEGORIES); self.assertTrue(d[5])
        for _b, _a, _z, members, has_account, category, description in residents():
            if has_account: self.assertIn(category, CATEGORIES); self.assertTrue(description)
            else: self.assertIsNone(category)

    def test_pending_residences_are_assisted_registrations_and_claims_belong_to_account_holders(self):
        assisted = {m[0][0] for _b, _a, _z, m, has_account, *_r in residents() if not has_account}
        holders = set(seed_households.HOUSEHOLDS) | {m[0][0] for _b, _a, _z, m, has_account, *_r in residents() if has_account}
        self.assertEqual(seed_households.PENDING_RESIDENCE, assisted)
        self.assertTrue(set(seed_households.CLAIMS) <= holders)
        self.assertTrue(set(seed_households.CLAIMS.values()) <= {'wait', 'one', 'split', 'both'})
        self.assertEqual(set(seed_households.CLAIMS) & seed_households.PENDING_RESIDENCE, set())
        where = {name: d[0] for name, d in seed_households.HOUSEHOLDS.items()} | {m[0][0]: b for b, _a, _z, m, *_r in residents()}
        for barangay in seed_mvp.BARANGAYS:
            self.assertIn('both', {plan for head, plan in seed_households.CLAIMS.items() if where[head] == barangay}, barangay)


if __name__ == '__main__': unittest.main()
