import unittest
from unittest.mock import patch, MagicMock

from sitemap_grabber.sitemap_grabber import SitemapGrabber


class TestSitemapGrabber(unittest.TestCase):
    @patch("curl_cffi.requests.get")
    def test_add_sitemap(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "User-agent: *\nDisallow: /\nSitemap: https://example.com/sitemap.xml"

        # Set the return value of the mock get function
        mock_get.return_value = mock_response

        sitemap_grabber = SitemapGrabber("https://example.com")
        sitemap_grabber._extract_sitemaps_from_robots_txt()

        mock_get.assert_called_once_with("https://example.com/robots.txt", impersonate="chrome110", timeout=30)
        # add new sitemap
        sitemap_grabber._add_sitemap("https://example.com/sitemap2.xml")
        self.assertEqual(
            sitemap_grabber.sitemap_urls,
            [
                "https://example.com/sitemap.xml",
                "https://example.com/sitemap2.xml",
            ],
        )

    def test_process_sitemap_content_bad_html_entity(self):
        """Handle case when there is a bad html entity in the <loc>. Coinbase
        is the offender here."""

        body = """<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
<url><loc>https://www.coinbase.com/converter/cassie&#128009/aed</loc></url>
</urlset>"""

        with self.assertLogs("sitemap_grabber", "ERROR") as cm:
            SitemapGrabber._process_sitemap_content(body)

        self.assertIn("Error parsing sitemap", cm.output[0])

    def test_is_sitemap_with_good_sitemap(self):
        body = """<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
<url><loc>https://www.example.com</loc></url>
</urlset>"""

        self.assertTrue(SitemapGrabber._is_sitemap(body))

    def test_is_sitemap_with_bad_sitemap(self):
        body = """<!doctype html><html lang="en">"""

        self.assertFalse(SitemapGrabber._is_sitemap(body))
        self.assertFalse(SitemapGrabber._is_sitemap(None))

    @patch("curl_cffi.requests.get")
    def test_check_common_sitemap_locations(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<?xml version='1.0'?>"

        # Set the return value of the mock get function
        mock_get.return_value = mock_response

        sitemap_grabber = SitemapGrabber("https://example.com")
        sitemap_grabber._check_common_sitemap_locations()
        self.assertEqual(
            len(sitemap_grabber.sitemap_urls),
            len(SitemapGrabber.COMMON_SITEMAP_LOCATIONS),
        )

    @patch("curl_cffi.requests.get")
    def test_extract_sitemaps_from_robots_txt_no_sitemaps_anywhere(self, mock_get):
        website = "https://example.com"

        # Define mock responses
        mock_responses = {
            f"{website}/robots.txt": (200, "User-agent: *\nDisallow: /"),
        }

        # Add 404 responses for all common sitemap locations
        for url in SitemapGrabber.COMMON_SITEMAP_LOCATIONS:
            mock_responses[f"{website}{url}"] = (404, "Not Found")

        # Configure the mock to return different responses based on the URL
        def side_effect(url, *args, **kwargs):
            status_code, content = mock_responses.get(url, (404, "Not Found"))
            mock_response = MagicMock()
            mock_response.status_code = status_code
            mock_response.text = content
            return mock_response

        mock_get.side_effect = side_effect

        # Create and test SitemapGrabber
        sitemap_grabber = SitemapGrabber(website)
        sitemap_grabber._extract_sitemaps_from_robots_txt()

        self.assertEqual(sitemap_grabber.sitemap_urls, [])

        # Verify that get was called for robots.txt and all common sitemap locations
        expected_calls = [f"{website}/robots.txt"] + [
            f"{website}{url}" for url in SitemapGrabber.COMMON_SITEMAP_LOCATIONS
        ]
        actual_calls = [call.args[0] for call in mock_get.call_args_list]
        self.assertEqual(set(actual_calls), set(expected_calls))

    @patch("curl_cffi.requests.get")
    def test_recursive_get_sitemaps(self, mock_get):
        website = "https://example.com"

        # Define mock responses
        mock_responses = {
            f"{website}/robots.txt": (200, f"User-agent: *\nDisallow: /\nSitemap: {website}/sitemap.xml"),
            f"{website}/sitemap.xml": (
                200,
                """<?xml version="1.0"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<sitemap>
<loc>https://example.com/sitemap2.xml</loc>
</sitemap>
<sitemap>
<loc>https://example.com/not-a-sitemap.xml</loc>
</sitemap>
</sitemapindex>""",
            ),
            f"{website}/sitemap2.xml": (
                200,
                """<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
<url><loc>https://www.example.com</loc></url>
</urlset>""",
            ),
            f"{website}/not-a-sitemap.xml": (200, """<!doctype html><html lang="en">"""),
        }

        # Configure the mock to return different responses based on the URL
        def side_effect(url, *args, **kwargs):
            status_code, content = mock_responses.get(url, (404, "Not Found"))
            mock_response = MagicMock()
            mock_response.status_code = status_code
            mock_response.text = content
            return mock_response

        mock_get.side_effect = side_effect

        sitemap_grabber = SitemapGrabber(website)

        # Capture and test logs
        with self.assertLogs(level="WARNING") as log_context:
            sitemap_grabber.get_all_sitemaps()

        # Check if a warning was logged (you might want to check for a specific warning message)
        self.assertTrue(any(record.levelname == "WARNING" for record in log_context.records))

        # Assert the sitemap URLs
        self.assertEqual(
            sitemap_grabber.sitemap_urls,
            [
                "https://example.com/sitemap.xml",
                "https://example.com/sitemap2.xml",
            ],
        )

        # Verify that get was called for all expected URLs
        expected_calls = [
            f"{website}/robots.txt",
            f"{website}/sitemap.xml",
            f"{website}/sitemap2.xml",
            f"{website}/not-a-sitemap.xml",
        ]
        actual_calls = [call.args[0] for call in mock_get.call_args_list]
        self.assertEqual(set(actual_calls), set(expected_calls))
