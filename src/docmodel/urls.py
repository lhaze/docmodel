import typing as t
from pathlib import Path
from urllib import parse as urllib_parse

Url = t.NewType("Url", str)


def get_url(current_href: str, relative: str) -> Url:
    """
    >>> get_url('https://www.iana.org/domains/reserved', '/domains/int')
    'https://www.iana.org/domains/int'
    >>> get_url('https://www.iana.org/domains/reserved/', '/domains/int')
    'https://www.iana.org/domains/int'
    >>> get_url('https://www.iana.org/domains/reserved#foo', '/domains/int')
    'https://www.iana.org/domains/int'
    """
    return Url(urllib_parse.urljoin(current_href + "/", relative))


def clean_url(doc_fragment, selector_list) -> Url:
    return get_url(doc_fragment.metadata.domain, selector_list.get())


def clean_urls(doc_fragment, selector_list) -> t.List[Url]:
    return [
        get_url(doc_fragment.metadata.domain, path) for path in selector_list.getall()
    ]


def get_host_from_url(url: Url):
    """
    >>> get_host_from_url(Url('https://www.iana.org/domains/reserved'))
    'www.iana.org'
    """
    return urllib_parse.urlparse(url).hostname


def get_domain(url: Url) -> Url:
    """
    >>> get_domain(Url('https://www.iana.org/domains/reserved'))
    'https://www.iana.org'
    """
    p = urllib_parse.urlparse(url)
    return Url(f"{p.scheme}://{p.netloc}")


def clean_filter_urls(doc_fragment, selector_list) -> t.List[Url]:
    urls = selector_list.getall()
    return [url for url in urls if not url.startswith("#")]


def get_url_filename(url: Url) -> str:
    """
    >>> get_url_filename(Url('https://www.iana.org/domains/reserved?foo=bar'))
    'reserved'
    >>> get_url_filename(Url('https://www.iana.org/media/product/760/1/foo-4648829.jpg'))
    'foo-4648829.jpg'
    >>> get_url_filename(Url('https://www.iana.org/'))
    ''
    >>> get_url_filename(Url('https://www.iana.org/domains/'))
    ''
    """
    if url.endswith("/"):
        return ""
    path = urllib_parse.urlparse(url).path
    return Path(path).name


def modify_url(url: Url, filename: str = None, query: str = None) -> Url:
    """
    >>> modify_url(Url('https://www.iana.org/domains/reserved?foo=bar'))
    'https://www.iana.org/domains/reserved?foo=bar'
    >>> modify_url(Url('https://www.iana.org/domains/reserved?foo=bar'), query="p=80")
    'https://www.iana.org/domains/reserved?p=80'
    >>> modify_url(Url('https://www.iana.org/media/product/760/1/foo-4648829.jpg?foo=bar'), filename='some.png')
    'https://www.iana.org/media/product/760/1/some.png?foo=bar'
    """
    parsed = urllib_parse.urlparse(url)
    kwargs = {}
    if query:
        kwargs["query"] = query
    if filename:
        path_split = parsed.path.rpartition("/")
        kwargs["path"] = "".join((path_split[0], path_split[1], filename))
    if not kwargs:
        return url
    result = urllib_parse.urlunparse(parsed._replace(**kwargs))
    return Url(result)
