import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import time
from Utilities.web_assist import (make_context, get_soup_from_html, get_website_chunk_by_class)

ct = make_context()

test_urls = ['https://www.allrecipes.com/recipe/262697/ham-and-cheese-omelette/',
            'https://www.allrecipes.com/recipe/18100/eggless-crepes/',
            'https://www.allrecipes.com/recipe/271049/kouign-amann/',
            'https://www.allrecipes.com/recipe/183002/chocolate-pancakes/',
            'https://www.allrecipes.com/recipe/216489/mexican-pumpkin-empanadas/',
            'https://www.allrecipes.com/recipe/92486/grilled-peanut-butter-and-banana-sandwich/',
            'https://www.allrecipes.com/recipe/19621/eggs-on-the-grill/',
            'https://www.allrecipes.com/recipe/259088/summertime-mango-drink/',
            'https://www.allrecipes.com/recipe/21544/easy-quiche-lorraine/']


start = time.time() #start time
for url in test_urls:
    soup = get_soup_from_html(url, ct)
    tags = get_website_chunk_by_class(soup, 'div', classname='component breadcrumbs')

    d_d = list(enumerate(tags.stripped_strings))[:-1]
    print(dict(d_d))

end = time.time()
print("Elapsed time is  {}".format(end-start))