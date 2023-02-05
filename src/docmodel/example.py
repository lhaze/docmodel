from docmodel import Css, DocFragment, DocModel, Re, XPath


class ExamplePage(DocFragment):
    title = XPath("//head/title/text()")
    link_for_more = Css("div p a::attr(href)")
    charset = Re("charset=([a-z1-9-]+)")


class ExampleMoreLink(DocFragment):
    title = Css("a::text")
    url = Css("a::attr(href)")


class ExampleMoreNavigation(DocFragment):
    items = Css(".navigation a", many=True, model=ExampleMoreLink)


class StartPage(DocModel):
    title = XPath("//head/title/text()")
    catalogue_pages = Css("div p a::attr(href)", many=True)


class CataloguePage(DocModel):
    items = Css(".navigation a", many=True, model=ExampleMoreLink)
