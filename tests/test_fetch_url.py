import unittest
from unittest.mock import patch, MagicMock
from sitemap_grabber.well_known_files import get_url


class TestGetUrl(unittest.TestCase):
    @patch("curl_cffi.requests.get")
    def test_fetch_url(self, mock_get):
        # Create a mock response object
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<?xml version="1.0"?>"""

        # Set the return value of the mock get function
        mock_get.return_value = mock_response

        result = get_url("https://example.com/sitemap.xml")

        mock_get.assert_called_once_with("https://example.com/sitemap.xml", impersonate="chrome110", timeout=30)
        self.assertEqual(result, """<?xml version="1.0"?>""")

    @patch("curl_cffi.requests.get")
    def test_fetch_url_bad_response(self, mock_get):
        # Create a mock response object
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = ""

        # Set the return value of the mock get function
        mock_get.return_value = mock_response

        result = get_url("https://example.com/sitemap.xml")

        mock_get.assert_called_once_with("https://example.com/sitemap.xml", impersonate="chrome110", timeout=30)
        self.assertFalse(result)
