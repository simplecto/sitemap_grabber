import html
import logging
import re
from urllib.parse import urljoin
from xml.etree.ElementTree import Element, ParseError

from defusedxml.ElementTree import fromstring

from sitemap_grabber.well_known_files import WellKnownFiles, get_url

logger = logging.getLogger(__name__)

TIMEOUT = 30


class SitemapGrabber:
    """SitemapGrabber class to get all sitemaps from a website."""

    COMMON_SITEMAP_LOCATIONS = [  # noqa: RUF012
        "/sitemap.xml",
        "/sitemap_index.xml",
        "/sitemap/sitemap.xml",
        "/sitemap/sitemap_index.xml",
    ]

    def __init__(self, website_url: str, blacklist_patterns: list[str] | None = None) -> None:
        """Initialize the SitemapGrabber.

        :param website_url:
        :param blacklist_patterns:
        """
        self.well_known_files = WellKnownFiles(website_url)
        self.website_url = self.well_known_files.website_url
        self.blacklist_patterns = blacklist_patterns

        self.sitemaps_crawled = set()  # set of sitemaps already crawled
        self.sitemap_urls = []

    def _add_sitemap(self, url: str) -> None:
        """Add a sitemap to the list of sitemaps we have crawled/seen.

        :param url:
        :return:
        """
        if url.lower() not in self.sitemaps_crawled:
            self.sitemap_urls.append(url)

        self.sitemaps_crawled.add(url.lower())

    def _extract_sitemaps_from_robots_txt(self) -> None:
        """Extract the sitemap urls from the robots.txt file.

        :return:
        """
        robots_txt = self.well_known_files.robots_txt

        for line in robots_txt.split("\n"):
            # regex case-insensitive match
            if re.match(r"^sitemap:.*", line, re.IGNORECASE):
                url = line.split(": ")[1].strip()
                self.sitemap_urls.append(url)

        if len(self.sitemap_urls) == 0:
            logger.info("No sitemaps found in robots.txt.")
            self._check_common_sitemap_locations()

    def _check_common_sitemap_locations(self) -> None:
        """Check the common sitemap locations. Add any valid ones to the list.

        :return:
        """
        logger.info("Trying default sitemap locations:")
        for location in self.COMMON_SITEMAP_LOCATIONS:
            url = urljoin(self.website_url, location)
            content = get_url(url)

            if self._is_sitemap(content):
                self.sitemap_urls.append(url)

    @staticmethod
    def _is_sitemap(content: str | None = None) -> bool:
        """Check if the URL is a sitemap.

        :param content:
        :return:
        """
        if not content:
            return False

        return content.startswith("<?xml")

    def get_all_sitemaps(self) -> None:
        """Get all sitemaps from the website.

        :return:
        """
        self._extract_sitemaps_from_robots_txt()

        for sitemap_url in self.sitemap_urls:
            self._recursive_get_sitemaps(sitemap_url)

        # deduplicate the list and sort it
        self.sitemap_urls = list(set(self.sitemap_urls))
        self.sitemap_urls.sort()

    @staticmethod
    def _process_sitemap_content(content: str) -> Element:
        """Process the sitemap content, receiving a string and returning an ElementTree.

        :param content:
        :return:
        """
        try:
            root = fromstring(content)
        except ParseError:
            logger.exception("Error parsing sitemap")
            unescaped_content = html.unescape(content)
            root = fromstring(unescaped_content)

        return root

    def _recursive_get_sitemaps(self, sitemap_url: str) -> None:
        """Given a list of sitemap URLs, get all sitemaps recursively.

        :param sitemap_url:
        :return:
        """
        if sitemap_url.lower() in self.sitemaps_crawled:
            logging.debug("Sitemap already seen: %s", sitemap_url)
            return

        logging.debug("Getting sitemap: %s", sitemap_url)

        content = get_url(sitemap_url)

        # check if it is a sitemap
        if not self._is_sitemap(content):
            logging.warning("Not a sitemap: %s", sitemap_url)
            return

        logging.debug("Adding sitemap: %s", sitemap_url)
        self._add_sitemap(sitemap_url)

        # parse the sitemap
        root = self._process_sitemap_content(content)

        for child in root:
            if child.tag.endswith("sitemap"):
                loc = child[0].text.strip()
                # Resolve relative URLs
                loc = urljoin(sitemap_url, loc)
                logging.debug("Found sitemap: %s", loc)
                self._recursive_get_sitemaps(loc)
            elif child.tag.endswith("sitemapindex"):
                for sitemap in child:
                    loc = sitemap[0].text.strip()
                    loc = urljoin(sitemap_url, loc)
                    self._recursive_get_sitemaps(loc)
