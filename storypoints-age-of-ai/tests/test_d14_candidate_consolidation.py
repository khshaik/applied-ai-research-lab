import unittest
from gate2.d14_candidate_consolidation import _occurrences


class D14CandidateConsolidationTests(unittest.TestCase):
    def test_inputs_are_stable_and_unique_by_source_id(self):
        rows=_occurrences()
        self.assertEqual(len(rows),6097)
        self.assertEqual(len({r["citation_occurrence_id"] for r in rows}),6097)
        self.assertEqual(sum(r["discovery_source"]=="OpenAlex" for r in rows),5530)
        self.assertEqual(sum(r["discovery_source"]=="Semantic Scholar" for r in rows),567)


if __name__=="__main__":unittest.main()
