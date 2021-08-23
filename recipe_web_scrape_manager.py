from collections import defaultdict
from Utilities.web_assist import (prepend_root_to_url, make_context, get_html_for_soup, find_in_url, 
                                  get_website_chunk_by_class, format_dict_from_soup)
from datetime import datetime as dt
from Objects.meal_info import MealInfo
from Objects.meal_collection import MealCollection
from Objects.batch_meal_collection import BatchMealCollection
from Data_Management.MySQL.mysql_manager import MySqlManager
import logging

__author__ = 'bmarx'

logger = logging.getLogger(__name__)


class RecipeWebScrapeManager:

    def __init__(self,
                 url: str = 'https://www.allrecipes.com',
                 page_limit: int = 100
                 ):
        self.base_url = url
        self._website_page_limit = page_limit
        self._context = make_context()
        self._recipe_link_dict = None
        self._meal_categories = None
        self._scraped_meal_info = None
        print('Initialized at', dt.now())

    @property
    def meal_categories(self):
        if self._meal_categories is None:
            self._meal_categories = self._get_meal_categories()
        return self._meal_categories

    @property
    def recipe_link_dict(self):
        if self._recipe_link_dict is None:
            self._recipe_link_dict = self._get_recipe_links()
        return self._recipe_link_dict

    @property
    def scraped_meal_info(self):
        if self._scraped_meal_info is None:
            self._scraped_meal_info = self._compile_recipe_info()
        return self._scraped_meal_info

    def _compile_recipe_info(self) -> MealCollection:
        meals_from_scrape = MealCollection()
        self._get_recipe_data(meals_from_scrape)
        return meals_from_scrape

    def dump_scrape_data_to_db(self, item_limit: int = 100) -> None:
        meals_from_scrape_batch = BatchMealCollection(item_limit=item_limit,write_to_db=True)
        self._get_recipe_data(meals_from_scrape_batch)
        meals_from_scrape_batch.dump_data_to_db()

    def _get_recipe_data(self, Meal_Col):
        for category, recipe_set in self.recipe_link_dict.items():
            # iterate through each recipe in the set
            for recipe in list(recipe_set):

                meal = self._format_data_as_meal(recipe, category)
                Meal_Col.add_meals_to_collection(meal)


    def _format_data_as_meal(self, recipe: str, cat: str) -> MealInfo:
        # Getting HTML for specific recipe page for scraping
        sp = get_html_for_soup(recipe, self._context)

        meal_name = self._get_recipe_name(sp)
        nutrition_data = self._get_nutrient_data_for_meal(sp)
        ingredient_data = self._get_cooking_ingredients(sp)
        instruction_dict = self._get_meal_instructions(sp)

        meal = MealInfo(url=recipe, 
                        category=cat,
                        name=meal_name,
                        ingredients=ingredient_data,
                        nutrition=nutrition_data,
                        instructions=instruction_dict)
        return meal

    def _get_meal_categories(self) -> dict:
        recipe_categories = {}
        soup = get_html_for_soup(self.base_url, self._context)
        tags = soup('a', class_='see-all-heading')
        if not tags:
            logger.critical(f'Unable to find any categories in {self.base_url}!')
            return recipe_categories

        for tag in tags:
            link = tag.get('href')
            cat = find_in_url(link)
            recipe_categories[cat] = link

        return recipe_categories

    def _get_recipe_links(self):
        recipe_links_by_cat = defaultdict(set)
        completed_parses = set()  # use a set to ensure we don't pick up duplicate recipes in different categories
        for cgy, lnk in self.meal_categories.items():
            page_num = 1
            valid_page = True

            while valid_page and page_num <= self._website_page_limit:
                page = '?page=' + str(page_num)
                try:
                    option_page = get_html_for_soup(lnk, self._context, page)
                except:
                    valid_page = False
                    logger.info(f'Reached last viable page for {cgy}')
                    continue

                tgs = option_page('a')
                for tg in tgs:

                    try:
                        class_logic = tg.get('class')[0]  # Class is needed, so skip if not there
                    except:
                        continue
                    try:
                        aria_logic = tg.get('aria-hidden')[0]  # Aria logic only needed in page one.
                    except:
                        aria_logic = 'NA'
                    if ((class_logic in 'card__titleLink manual-link-behavior' and aria_logic in 'true') 
                         or class_logic in 'tout__imageLink'):

                        raw_link = tg.get('href')

                        if '/recipe/' in raw_link:
                            corrected_link = prepend_root_to_url(raw_link, self.base_url)
                            rec_id = find_in_url(corrected_link, -2, False)
                            if rec_id not in completed_parses:
                                recipe_links_by_cat[cgy].add(corrected_link)
                                completed_parses.add(rec_id)
                                if rec_id == '9401':
                                    print('\n\n\nFOUND 9401\n\n\n')
                            else:
                                logger.info(f'{corrected_link} already exists')

                page_num += 1
            # print(len(list(recipe_links_by_cat[cgy])))
        return recipe_links_by_cat

    @staticmethod
    def _get_nutrient_data_for_meal(soup) -> dict:
        content = {}
        sect = get_website_chunk_by_class(soup,
                                          'section',
                                          'recipe-nutrition ng-dialog component nutrition-section container')
        # iterate through all 'div' sections that are a 'nutrient-row' class
        for div in sect.find_all('div', class_='nutrition-row'):
            # iterate through each nutrient NAME only
            for span in div.find_all('span', class_='nutrient-name'):
                # iterate through nutrient qty and %DV for nutrient
                try:
                    nutr_name = next(span.stripped_strings)
                    rm_colon_name = nutr_name.replace(':','')
                    nutrient_values = format_dict_from_soup(div, 'value')
                    content[rm_colon_name] = nutrient_values
                except:
                    print('couldnt parse', span)
                    continue
        return content

# TODO: refactor the find_all and for-loop into a separate function in web_assist
    @staticmethod
    def _get_cooking_ingredients(soup) -> list:
        item_list = []
        ingredients_table = get_website_chunk_by_class(soup,
                                                       'ul',
                                                       'ingredients-section')

        ing_components = ingredients_table.find_all('span', class_='ingredients-item-name')

        for item in ing_components:
            item_str = str(item.string)
            item_list.append(item_str)
        return item_list

    @staticmethod
    def _get_meal_instructions(soup) -> dict:
        item_dict = {}
        instructions_table = get_website_chunk_by_class(soup,
                                                        'ul',
                                                        'instructions-section')

        inst_components = instructions_table.find_all('p')

        for step, item in enumerate(inst_components):
            item_str = str(item.string)
            item_dict[step+1] = item_str
        return item_dict

    @staticmethod
    def _get_recipe_name(soup) -> str:
        title = get_website_chunk_by_class(soup,
                                           'h1',
                                           'headline heading-content')
        return title.string


if __name__ == '__main__':
    test_connect = MySqlManager(database='mealplanner_test')
    test_connect.rebuild_database()
    scr = RecipeWebScrapeManager(page_limit=1)
    scr.dump_scrape_data_to_db(item_limit=1)
