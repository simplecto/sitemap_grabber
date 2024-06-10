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
        sitemap_grabber._extract_sitemaps_from_robots_txt()
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

    @responses.activate
    def test_is_sitemap_with_good_sitemap(self):
        body = """<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
<url><loc>https://www.example.com</loc></url>
</urlset>"""

        self.assertTrue(SitemapGrabber._is_sitemap(body))

    @responses.activate
    def test_is_sitemap_with_bad_sitemap(self):
        body = """<!doctype html><html lang="en">"""

        self.assertFalse(SitemapGrabber._is_sitemap(body))
        self.assertFalse(SitemapGrabber._is_sitemap(None))

    @responses.activate
    def test_fetch_url(self):
        responses.add(
            responses.GET,
            "https://example.com/sitemap.xml",
            body="""<?xml version="1.0"?>""",
        )

        sitemap_grabber = SitemapGrabber("https://example.com")
        self.assertEqual(
            sitemap_grabber._fetch_url("https://example.com/sitemap.xml"),
            """<?xml version="1.0"?>""",
        )

    @responses.activate
    def test_fetch_url_bad_response(self):
        responses.add(
            responses.GET,
            "https://example.com/sitemap.xml",
            status=404,
        )

        sitemap_grabber = SitemapGrabber("https://example.com")
        self.assertFalse(
            sitemap_grabber._fetch_url("https://example.com/sitemap.xml")
        )

    @responses.activate
    def test_check_common_sitemap_locations(self):
        website = "https://example.com"
        for url in SitemapGrabber.COMMON_SITEMAP_LOCATIONS:
            responses.add(
                responses.GET, f"{website}{url}", body="<?xml version='1.0'?>"
            )

        sitemap_grabber = SitemapGrabber("https://example.com")
        sitemap_grabber._check_common_sitemap_locations()
        self.assertEqual(
            len(sitemap_grabber.sitemap_urls),
            len(SitemapGrabber.COMMON_SITEMAP_LOCATIONS),
        )

    @responses.activate
    def test_extract_sitemaps_from_robots_txt_no_sitemaps_anywhere(self):
        website = "https://example.com"
        responses.add(
            responses.GET,
            f"{website}/robots.txt",
            body="User-agent: *\nDisallow: /",
        )
        for url in SitemapGrabber.COMMON_SITEMAP_LOCATIONS:
            responses.add(responses.GET, f"{website}{url}", status=404)

        sitemap_grabber = SitemapGrabber("https://example.com")
        sitemap_grabber._extract_sitemaps_from_robots_txt()
        self.assertEqual(sitemap_grabber.sitemap_urls, [])

    @responses.activate
    def test_get_all_sitemaps_no_sitemaps_anywhere(self):
        website = "https://example.com"
        responses.add(
            responses.GET,
            f"{website}/robots.txt",
            body="User-agent: *\nDisallow: /",
        )
        for url in SitemapGrabber.COMMON_SITEMAP_LOCATIONS:
            responses.add(responses.GET, f"{website}{url}", status=404)

        sitemap_grabber = SitemapGrabber("https://example.com")
        sitemap_grabber.get_all_sitemaps()
        self.assertEqual(sitemap_grabber.sitemap_urls, [])

    @responses.activate
    def test_recursive_get_sitemaps(self):
        website = "https://example.com"
        responses.add(
            responses.GET,
            f"{website}/robots.txt",
            body=f"User-agent: *\nDisallow: /\nSitemap: {website}/sitemap.xml",
        )
        responses.add(
            responses.GET,
            f"{website}/sitemap.xml",
            body="""<?xml version="1.0"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<sitemap>
<loc>https://example.com/sitemap2.xml</loc>
</sitemap>
<sitemap>
<loc>https://example.com/not-a-sitemap.xml</loc>
</sitemap>
</sitemapindex>""",
        )
        responses.add(
            responses.GET,
            f"{website}/sitemap2.xml",
            body="""<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
<url><loc>https://www.example.com</loc></url>
</urlset>""",
        )

        responses.add(
            responses.GET,
            f"{website}/not-a-sitemap.xml",
            body="""<!doctype html><html lang="en">""",
        )

        sitemap_grabber = SitemapGrabber(website)

        with self.assertLogs(level="WARNING"):
            sitemap_grabber.get_all_sitemaps()

        # sitemap_grabber.get_all_sitemaps()
        self.assertEqual(
            sitemap_grabber.sitemap_urls,
            [
                "https://example.com/sitemap.xml",
                "https://example.com/sitemap2.xml",
            ],
        )
