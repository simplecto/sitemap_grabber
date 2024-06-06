import logging
from urllib.parse import urlparse

import requests
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

TIMEOUT = 30


class WellKnownFilesException(Exception):
    pass


class WellKnownFiles(object):
    """
    This class is for fetching the well-known files from a website
    (e.g. robots.txt, humans.txt, security.txt)
    """

    FILES = {
        "robots.txt": ["/robots.txt"],
        "humans.txt": ["/humans.txt"],
        "security.txt": ["/security.txt", "/.well-known/security.txt"],
    }

    def __init__(self, website_url: str = None):
        if not website_url or not website_url.startswith("http"):
            raise WellKnownFilesException(
                "website_url is required (eg. https://example.com)"
            )

        domain = urlparse(website_url.lower()).netloc
        self.website_url = f"https://{domain}"

        self.request_headers = {
            "User-Agent": UserAgent().random,
        }

        self.cache = {}

    @staticmethod
    def _is_html(response):
        """
            test if the returned content is detected as HTML (which means it
            is not a valid response)
            it should look for "<html" or "<body" in the response
        :param response:
        :return:
        """
        return "<html" in response or "<body" in response

    def _get_response(self, url):
        try:
            logger.debug("Fetching: %s", url)
            response = requests.get(
                url, headers=self.request_headers, timeout=TIMEOUT
            )
            response.raise_for_status()
        except requests.HTTPError as e:
            logger.error("Error fetching: %s", url)
            logger.error("Response: %s", e)
            return ""

        if self._is_html(response.text):
            logger.info("Response is HTML, skipping %s", url)
            return ""

        return response.text

    def fetch(self, file_name: str) -> str:
        """
        Fetches the specified file from the website
        :param file_name: The name of the file to fetch
        :return: The contents of the file
        """
        if file_name in self.cache:
            return self.cache[file_name]

        for path in self.FILES[file_name]:
            file_url = f"{self.website_url}{path}"
            response = self._get_response(file_url)

            if response:
                self.cache[file_name] = response
                return response

        return ""
