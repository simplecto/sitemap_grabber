import html
import logging
import re
import xml.etree.ElementTree  # nosec B405

import requests
from defusedxml.ElementTree import fromstring
from fake_useragent import UserAgent
from urllib.parse import urljoin
from .well_known_files import WellKnownFiles


logger = logging.getLogger(__name__)

TIMEOUT = 30


class SitemapGrabber(object):
    def __init__(self, website_url: str, blacklist_patterns: list[str] = None):
        self.well_known_files = WellKnownFiles(website_url)
        self.website_url = self.well_known_files.website_url
        self.blacklist_patterns = blacklist_patterns

        self.sitemaps_crawled = set()
        self.sitemap_urls = []

        self._extract_sitemaps_from_robots_txt()

    def _add_sitemap(self, url: str):
        if url.lower() not in self.sitemaps_crawled:
            self.sitemap_urls.append(url)

        self.sitemaps_crawled.add(url.lower())

    def _extract_sitemaps_from_robots_txt(self):
        """
        Extracts the sitemap urls from the robots.txt file
        :return:
        """
        robots_txt = self.well_known_files.fetch("robots.txt")

        for line in robots_txt.split("\n"):
            # regex case-insensitive match
            if re.match(r"^sitemap:.*", line, re.IGNORECASE):
                url = line.split(": ")[1].strip()
                self.sitemap_urls.append(url)

    def get_all_sitemaps(self):
        """
        Get all sitemaps from the website
        :return:
        """
        for sitemap_url in self.sitemap_urls:
            self._recursive_get_sitemaps(sitemap_url)

        # deduplicate the list and sort it
        self.sitemap_urls = list(set(self.sitemap_urls))
        self.sitemap_urls.sort()

    @staticmethod
    def _process_sitemap_content(
        content: str,
    ) -> xml.etree.ElementTree.Element:
        try:
            root = fromstring(content)
        except xml.etree.ElementTree.ParseError as e:
            logger.error("Error parsing sitemap: %s", e)
            unescaped_content = html.unescape(content)
            root = fromstring(unescaped_content)

        return root

    def _recursive_get_sitemaps(self, sitemap_url: str):
        """
        Given a list of sitemap URLs, get all sitemaps recursively
        :param sitemap_url:
        :return:
        """
        if sitemap_url.lower() in self.sitemaps_crawled:
            logging.debug("Sitemap already seen: %s", sitemap_url)
            return None

        logging.debug("Getting sitemap: %s", sitemap_url)
        response = requests.get(
            sitemap_url, headers={"User-Agent": UserAgent().random}, timeout=30
        )

        # test that it was a good response
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            logging.error("Error fetching: %s", sitemap_url)
            logging.error("Response: %s", e)
            return None

        logging.debug("Adding sitemap: %s", sitemap_url)
        self._add_sitemap(sitemap_url)

        # parse the sitemap
        root = self._process_sitemap_content(response.content.decode("utf-8"))

        for child in root:
            if child.tag.endswith("sitemap"):
                loc = child[0].text.strip()
                # Resolve relative URLs
                loc = urljoin(sitemap_url, loc)
                logging.debug("Found sitemap: %s", loc)
                self._recursive_get_sitemaps(loc)
