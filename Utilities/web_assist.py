from bs4 import BeautifulSoup
import ssl
from urllib.request import urlopen
from retry import retry
import re
import warnings
from typing import Union
from bs4.element import NavigableString
import logging


__author__ = 'bmarx'

logger = logging.getLogger(__name__)


def make_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

@retry(tries=3)
def get_html_for_soup(url: str, ct, suffix: str = ''):
    formatted_url = url + suffix
    html = urlopen(formatted_url, context=ct).read()
    soup = BeautifulSoup(html, "html.parser")
    return soup


def find_in_url(url: str,
                item: int = -1,
                cleanup: bool = True) -> str:

    elements = re.findall(r"[^/]+", url)
    try:
        target = elements[item]
    except:
        msg = 'Index %d out of range. defaulting to last element in string.' % item
        warnings.warn(msg, UserWarning, stacklevel=2)
        target = elements[-1]
    
    if cleanup:
        target = re.sub(r'[^A-Za-z0-9]', " ", target)

    return target


def prepend_root_to_url(base_url: str, prefix: str) -> str:

    if base_url[0] == '/':
        url = prefix + base_url
    else:
        url = base_url
    return url


def get_website_chunk_by_class(soup: BeautifulSoup, tag: str, classname: Union[str, None] = None):

    if classname is None:
        sect = soup.find(tag)
    else:
        sect = soup.find(tag, class_=classname)
    return sect


def format_dict_from_soup(tag: NavigableString, substring: str) -> dict:
    content = {}
    for span_vals in tag.find_all(class_=re.compile(substring)):
        # add qty to dictionary. key is nutrient name

        full_text = str(next(span_vals.stripped_strings))
        stripped_text = full_text.replace(' ', '')

        qty = re.findall(r'[0-9\.]+', stripped_text)
        qty_value = qty[0]
        try:
            unit = re.findall(r'[^0-9\.]+', stripped_text)
            unit_value = unit[0]
        except:
            unit_value = ''

        content[span_vals.get('class')[0]] = [qty_value, unit_value]

    return content


# TODO: Make this function able to write dictionaries of any form/nesting to csv
def write_to_csv(filename: str, data: dict, headers: Union[None, list]):

    with open(filename, 'w') as f:
        if headers is not None:
            column_names = ','.join(headers) + '\n'
            f.write(column_names)
        for i, r in data.items():
            for item in list(r):
                f.write("%s,%s\n" % (i, item))


if __name__ == '__main__':
    print(find_in_url('https://www.allrecipes.com/recipes/86/world-cuisine/'))
