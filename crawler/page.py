from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup


class PageRequestError(Exception):
    pass


class Page:

    def __init__(self, url):
        self.url = url

    @property
    def parsed_url(self):
        if not hasattr(self, '_parsed_url'):
            self._parsed_url = urlparse(self.url)
        return self._parsed_url

    def _get_live_response(self):
        resp = requests.get(self.url)
        if resp.status_code != 200:
            raise PageRequestError
        return resp

    def _get_page_response(self):
        if not hasattr(self, '_live_response'):
            self._live_response = self._get_live_response()
        return self._live_response

    def headers(self):
        return self._get_page_response().headers

    def content_type(self):
        return self.headers()['content-type']

    def content(self):
        return self._get_page_response().content

    def text(self):
        return self._get_page_response().text

    def soup(self):
        return BeautifulSoup(self.text(), 'html.parser')

    def links(self):
        for link in self.soup().find_all('a'):
            url = link.get('href')
            if url:
                if url.lower().startswith('http'):
                    yield url.lower()
                elif url.startswith('/'):
                    yield urljoin(self.url, url)
