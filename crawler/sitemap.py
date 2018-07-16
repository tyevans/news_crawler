import xml.etree.ElementTree as ET
from six.moves.urllib import parse
from reppy.robots import Robots
import requests

ns = {
    "sitemap": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "news": "http://www.google.com/schemas/sitemap-news/0.9",
    "image": "http://www.google.com/schemas/sitemap-image/1.1"
}


def get_text(element, default=None):
    return element.text if element else default


class Sitemap:
    _et = None

    def __init__(self, url):
        self.url = url

    def get_element_tree(self):
        if self._et is None:
            resp = requests.get(self.url)
            self._et = ET.fromstring(resp.content)
        return self._et

    def get_child_sitemap_urls(self):
        etree = self.get_element_tree()
        return [sitemap.find('sitemap:loc', ns).text
                for sitemap in etree.findall("sitemap:sitemap", ns)]

    def get_urls(self):
        etree = self.get_element_tree()
        urls = []
        for url in etree.findall("sitemap:url", ns):
            location = url.find("sitemap:loc", ns)
            last_modified = url.find("sitemap:lastmod", ns)
            change_freq = url.find("sitemap:changefreq", ns)
            priority = url.find("sitemap:priority", ns)

            page = {
                'location': location.text,
                'last_modified': get_text(last_modified),
                'change_freq': get_text(change_freq),
                'priority': get_text(priority)
            }

            news = url.find("news:news", ns)
            if news:
                news_dict = {}
                news_dict['publication'] = {}
                publication = news.find("news:publication", ns)

                news_dict['publication']['name'] = publication.find("news:name",
                                                                    ns).text
                news_dict['publication']['language'] = publication.find(
                    "news:language", ns).text
                news_dict['publication_date'] = get_text(
                    news.find("news:publication_date", ns))
                news_dict['title'] = news.find("news:title", ns).text
                keywords_el = news.find("news:keywords", ns)
                if keywords_el:
                    news_dict['keywords'] = keywords_el.text.split(",")
                page['news'] = news_dict

            image = url.find("image:image", ns)
            if image:
                image_url = image.find("image:loc", ns).text
                page['image'] = image_url
            urls.append(page)

        return urls


def crawl_sitemaps(url, max_depth=1):
    robots = Robots.fetch(parse.urljoin(url, "/robots.txt"))

    sitemap_stack = []
    seen_sitemaps = set()

    for url in robots.sitemaps:
        sitemap_stack.append((url, 0))

    all_urls = []
    while sitemap_stack:
        sitemap_url, depth = sitemap_stack.pop()
        if depth >= max_depth:
            continue

        if sitemap_url in seen_sitemaps:
            continue

        seen_sitemaps.add(sitemap_url)
        sitemap = Sitemap(sitemap_url)
        all_urls.extend(sitemap.get_urls())
        for url in sitemap.get_child_sitemap_urls():
            sitemap_stack.append((url, depth + 1))

    return all_urls
