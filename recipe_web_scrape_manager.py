from collections import defaultdict
from Utilities.web_assist import amend_url, make_context, get_html_for_soup, find_in_url
from datetime import datetime as dt
import csv

class RecipeWebScrapeManager:

    def __init__(self,
                url: str = 'https://www.allrecipes.com/'):
        self.base_url = url
        self._context = make_context()
        self._meal_categories = {}
        print('Initialized at', dt.now())

    @property
    def meal_categories(self):
        if self._meal_categories == {}:
            self._get_meal_categories()
        return self._meal_categories

    def _get_meal_categories(self):
        
        soup = get_html_for_soup(self.base_url, self._context)

        tags = soup('a')
        for tag in tags:
            try:
                if tag.get('class')[0] in 'see-all-heading':
                    link = tag.get('href')
                    cat = find_in_url(link)
                    self._meal_categories[cat] = link
            except:
                continue
    

if __name__ == '__main__':
    scr = RecipeWebScrapeManager()
    # [print(i, r) for i, r in scr.meal_categories.items()]
    root_url = 'https://www.allrecipes.com'
    recipelist = defaultdict(set)
    for cat, lnk in scr.meal_categories.items():

        i = 1
        page_limit = 25
        valid_page = True

        while valid_page and i <= page_limit:
            page = '?page='+str(i)
            try:
                option_page = get_html_for_soup(lnk, make_context(), page)
                print(lnk+page)
            except:
                valid_page = False
                continue

            tgs = option_page('a')
            for tg in tgs:
                try:
                    if ((tg.get('class')[0] in 'card__titleLink manual-link-behavior'
                    and tg.get('aria-hidden')[0] in 'true') \
                    or tg.get('class')[0] in 'tout__imageLink'):

                        link = tg.get('href')
                        corrected_link = amend_url(link, root_url)
                        recipelist[cat].add(corrected_link)

                except:
                    continue
            i += 1

    with open('recipeURLs.csv', 'w') as f:
        f.write("Category,URL\n")
        for i, r in recipelist.items():
            for item in list(r):
                f.write("%s,%s\n"%(i,item))

    [print(i, len(r)) for i, r in recipelist.items()]
