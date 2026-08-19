import socket,unittest
from unittest.mock import patch
from gate2.d14_secure_fulltext import active_indicators,fetch,validate_public_https

class SecureFulltextTests(unittest.TestCase):
    @patch('gate2.d14_secure_fulltext.socket.getaddrinfo')
    def test_public_https_only(self,m):
        m.return_value=[(socket.AF_INET,socket.SOCK_STREAM,6,'',('93.184.216.34',443))]
        self.assertEqual(validate_public_https('https://example.org/a.pdf'),'https://example.org/a.pdf')
        with self.assertRaises(ValueError):validate_public_https('http://example.org/a.pdf')
    @patch('gate2.d14_secure_fulltext.socket.getaddrinfo')
    def test_private_ip_rejected(self,m):
        m.return_value=[(socket.AF_INET,socket.SOCK_STREAM,6,'',('127.0.0.1',443))]
        with self.assertRaises(ValueError):validate_public_https('https://example.org/a.pdf')
    def test_active_content_tokens(self):
        self.assertEqual(active_indicators(b'%PDF-1.7 /JavaScript %%EOF'),['/JavaScript'])
        self.assertEqual(active_indicators(b'%PDF-1.7 /OpenAction [1 0 R /FitH] %%EOF'),[])
        self.assertEqual(active_indicators(b'%PDF-1.7 /AAPL /JSTOR %%EOF'),[])
        self.assertEqual(active_indicators(b'%PDF-1.7 /OpenAction 8 0 R 8 0 obj << /S /URI >> %%EOF'),['/S /URI'])
        self.assertEqual(active_indicators(b'%PDF-1.7 safe %%EOF'),[])
    def test_concurrency_is_fail_closed(self):
        with self.assertRaisesRegex(ValueError,'limit must be nonnegative'):fetch(-1,1)
        with self.assertRaisesRegex(ValueError,'workers must be between 1 and 3'):fetch(1,4)
if __name__=='__main__':unittest.main()
