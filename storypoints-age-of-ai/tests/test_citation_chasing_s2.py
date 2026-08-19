import unittest
from email.message import Message
from unittest.mock import patch
from urllib.error import HTTPError

from gate2.citation_chasing_s2 import _get, _match_title

class CitationChasingS2Tests(unittest.TestCase):
    def test_exact_title_only(self):
        seed={"title":"AI-Assisted Software Delivery"}
        self.assertEqual(_match_title(seed,[{"paperId":"P1","title":"AI Assisted Software Delivery"}])["paperId"],"P1")
        self.assertIsNone(_match_title(seed,[{"paperId":"P2","title":"AI in Chemistry"}]))

    @patch("gate2.citation_chasing_s2.time.sleep")
    @patch("gate2.citation_chasing_s2.urlopen")
    def test_rate_limit_honors_retry_after(self, mocked_open, mocked_sleep):
        headers = Message(); headers["Retry-After"] = "7"
        response = unittest.mock.MagicMock()
        response.__enter__.return_value.read.return_value = b'{"paperId":"P1"}'
        mocked_open.side_effect = [HTTPError("redacted", 429, "rate", headers, None), response]
        self.assertEqual(_get("/paper/P1", {"fields":"paperId"}, "")["paperId"], "P1")
        mocked_sleep.assert_called_once_with(7.0)

    @patch("gate2.citation_chasing_s2.time.sleep")
    @patch("gate2.citation_chasing_s2.urlopen")
    def test_rate_limit_retry_is_bounded(self, mocked_open, mocked_sleep):
        mocked_open.side_effect = HTTPError("redacted", 429, "rate", Message(), None)
        with self.assertRaisesRegex(Exception, "HTTP 429"):
            _get("/paper/P1", {"fields":"paperId"}, "")
        self.assertEqual(mocked_open.call_count, 3)
        self.assertEqual(mocked_sleep.call_count, 2)

if __name__=="__main__": unittest.main()
