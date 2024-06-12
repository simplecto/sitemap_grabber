import logging
from urllib.parse import urlparse

import requests
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

TIMEOUT = 30

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
    "image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def get_url(url: str) -> str:
    """
    Fetches the specified URL. Returns the response text or an empty string.
    Looks like a browser base on its headers.
    :param url:
    :return:
    """
    data = ""  # default return value
    logger.debug("Fetching: %s", url)
    HEADERS["User-Agent"] = UserAgent().random
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.text
    except requests.HTTPError as e:
        logger.debug("Error fetching: %s", url)
        logger.debug("Response: %s", e)

    return data


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

    # Make the headers look more like an actual browser

    def __init__(self, website_url: str = None):
        if not website_url or not website_url.startswith("http"):
            raise WellKnownFilesException(
                "website_url is required (eg. https://example.com)"
            )

        domain = urlparse(website_url.lower()).netloc
        self.website_url = f"https://{domain}"

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
            response = get_url(file_url)

            if self._is_html(response):
                logger.info("Response is HTML, skipping %s", file_url)
                continue

            if response:
                self.cache[file_name] = response
                return response

        return ""
