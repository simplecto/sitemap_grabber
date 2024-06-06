import unittest
import responses
from sitemap_grabber.sitemap_grabber import SitemapGrabber


class TestSitemapGrabber(unittest.TestCase):
    @responses.activate
    def test_add_sitemap(self):
        responses.add(
            responses.GET,
            "https://example.com/robots.txt",
            body="User-agent: *\nDisallow: /\nSitemap: https://example.com/sitemap.xml",
        )
        sitemap_grabber = SitemapGrabber("https://example.com")
        self.assertEqual(
            sitemap_grabber.sitemap_urls, ["https://example.com/sitemap.xml"]
        )

        # add new sitemap
        sitemap_grabber._add_sitemap("https://example.com/sitemap2.xml")
        self.assertEqual(
            sitemap_grabber.sitemap_urls,
            [
                "https://example.com/sitemap.xml",
                "https://example.com/sitemap2.xml",
            ],
        )

    @responses.activate
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
