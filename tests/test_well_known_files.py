import json

from sitemap_grabber.well_known_files import (
    WellKnownFiles,
    WellKnownFilesError,
)

# import testing framework
import unittest
from unittest.mock import patch, MagicMock


# setup testing class
class TestWellKnownFiles(unittest.TestCase):
    def setUp(self):
        self.well_known_files = WellKnownFiles("https://example.com")
        self.robots_txt = "User-agent: *\nDisallow: /"
        self.humans_txt = "Humans: Me"
        self.security_txt = "Contact:"
        self.assetlinks_json = {"example": ["output"]}
        self.change_password = "https://example.com/new-location"
        self.html_response = "<html><body>"

    @patch("curl_cffi.requests.get")
    def test_fetch_txt(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "User-agent: *\nDisallow: /"
        mock_get.return_value = mock_response

        self.assertEqual(self.well_known_files.robots_txt, "User-agent: *\nDisallow: /")

    @patch("curl_cffi.requests.get")
    def test_fetch_txt_404(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        self.assertEqual(self.well_known_files.robots_txt, "")

    @patch("curl_cffi.requests.get")
    def test_fetch_json(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps(self.assetlinks_json)
        mock_get.return_value = mock_response

        self.assertEqual(self.well_known_files.assetlinks_json, self.assetlinks_json)

    @patch("curl_cffi.requests.get")
    def test_fetch_json_404(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        self.assertEqual(self.well_known_files.assetlinks_json, {})

    @patch("curl_cffi.requests.get")
    def test_security_txt_well_known(self, mock_get):
        def side_effect(url, *args, **kwargs):
            if url == "https://example.com/security.txt":
                return MagicMock(status_code=200, text=self.html_response)
            elif url == "https://example.com/.well-known/security.txt":
                return MagicMock(status_code=200, text="Contact:")
            return MagicMock(status_code=404, text="Not Found")

        mock_get.side_effect = side_effect

        self.assertEqual("Contact:", self.well_known_files.security_txt)

    # test that website_url does not have http or end with /
    def test_website_url(self):
        # assert raises exception if the code does not raise an exception
        with self.assertRaises(WellKnownFilesError):
            WellKnownFiles()
            WellKnownFiles("example.com")

        well_known_files = WellKnownFiles("https://example.com/")
        self.assertEqual(well_known_files.website_url, "https://example.com")

        well_known_files = WellKnownFiles("http://example.com")
        self.assertEqual(well_known_files.website_url, "https://example.com")

        well_known_files = WellKnownFiles("http://example.com/")
        self.assertEqual(well_known_files.website_url, "https://example.com")

        well_known_files = WellKnownFiles("https://example.com/en")
        self.assertEqual(well_known_files.website_url, "https://example.com")

    @patch("curl_cffi.requests.get")
    def test_fetch_all(self, mock_get):
        def side_effect(url, *args, **kwargs):
            if url == "https://example.com/robots.txt":
                return MagicMock(status_code=200, text="User-agent: *\nDisallow: /")
            elif url == "https://example.com/humans.txt":
                return MagicMock(status_code=200, text="Humans: Me")
            elif url == "https://example.com/security.txt":
                return MagicMock(status_code=404, text="Not Found")
            elif url == "https://example.com/.well-known/security.txt":
                return MagicMock(status_code=200, text="Contact:")
            elif url == "https://example.com/.well-known/assetlinks.json":
                return MagicMock(status_code=200, text=json.dumps(self.assetlinks_json))
            elif url == "https://example.com/.well-known/change-password":
                return MagicMock(status_code=302, headers={"Location": "https://example.com/new-location"})

            return MagicMock(status_code=404, text="Not Found")

        mock_get.side_effect = side_effect

        expected_result = {
            "robots.txt": "User-agent: *\nDisallow: /",
            "humans.txt": "Humans: Me",
            "security.txt": "Contact:",
            "assetlinks.json": self.assetlinks_json,
            "change-password": "https://example.com/new-location",
        }

        result = self.well_known_files.fetch_all()
        self.assertDictEqual(result, expected_result)

    @patch("curl_cffi.requests.get")
    def test_change_password(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 302
        mock_response.headers = {"Location": "https://example.com/new-location"}
        mock_get.return_value = mock_response

        self.assertEqual(mock_response.headers["Location"], self.well_known_files.change_password)

    @patch("curl_cffi.requests.get")
    def test_change_password_404(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        self.assertEqual("", self.well_known_files.change_password)
