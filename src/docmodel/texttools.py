import re
import typing as t


def find_strip(strings: t.Sequence[str]) -> str:
    """
    >>> find_strip(['\\n\\t\\t\\t ', ' 44,9 PLN\\n\\t\\t\\t\\t\\t\\t', '\\n\\t\\t\\t '])
    '44,9 PLN'
    """
    return next((s for s in (s.strip() for s in strings) if s), "")


def clean_split_n_strip(self, selector_list) -> str:
    lines = (selector_list.get() or "").split()
    return " ".join(line.strip() for line in lines)


def clean_money(doc_fragment, selector_list) -> t.Optional[t.Dict[str, str]]:
    return text_to_money(selector_list.get())


def text_to_money(value_str: str) -> t.Optional[t.Dict[str, str]]:
    """
    >>> text_to_money('49,9 PLN')
    {'amount': '49.9', 'currency': 'PLN'}
    """
    if not value_str:
        return None
    amount, currency = value_str.split(maxsplit=1)
    return to_money(amount, currency)


def to_money(amount: str, currency: str) -> t.Dict[str, str]:
    """
    >>> to_money('49,9', 'PLN')
    {'amount': '49.9', 'currency': 'PLN'}
    """
    return {"amount": amount.replace(",", "."), "currency": currency}


def find_path_in_css(string: str) -> str:
    """
    >>> find_path_in_css('background-image: url("/o/foo,bar.jpg"); display: block;')
    '/o/foo,bar.jpg'
    >>> find_path_in_css('background-image: url(""); display: block;')
    ''
    >>> find_path_in_css('background-image: url("/o/foo,bar.jpg");\\n background: url("background.jpg");')
    '/o/foo,bar.jpg'
    """
    match = re.search(r'url\((["\'])?(?P<path>.*?)(?(1)\1|)\)', string, re.MULTILINE)
    return match.groups()[1] if match else ""


def clean_all_text(doc_fragment, selector_list) -> str:
    fragments = [
        line.strip()
        for selector in selector_list
        for line in selector.root.text_content().split()
    ]
    return "\n".join(f or "" for f in fragments)
