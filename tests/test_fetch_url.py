import unittest
import responses
from well_known_files import get_url


class TestGetUrl(unittest.TestCase):
    @responses.activate
    def test_fetch_url(self):
        responses.add(
            responses.GET,
            "https://example.com/sitemap.xml",
            body="""<?xml version="1.0"?>""",
        )

        self.assertEqual(
            get_url("https://example.com/sitemap.xml"),
            """<?xml version="1.0"?>""",
        )

    @responses.activate
    def test_fetch_url_bad_response(self):
        responses.add(
            responses.GET,
            "https://example.com/sitemap.xml",
            status=404,
        )

        self.assertFalse(get_url("https://example.com/sitemap.xml"))
