from bs4 import BeautifulSoup
import ssl
from urllib.request import urlopen
import re
import warnings


def make_context() -> ssl.SSLContext:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

def get_html_for_soup(url: str, ct, suffix: str = ''):
    formatted_url = url + suffix
    html = urlopen(formatted_url, context=ct).read()
    soup = BeautifulSoup(html, "html.parser")
    return soup

def find_in_url(url: str, item: int = -1, cleanup: bool = True) -> str:
    elements = re.findall(r"[^/]+", url)

    try:
        target = elements[item]
    except:
        msg = 'Index %d out of range. defaulting to last element in string.' % item
        warnings.warn(msg, UserWarning, stacklevel=2)
        target = elements[-1]
    
    if cleanup:
        target = re.sub(r'[^A-Za-z0-9]{1}', " ", target)

    return target

def amend_url(base_url: str, prefix: str) -> str:

    if base_url[0] == '/':
        url = prefix + base_url
    else:
        url = base_url
    
    return url


if __name__ == '__main__':
    print(find_in_url('https://www.allrecipes.com/recipes/86/world-cuisine/'))