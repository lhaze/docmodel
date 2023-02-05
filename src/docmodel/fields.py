import typing as t
from inspect import isawaitable

from parsel import SelectorList

from .docmodel import DocFragment, FieldInterface

Value = t.Union[str, dict, t.List[dict]]
Model = t.Union[DocFragment, t.List[DocFragment]]
ValueOrModel = t.Union[Value, Model]
CleanFunction = t.Callable[[DocFragment, SelectorList], ValueOrModel]


class Field(FieldInterface):
    def __init__(
        self,
        *,
        clean: t.Optional[CleanFunction] = None,
        model: t.Optional[t.Type[DocFragment]] = None,
        many: bool = False,
        name: t.Optional[str] = None,
        excluded: bool = False,
    ):
        self.model = model
        self.many = many
        self.excluded = excluded
        if name:
            self.name = name

        if clean:
            self._clean = clean
        elif model and many:
            self._clean = lambda doc_fragment, selector_list: [
                model(selector=v, metadata=doc_fragment.metadata) for v in selector_list
            ]
        elif model:
            self._clean = lambda doc_fragment, selector_list: model(
                selector=selector_list[0], metadata=doc_fragment.metadata
            )
        elif many:
            self._clean = lambda _, selector_list: selector_list.getall()
        else:
            self._clean = lambda _, selector_list: selector_list.get()

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(
        self,
        doc_fragment: t.Optional[DocFragment],
        owner: t.Optional[t.Type[DocFragment]],
    ) -> t.Union["Field", ValueOrModel]:
        if doc_fragment is None:
            return self
        value = self._get_value(doc_fragment)
        doc_fragment.__dict__[self.name] = value
        return value

    def to_value(self, doc_fragment: DocFragment) -> Value:
        if self.many and self.model:
            return [m.to_dict() for m in self._get_value(doc_fragment)]
        if self.model:
            return self._get_value(doc_fragment).to_dict()
        return self._get_value(doc_fragment)

    async def async_to_value(self, doc_fragment: DocFragment):
        if self.many and self.model:
            return [
                await m.async_to_dict()
                for m in await self._async_get_value(doc_fragment)
            ]
        if self.model:
            instance = await self._async_get_value(doc_fragment)
            return await instance.async_to_dict()
        return await self._async_get_value(doc_fragment)

    def _get_value(self, doc_fragment: DocFragment) -> ValueOrModel:
        # TODO research for async interface for Selector
        selector = self._get_selector(doc_fragment)
        return self._clean(doc_fragment, selector)

    async def _async_get_value(self, doc_fragment: DocFragment) -> ValueOrModel:
        selector = self._get_selector(doc_fragment)
        if isawaitable(self._clean):
            value = await self._clean(doc_fragment, selector)
        else:
            value = self._clean(doc_fragment, selector)
        return value

    def _get_selector(self, doc_fragment: DocFragment) -> SelectorList:
        raise NotImplementedError

    def clean(self, method: CleanFunction) -> None:
        """Decorator for marking a field's clean method"""
        self._clean = method
        return method


class XPath(Field):
    def __init__(self, xpath: str, **kwargs):
        self.xpath = xpath
        super().__init__(**kwargs)

    def _get_selector(self, doc_fragment: DocFragment) -> SelectorList:
        return doc_fragment.selector.xpath(self.xpath)


class Css(Field):
    def __init__(self, css_selector: str, **kwargs):
        self.css_selector = css_selector
        super().__init__(**kwargs)

    def _get_selector(self, doc_fragment: DocFragment) -> SelectorList:
        return doc_fragment.selector.css(self.css_selector)


class Re(Field):
    def __init__(
        self, regex: str, *, clean: t.Callable = None, many: bool = False, **kwargs
    ):
        self.regex = regex
        if not clean:
            if many:
                clean = lambda _, selected: selected
            else:
                clean = lambda _, selected: selected[0] if selected else None
        super().__init__(clean=clean, many=many, **kwargs)

    def _get_selector(self, doc_fragment: DocFragment) -> SelectorList:
        return doc_fragment.selector.re(self.regex)


class Metadata(Field):
    def __init__(
        self,
        attr: str,
        *,
        clean: t.Optional[t.Callable[[Value], Value]] = None,
        name: str = None,
        excluded: bool = False,
    ):
        self.model = None
        self.many = False
        self.attr = attr
        self.name = name
        self.excluded = excluded
        self._clean = clean if clean else lambda value: value

    def _get_value(self, doc_fragment: DocFragment) -> ValueOrModel:
        value = getattr(doc_fragment.metadata, self.attr, None)
        return self._clean(value)


class Noop(Field):
    def __init__(
        self,
        clean: t.Optional[t.Callable[[Value], Value]] = None,
        name: str = None,
        excluded: bool = False,
    ):
        self.model = None
        self.many = False
        self.name = name
        self.excluded = excluded
        self._clean = clean if clean else lambda value: value

    def _get_value(self, doc_fragment: DocFragment) -> ValueOrModel:
        return self._clean(doc_fragment, doc_fragment.selector)
