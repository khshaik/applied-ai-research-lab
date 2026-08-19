import unittest
from collections import Counter
from gate2.citation_chasing_s2_revalidate import targets

class S2EmptyRevalidationTests(unittest.TestCase):
    def test_frozen_ambiguous_population(self):
        rows=targets();self.assertEqual(len(rows),13);self.assertEqual(len({(r['family_id'],r['direction']) for r in rows}),13)
        self.assertEqual(set(Counter(r['direction'] for r in rows)),{'backward','forward'})

if __name__=='__main__':unittest.main()
