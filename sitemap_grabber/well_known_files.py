from urllib.parse import urlparse

import requests
from fake_useragent import UserAgent


TIMEOUT = 30


# this class is for fetching the well-known files from a website
# (e.g. robots.txt, humans.txt, security.txt)
class WellKnownFiles(object):
    def __init__(self, website_url):
        website_url = website_url.replace("http://", "https://")

        if not website_url.startswith("http"):
            website_url = f"https://{website_url}"

        if website_url.endswith("/"):
            website_url = website_url[:-1]

        # use urlparse to get the domain name
        domain = urlparse(website_url).netloc

        self.website_url = f"https://{domain}"
        self.robots_txt = ""
        self.robots_txt_fetched = False

        self.request_headers = {
            "User-Agent": UserAgent().random,
        }

    @staticmethod
    def is_html(response):
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
            response = requests.get(
                url, headers=self.request_headers, timeout=TIMEOUT
            )
        except requests.exceptions.RequestException:
            return ""

        if self.is_html(response.text):
            return ""

        return response.text

    def fetch_robots_txt(self):
        robots_txt = self._get_response(f"{self.website_url}/robots.txt")

        if not self.is_html(robots_txt) and robots_txt != "":
            self.robots_txt = robots_txt

        self.robots_txt_fetched = True
        return robots_txt

    def fetch_humans_txt(self):
        return self._get_response(f"{self.website_url}/humans.txt")

    def fetch_security_txt(self):
        """
        Fetches the security.txt file from the website. It should look in
        /security.txt and in /.well-known/security.txt
        :return:
        """
        security_txt = self._get_response(f"{self.website_url}/security.txt")
        if not self.is_html(security_txt) and security_txt != "":
            return security_txt

        security_txt = self._get_response(
            f"{self.website_url}/.well-known/security.txt"
        )
        if not self.is_html(security_txt) and security_txt != "":
            return security_txt

        return security_txt

    def fetch_sitemap_xml(self):
        if not self.robots_txt_fetched:
            self.fetch_robots_txt()

        all_sitemaps = []
        for line in self.robots_txt.split("\n"):
            if line.startswith("Sitemap:"):
                all_sitemaps.append(line.split(": ")[1])

        if len(all_sitemaps) > 0:
            return ",".join(all_sitemaps)

        # we made it this far and still no sitemap, let's try the
        # default location
        sitemap_url = f"{self.website_url}/sitemap.xml"
        sitemap_xml = self._get_response(sitemap_url)

        if not self.is_html(sitemap_xml) and sitemap_xml != "":
            return sitemap_url

        return ""
