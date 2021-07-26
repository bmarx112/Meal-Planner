from collections import defaultdict
from Utilities.web_assist import prepend_root_to_url, make_context, get_html_for_soup, find_in_url, write_to_csv
from datetime import datetime as dt
import csv


class RecipeWebScrapeManager:

    def __init__(self,
                 url: str = 'https://www.allrecipes.com',
                 page_limit: int = 100):
        self.base_url = url
        self._context = make_context()
        self._meal_categories = None
        self._recipe_link_dict = None
        self._website_page_limit = page_limit
        print('Initialized at', dt.now())

    @property
    def meal_categories(self):
        if self._meal_categories is None:
            self._meal_categories = self._get_meal_categories()
        return self._meal_categories

    @property
    def recipe_link_dict(self):
        if self._recipe_link_dict is None:
            self._recipe_link_dict = self.get_recipe_links()
        return self._recipe_link_dict

    def _get_meal_categories(self) -> dict:
        recipe_categories = {}
        soup = get_html_for_soup(self.base_url, self._context)
        tags = soup('a')

        for tag in tags:
            try:
                if tag.get('class')[0] in 'see-all-heading':
                    link = tag.get('href')
                    cat = find_in_url(link)
                    recipe_categories[cat] = link
            except:
                continue
        return recipe_categories

    def get_recipe_links(self):
        recipe_links_by_cat = defaultdict(set)

        for cgy, lnk in self.meal_categories.items():
            page_num = 1
            valid_page = True

            while valid_page and page_num <= self._website_page_limit:
                page = '?page=' + str(page_num)
                try:
                    option_page = get_html_for_soup(lnk, self._context, page)
                    print(lnk + page)
                except:
                    valid_page = False
                    continue

                tgs = option_page('a')
                for tg in tgs:
                    try:
                        if ((tg.get('class')[0] in 'card__titleLink manual-link-behavior'
                             and tg.get('aria-hidden')[0] in 'true') or tg.get('class')[0] in 'tout__imageLink'):
                            raw_link = tg.get('href')

                            if '/recipe/' in raw_link:
                                corrected_link = prepend_root_to_url(raw_link, self.base_url)
                                recipe_links_by_cat[cgy].add(corrected_link)
                    except:
                        continue
                page_num += 1
        return recipe_links_by_cat


if __name__ == '__main__':
    scr = RecipeWebScrapeManager(page_limit=15)
    names = ['Category', 'URL']
    write_to_csv('recipeURLs.csv', scr.recipe_link_dict, names)

