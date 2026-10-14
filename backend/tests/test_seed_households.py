"""The opt-in sample households only use reference accounts and barangays, with fictional people."""
import re
import unittest
from backend.scripts import seed_mvp, seed_households

BANNED = re.compile(r'\b(invented|demo|demonstration|static)\b', re.I)


class SeedHouseholdsTests(unittest.TestCase):
    def test_every_household_belongs_to_a_reference_beneficiary_and_barangay(self):
        beneficiaries = set(dict(seed_mvp.ACTORS)['beneficiary'])
        self.assertEqual(set(seed_households.HOUSEHOLDS), beneficiaries)
        for name, (barangay, *_rest) in seed_households.HOUSEHOLDS.items():
            self.assertIn(barangay, seed_mvp.BARANGAYS, name)

    def test_every_barangay_gets_residents_so_no_barangay_screen_is_empty(self):
        placed = {barangay for barangay, *_rest in seed_households.HOUSEHOLDS.values()}
        self.assertEqual(placed, set(seed_mvp.BARANGAYS))

    def test_heads_are_the_account_holder_and_member_names_are_unique_and_fictional(self):
        people = []
        for name, (_b, address, zone, members, category, description) in seed_households.HOUSEHOLDS.items():
            self.assertEqual(members[0][0], name)
            self.assertEqual(members[0][2], 'head')
            self.assertTrue(address and zone and description)
            self.assertIn(category, dict(seed_mvp.DAMAGE_CATEGORIES).values())
            people += [m[0] for m in members]
        self.assertEqual(len(people), len(set(people)))
        self.assertEqual([p for p in people if BANNED.search(p)], [])

    def test_assisted_residents_are_fictional_unique_and_spread_over_the_reference_barangays(self):
        accounts = [m[0] for *_x, members, _c, _d in seed_households.HOUSEHOLDS.values() for m in members]
        residents = []
        for barangay, rows in seed_households.ASSISTED_HOUSEHOLDS.items():
            self.assertIn(barangay, seed_mvp.BARANGAYS)
            self.assertGreaterEqual(len(rows), 5)
            for address, zone, members in rows:
                self.assertTrue(address and zone)
                self.assertEqual(members[0][2], 'head')
                self.assertEqual([m[2] for m in members].count('head'), 1)
                self.assertTrue(all(m[2] in {'head', 'spouse', 'child', 'member'} for m in members))
                residents += [m[0] for m in members]
        everyone = residents + accounts
        self.assertEqual(len(everyone), len(set(everyone)))
        self.assertEqual([p for p in everyone if BANNED.search(p)], [])
        staff = {n for role, people in seed_mvp.ACTORS for n in people}
        self.assertEqual(staff & set(residents), set())


if __name__ == '__main__': unittest.main()
