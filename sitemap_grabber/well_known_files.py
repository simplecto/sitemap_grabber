import json
import logging
from urllib.parse import urlparse

from curl_cffi import requests
from curl_cffi.requests.exceptions import RequestException

logger = logging.getLogger(__name__)

TIMEOUT = 30
HTTP_200 = 200
HTTP_REDIRECTS = [301, 302, 303, 307, 308]


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

        if response.status_code == HTTP_200:
            data = response.text

        if response.status_code in HTTP_REDIRECTS:
            data = response.headers["Location"]

    except RequestException as e:
        logger.warning("Error fetching: %s", url)
        logger.warning("Response: %s", e)

    return data


class WellKnownFilesError(Exception):
    """Base exception for WellKnownFiles."""


class WellKnownFiles:
    """Fetch the well-known files from a website (e.g. robots.txt, humans.txt, security.txt)."""

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

    @property
    def robots_txt(self) -> str:
        """Fetch the robots.txt file from the website.

        :return:
        """
        return self.fetch_txt("/robots.txt")

    @property
    def humans_txt(self) -> str:
        """Fetch the humans.txt file from the website.

        :return:
        """
        return self.fetch_txt("/humans.txt")

    @property
    def security_txt(self) -> str:
        """Fetch the security.txt file from the website.

        :return:
        """
        output = self.fetch_txt("/security.txt")

        if output == "" or self._is_html(output):
            output = self.fetch_txt("/.well-known/security.txt")

        return output

    @property
    def assetlinks_json(self) -> dict:
        """Fetch the assetlinks.json file from the website.

        :return:
        """
        return self.fetch_json("/.well-known/assetlinks.json")

    @property
    def change_password(self) -> str:
        """Fetch the change-password file from the website.

        :return:
        """
        return get_url(f"{self.website_url}/.well-known/change-password")

    def fetch_txt(self, uri: str) -> str:
        """Fetch the specified file from the website.

        :param uri: The URI of the file to fetch
        :return: The contents of the file
        """
        if uri in self.cache:
            return self.cache[uri]

        file_url = f"{self.website_url}{uri}"
        response = get_url(file_url)

        if self._is_html(response) or response == "":
            logger.warning("Response is HTML or empty, skipping %s", file_url)

        if response:
            self.cache[uri] = response
            return response

        return ""

    def fetch_json(self, uri: str) -> dict:
        """Fetch the specified JSON file from the website.

        :param uri: The URI of the file to fetch
        :return: The contents of the file
        """
        txt = self.fetch_txt(uri)
        if txt != "":
            return json.loads(txt)

        return {}

    def fetch_all(self) -> dict:
        """Fetch all the well-known files.

        :return: A dictionary of the files and their contents
        """
        return {
            "robots.txt": self.robots_txt,
            "humans.txt": self.humans_txt,
            "security.txt": self.security_txt,
            "assetlinks.json": self.assetlinks_json,
            "change-password": self.change_password,
        }
