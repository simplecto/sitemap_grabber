import logging
from urllib.parse import urlparse

from curl_cffi import requests
from curl_cffi.requests.exceptions import RequestException

logger = logging.getLogger(__name__)

TIMEOUT = 30


def get_url(url: str) -> str:
    """Fetch the specified URL.

    Return the response text or an empty string. Looks like a browser base on
    its headers.
    :param url:
    :return:
    """
    data = ""  # default return value
    logger.debug("Fetching: %s", url)

    try:
        response = requests.get(url, impersonate="chrome110", timeout=TIMEOUT)
        response.raise_for_status()
        data = response.text
    except RequestException as e:
        logger.warning("Error fetching: %s", url)
        logger.warning("Response: %s", e)

    return data


class WellKnownFilesError(Exception):
    """Base exception for WellKnownFiles."""


class WellKnownFiles:
    """Fetch the well-known files from a website (e.g. robots.txt, humans.txt, security.txt)."""

    FILES = {  # noqa: RUF012
        "robots.txt": ["/robots.txt"],
        "humans.txt": ["/humans.txt"],
        "security.txt": ["/security.txt", "/.well-known/security.txt"],
    }

    def __init__(self, website_url: str = "") -> None:
        """Initialize the WellKnownFiles class.

        :param website_url:

        """
        if website_url == "" or not website_url.startswith("http"):
            msg = "website_url is required (eg. https://example.com)"
            raise WellKnownFilesError(msg)

        domain = urlparse(website_url.lower()).netloc
        self.website_url = f"https://{domain}"

        self.cache = {}

    @staticmethod
    def _is_html(response: str) -> bool:
        """Test if the returned content is detected as HTML (which means it is not a valid response).

            It should look for "<html" or "<body" in the response.

        :param response:
        :return:
        """
        return "<html" in response or "<body" in response

    def fetch(self, file_name: str) -> str:
        """Fetch the specified file from the website.

        :param file_name: The name of the file to fetch
        :return: The contents of the file
        """
        if file_name in self.cache:
            return self.cache[file_name]

        for path in self.FILES[file_name]:
            file_url = f"{self.website_url}{path}"
            response = get_url(file_url)

            if self._is_html(response):
                logger.warning("Response is HTML, skipping %s", file_url)
                continue

            if response:
                self.cache[file_name] = response
                return response

        return ""
