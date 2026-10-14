"""The reference seed describes one disaster response with a few staffed barangays and fictional people."""
import re
import unittest
from backend.scripts import seed_mvp

BANNED=re.compile(r'\b(invented|demo|demonstration|static)\b',re.I)


class SeedReferenceTests(unittest.TestCase):
    def names(self):
        yield seed_mvp.FIELD_OFFICE
        yield from seed_mvp.BARANGAYS
        yield from seed_mvp.DISASTERS
        yield from seed_mvp.NOMINATORS
        for _role,people in seed_mvp.ACTORS:yield from people

    def test_scope_is_one_disaster_and_two_or_three_barangays(self):
        self.assertEqual(len(seed_mvp.DISASTERS),1)
        self.assertIn(len(seed_mvp.BARANGAYS),(2,3))

    def test_every_barangay_is_staffed_by_a_punong_barangay_and_a_secretary(self):
        officers=dict(seed_mvp.ACTORS)['barangay']
        self.assertEqual(len(officers),2*len(seed_mvp.BARANGAYS))
        self.assertEqual(len(seed_mvp.NOMINATORS),len(seed_mvp.BARANGAYS))

    def test_enough_beneficiaries_and_every_role_is_present(self):
        roles=dict(seed_mvp.ACTORS)
        self.assertGreaterEqual(len(roles['beneficiary']),5)
        self.assertGreaterEqual(len(roles['dswd']),2)
        self.assertGreaterEqual(len(roles['disbursing']),2)
        self.assertGreaterEqual(len(roles['auditor']),1)

    def test_names_are_unique_and_free_of_banned_words(self):
        names=list(self.names())
        people=[n for _r,ps in seed_mvp.ACTORS for n in ps if _r!='system']
        self.assertEqual(len(people),len(set(people)),'duplicate person names')
        self.assertEqual([n for n in names if BANNED.search(n)],[])


if __name__=='__main__':unittest.main()
