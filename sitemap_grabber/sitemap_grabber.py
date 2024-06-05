import requests
from defusedxml.ElementTree import fromstring
from fake_useragent import UserAgent

TIMEOUT = 30


def remove_from_list(lst: list[str], blacklist: list[str]) -> list[str]:
    """
    Remove any strings from a list that contain any found in blacklist

    :param lst:
    :param blacklist:
    :return: a list with the strings removed
    """
    return [s for s in lst if not any(bs in s for bs in blacklist)]


def get_sitemap_urls_from_robots_txt(
    domain: str, blacklist: list[str] = None
) -> list[str]:
    """
    Get a list of sitemap urls from a domain's robots.txt file

    :param domain: The domain to get the sitemap urls from
    :param blacklist: Optional list of strings to blacklist from sitemap urls
    :return: List of sitemap urls
    """
    robots_url = f"https://{domain}/robots.txt"
    useragent = {"User-Agent": UserAgent().random}
    response = requests.get(robots_url, headers=useragent, timeout=TIMEOUT)

    sitemap_urls = []
    for line in response.text.split("\n"):
        if line.startswith("Sitemap:"):
            sitemap_urls.append(line.replace("Sitemap: ", "").strip())

    if blacklist:
        sitemap_urls = remove_from_list(sitemap_urls, blacklist)

    return sitemap_urls


def get_urls_from_sitemap(sitemap_url: str) -> list[str]:
    """
    Get a list of urls from a sitemap url

    :param sitemap_url: The sitemap url to get the urls from
    :return: List of urls
    """
    useragent = {"User-Agent": UserAgent().random}
    response = requests.get(sitemap_url, headers=useragent, timeout=TIMEOUT)
    root = fromstring(response.content)
    urls = [child[0].text for child in root]

    for child in root:
        if child.tag.endswith("sitemap") or child.tag.endswith("urlset"):
            urls += get_urls_from_sitemap(child[0].text)

    return urls


def get_all_urls(domain: str) -> list[str]:
    """
    Get all urls from a domain

    :param domain: The domain to get the urls from
    :return: List of urls
    """
    sitemap_urls = get_sitemap_urls_from_robots_txt(domain)

    urls = []

    for sitemap_url in sitemap_urls:
        urls += get_urls_from_sitemap(sitemap_url)

    return urls


# Example usage
# urls = get_all_urls("cypherhunter.com")
# blacklist = ['/es/', '/zh-hans/', '/zh-hans-bk/']
