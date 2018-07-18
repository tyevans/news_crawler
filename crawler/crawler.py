import re
import time
from logging import getLogger

from crawler.page import Page, PageRequestError
from crawler import __version__, __author__
from six.moves.urllib import parse
from reppy.robots import Robots

logger = getLogger(__name__)


class Crawler:
    """ Web crawler that dispatches crawled pages to a
    router for further processing.
    """
    max_depth = 2
    domain_blacklist = None
    base_domain_pattern = re.compile(r"^(.*?://[^/]+)(?:/.*$|$)")
    user_agent = 'News Crawler v{} - {}'.format(__version__, __author__)
    _headers = {
        'User-Agent': user_agent
    }

    def __init__(self, router, url_stack=None, domain_blacklist_func=None):
        """

        :param router: (`router.PageRouter`) instance.  Used to determine what to do with crawled pages.
        :param url_stack: (`list`) of url strings to start crawling from.
        :param domain_blacklist_func: callable that determines whether a url should be crawled or not (optional)
            Defaults to allowing everything.
        """
        self.url_stack = []
        self.router = router
        self.domain_blacklist_func = domain_blacklist_func or (lambda x: False)
        self._robots_parsers = {}
        self._request_times = {}

        if url_stack:
            for url in url_stack:
                self.push_url(url)

    def get_robots_parser(self, url):
        robots_url = parse.urljoin(url, "/robots.txt")
        r_parser = self._robots_parsers.get(robots_url)

        if not r_parser:
            logger.info("Reading robots.txt: %s", robots_url)
            r_parser = Robots.fetch(robots_url)
            self._robots_parsers[robots_url] = r_parser

        return r_parser

    def can_fetch_url(self, url):
        r_parser = self.get_robots_parser(url)
        is_blacklisted = self.domain_blacklist_func(url)
        return r_parser.allowed(url, self.user_agent) and not is_blacklisted

    def is_delayed(self, url):
        r_parser = self.get_robots_parser(url)
        delay = r_parser.agent(self.user_agent).delay or 0
        now = time.time()
        if self.get_last_request_time(url) + delay < now:
            return False
        return True

    def set_last_request_time(self, url):
        p_url = parse.urlsplit(url)
        self._request_times[p_url.netloc] = time.time()

    def get_last_request_time(self, url):
        p_url = parse.urlsplit(url)
        return self._request_times.get(p_url.netloc, 0)

    def push_url(self, url, depth=0):
        """ Adds `url` to the url stack, depth is how deep into the crawling process
        that this url should be listed at.

        Top level URLs should have a depth of 0 (default).

        urls with a depth >= max_depth will not be crawled.
        """
        if self.can_fetch_url(url):
            self.url_stack.insert(0, (url, depth))

    def start(self):
        """ Begins the process of crawling the urls in the crawler's url stack.

        Does not return until all urls have been crawled to `max_depth`.
        """
        while self.url_stack:
            url, depth = self.url_stack.pop()
            if depth >= self.max_depth:
                continue

            try:
                if not self.is_delayed(url):
                    self.set_last_request_time(url)
                    page = Page(url)
                    for link in page.links():
                        self.push_url(link, depth + 1)
                    self.router.route(page)
                else:
                    self.push_url(url)
            except PageRequestError:
                continue
