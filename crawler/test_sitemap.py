import io
import os
from unittest import mock

# This method will be used by the mock to replace requests.get
from crawler.sitemap import Sitemap, crawl_sitemaps


def mocked_requests_get(url, *args, **kwargs):
    class MockResponse:
        def __init__(self, content, status_code):
            self.content = content
            self.status_code = status_code

    if url.endswith("robots.txt"):
        url = "test_robots.txt"

    with open(os.path.join("test_data", url), 'r') as fd:
        data = fd.read()

    return MockResponse(data, 200)


@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_sitemap(mock_get):
    # Assert requests.get calls
    sitemap = Sitemap("test_sitemap.xml")
    urls = sitemap.get_urls()
    assert len(urls) == 1
    url = urls[0]
    assert url['location'] == "http://a.page.example"
    print(url)
    assert url['news']['publication'] == {"name": "CNN", "language": "en"}
    assert url['news']['publication_date'] == "2018-07-16T06:47:26Z"
    assert url['news']['title'] == "A very nice article"
    assert url['image'] == "http://an.image.example.jpg"
