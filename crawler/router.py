import re


class PageRouter:

    def __init__(self):
        self._domain_funcs = {}

    def add_route(self, pattern, function):
        self._domain_funcs.setdefault(re.compile(pattern), []).append(function)

    def route(self, page):
        for pattern, func in self._domain_funcs.items():
            if pattern.match(page.parsed_url.netloc):
                for f in func:
                    f(page)
