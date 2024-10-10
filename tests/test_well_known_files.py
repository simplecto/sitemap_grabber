import responses
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
        self.html_response = "<html><body>"

    @patch("curl_cffi.requests.get")
    def test_fetch_robots_txt(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "User-agent: *\nDisallow: /"
        mock_get.return_value = mock_response

        robots_txt = self.well_known_files.fetch("robots.txt")
        self.assertEqual(robots_txt, "User-agent: *\nDisallow: /")

    @patch("curl_cffi.requests.get")
    def test_fetch_humans_txt(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Humans: Me"
        mock_get.return_value = mock_response

        humans_txt = self.well_known_files.fetch("humans.txt")
        self.assertEqual(humans_txt, "Humans: Me")

    @patch("curl_cffi.requests.get")
    def test_fetch_security_txt(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Contact:"
        mock_get.return_value = mock_response

        security_txt = self.well_known_files.fetch("security.txt")
        self.assertEqual(security_txt, "Contact:")

    @patch("curl_cffi.requests.get")
    def test_fetch_security_txt_well_known(self, mock_get):
        def side_effect(url, *args, **kwargs):
            if url == "https://example.com/security.txt":
                return MagicMock(status_code=200, text=self.html_response)
            elif url == "https://example.com/.well-known/security.txt":
                return MagicMock(status_code=200, text="Contact:")
            return MagicMock(status_code=404, text="Not Found")

        mock_get.side_effect = side_effect

        security_txt = self.well_known_files.fetch("security.txt")
        self.assertEqual("Contact:", security_txt)

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
