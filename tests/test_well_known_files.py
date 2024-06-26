import responses
from sitemap_grabber.well_known_files import (
    WellKnownFiles,
    WellKnownFilesException,
)

# import testing framework
import unittest


# setup testing class
class TestWellKnownFiles(unittest.TestCase):
    def setUp(self):
        self.well_known_files = WellKnownFiles("https://example.com")
        self.robots_txt = "User-agent: *\nDisallow: /"
        self.humans_txt = "Humans: Me"
        self.security_txt = "Contact:"
        self.html_response = "<html><body>"

    @responses.activate
    def test_fetch_robots_txt(self):
        responses.add(
            responses.GET,
            "https://example.com/robots.txt",
            body="User-agent: *\nDisallow: /",
        )
        robots_txt = self.well_known_files.fetch("robots.txt")
        self.assertEqual(robots_txt, "User-agent: *\nDisallow: /")

    @responses.activate
    def test_fetch_humans_txt(self):
        responses.add(
            responses.GET, "https://example.com/humans.txt", body="Humans: Me"
        )
        humans_txt = self.well_known_files.fetch("humans.txt")
        self.assertEqual(humans_txt, "Humans: Me")

    @responses.activate
    def test_fetch_security_txt(self):
        responses.add(
            responses.GET, "https://example.com/security.txt", body="Contact:"
        )
        security_txt = self.well_known_files.fetch("security.txt")
        self.assertEqual(security_txt, "Contact:")

    @responses.activate
    def test_fetch_security_txt_well_known(self):
        responses.add(
            responses.GET,
            "https://example.com/security.txt",
            body=self.html_response,
        )
        responses.add(
            responses.GET,
            "https://example.com/.well-known/security.txt",
            body="Contact:",
        )
        security_txt = self.well_known_files.fetch("security.txt")
        self.assertEqual("Contact:", security_txt)

    # test that website_url does not have http or end with /
    def test_website_url(self):
        # assert raises exception if the code does not raise an exception
        with self.assertRaises(WellKnownFilesException):
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
