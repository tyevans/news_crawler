import xml.etree.ElementTree as ET
from six.moves.urllib import parse
from reppy.robots import Robots
import requests

xmlns = {
    "sitemap": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "news": "http://www.google.com/schemas/sitemap-news/0.9",
    "image": "http://www.google.com/schemas/sitemap-image/1.1"
}


def get_text(element, default=None):
    return element.text if element is not None else default


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
        return [sitemap.find('sitemap:loc', xmlns).text
                for sitemap in etree.findall("sitemap:sitemap", xmlns)]

    def _extract_news_info(self, urlElement):
        news = urlElement.find("news:news", xmlns)
        if news:
            publication = news.find("news:publication", xmlns)
            news_dict = {
                'publication': {
                    'name': publication.find("news:name", xmlns).text,
                    'language': publication.find("news:language", xmlns).text
                },
                'publication_date': get_text(
                    news.find("news:publication_date", xmlns)),
                'title': news.find("news:title", xmlns).text
            }

            keywords_el = news.find("news:keywords", xmlns)
            if keywords_el:
                news_dict['keywords'] = keywords_el.text.split(",")
            return news_dict

    def get_urls(self):
        etree = self.get_element_tree()
        urls = []
        for url in etree.findall("sitemap:url", xmlns):
            location = url.find("sitemap:loc", xmlns)
            last_modified = url.find("sitemap:lastmod", xmlns)
            change_freq = url.find("sitemap:changefreq", xmlns)
            priority = url.find("sitemap:priority", xmlns)

            page = {
                'location': location.text,
                'last_modified': get_text(last_modified),
                'change_freq': get_text(change_freq),
                'priority': get_text(priority)
            }

            news = self._extract_news_info(url)
            if news is not None:
                page['news'] = news

            image = url.find("image:image", xmlns)
            if image:
                image_url = image.find("image:loc", xmlns).text
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
