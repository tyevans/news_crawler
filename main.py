from crawler.router import PageRouter
from crawler.crawler import Crawler
from models import insert_page, get_connection
from crawler.sitemap import crawl_sitemaps


def save_page(page):
    db_conn = get_connection()
    insert_page(page.url, page.text(), conn=db_conn)
    db_conn.close()


if __name__ == "__main__":
    # Override the 100 header limit on responses
    # Otherwise our requests to the washington post will fail.
    try:
        import http.client
        http.client._MAXHEADERS = 1000
    except ImportError:
        import httplib
        httplib._MAXHEADERS = 1000


    starting_urls = [
        'http://thehill.com/',
        'http://www.newsweek.com/',
        'https://www.washingtonpost.com/',
        'https://www.wsj.com/',
        'http://thefederalist.com/',
        'http://www.cnn.com/',
        'http://foxnews.com/'
    ]

    urls = []
    for s_url in starting_urls:
        urls.extend(crawl_sitemaps(s_url, max_depth=2))

    router = PageRouter()
    router.add_route('.*', save_page)

    c = Crawler(router, url_stack=[u['location'] for u in urls])
    c.max_depth = 1
    c.start()
