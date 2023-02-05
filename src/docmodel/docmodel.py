import dataclasses
import typing as t

from parsel import Selector

from .exceptions import IgnoreThisItem
from .urls import Url


@dataclasses.dataclass
class DocMetadata:
    """Describes data about the document, other than the source."""

    url: Url
    domain: Url
    source: str


class FieldInterface:
    ...


class DocFragment:
    """
    >>> html = (
    ...     "<html>"
    ...     " <head>"
    ...     " <base href='http://example.com/' />"
    ...     "  <title>Example website</title>"
    ...     " </head>"
    ...     " <body>"
    ...     " <div id='images'>"
    ...     "  <a href='image1.html'>Name: My image 1 <br /><img src='image1_thumb.jpg' /></a>"
    ...     "  <a href='image2.html'>Name: My image 2 <br /><img src='image2_thumb.jpg' /></a>"
    ...     "  <a href='image3.html'>Name: My image 3 <br /><img src='image3_thumb.jpg' /></a>"
    ...     "  </div>"
    ...     " </body>"
    ...     "</html>"
    ... )

    Ad-hoc DocFragment with ad-hoc field
    >>> from docmodel import Css, Re, XPath
    >>> p = DocFragment(
    ...     text=html,
    ...     fields={'title': XPath('/html/head/title/text()', name='title')}
    ... )
    >>> p.to_dict()
    {'title': 'Example website'}

    Custom DocFragment with fields
    >>> class MyLink(DocFragment):
    ...     a = Css('a::attr(href)')
    ...     image = XPath('.//img/@src')
    >>> MyLink("<a href='image1.html'>Name: My image 1 <br /><img src='image1_thumb.jpg' /></a>").to_dict()
    {'a': 'image1.html', 'image': 'image1_thumb.jpg'}

    >>> class ThePage(DocFragment):
    ...     title = XPath('/html/head/title/text()')
    ...     mylinks = XPath('//a', many=True, model=MyLink)
    ...     mylink = XPath('//a', model=MyLink)
    ...     links = XPath('//a/img', many=True)


    >>> ThePage(html).to_dict() # doctest: +NORMALIZE_WHITESPACE
    {'title': 'Example website',
    'mylinks': [{'a': 'image1.html', 'image': 'image1_thumb.jpg'}, {'a': 'image2.html', 'image': 'image2_thumb.jpg'},
              {'a': 'image3.html', 'image': 'image3_thumb.jpg'}],
    'mylink': {'a': 'image1.html', 'image': 'image1_thumb.jpg'},
    'links': ['<img src="image1_thumb.jpg">', '<img src="image2_thumb.jpg">', '<img src="image3_thumb.jpg">']}
    """

    _fields: t.Dict[str, t.Optional[FieldInterface]] = {}
    to_be_ignored: bool = False

    def __init__(
        self,
        text: str = None,
        selector: Selector = None,
        fields: t.Mapping[str, FieldInterface] = None,
        metadata: DocMetadata = None,
    ):
        self.html = text
        self.selector = selector or Selector(text=text)
        self.metadata = metadata
        if fields:
            self._fields = {**self._fields, **fields}

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls._fields = {
            k: v
            for k, v in cls.__dict__.items()
            if isinstance(v, FieldInterface) and not v.excluded
        }

    def get_field(self, name):
        return self._fields[name]

    def to_dict(self) -> dict:
        try:
            return {k: f.to_value(self) for k, f in self._fields.items()}
        except IgnoreThisItem:
            self.to_be_ignored = True

    async def async_to_dict(self) -> dict:
        try:
            return {k: await f.async_to_value(self) for k, f in self._fields.items()}
        except IgnoreThisItem:
            self.to_be_ignored = True

    def __repr__(self):
        data = repr(self.selector.get()[:40])
        return f"<{self.__class__.__name__} xpath={self.selector._expr} data={data}>"


class DocModel(DocFragment):
    ...
