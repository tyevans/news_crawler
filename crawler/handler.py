def example_handler(page):
    """ Just an example of a function to handle pages that are crawled.

    :param page: (`page.Page`) instance
    """
    print(page.parsed_url, page.content_type())
