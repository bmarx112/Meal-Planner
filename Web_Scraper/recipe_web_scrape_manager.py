from concurrent.futures.thread import ThreadPoolExecutor
import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from collections import defaultdict
from Utilities.web_assist import (prepend_root_to_url, make_context, get_soup_from_html, find_in_url,
                                  get_website_chunk_by_class, format_dict_from_soup)
from Utilities.helper_functions import timeit
from datetime import datetime as dt
from typing import Union
from Objects.meal_info import MealInfo
from Objects.meal_collection import MealCollection
from Data_Management.MySQL.mysql_manager import MySqlManager
import logging
import re
import concurrent.futures
import queue
import threading

__author__ = 'bmarx'

logger = logging.getLogger(__name__)


class RecipeWebScrapeManager:

    def __init__(self,
                 url: str = 'https://www.allrecipes.com',
                 page_limit: int = 100,
                 choose_cats: bool = False,
                 dump_limit: int = 150
                 ):
        self.base_url = url
        self._website_page_limit = page_limit
        self._context = make_context()
        self._recipe_link_dict = None
        self._meal_categories = None
        self._scraped_meal_info = None
        self._choose_cats = choose_cats
        self._pipeline = queue.Queue(maxsize=dump_limit)
        self._scanned_sites = 0
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

    @timeit
    def dump_scrape_data_to_db(self, db: MySqlManager, dump_limit: int = 100) -> None:
        meals_from_scrape = self._upload_to_mysql(db, dump_limit)
        if len(meals_from_scrape.collection) > 0:
            meals_from_scrape.dump_data_to_db()

    def _upload_to_mysql(self, db: MySqlManager, dump_limit: Union[None, int] = 100):
        meal_col = MealCollection(item_limit=dump_limit, db=db)
        for category, recipe_set in self.recipe_link_dict.items():
            # iterate through each recipe in the set
            recipe_list = list(recipe_set)
            num_rcps = len(recipe_list)
            self._scanned_sites = 0
            with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:

                executor.submit(self._format_meal_from_soup, category, meal_col, num_rcps)
                executor.map(self._add_meal_to_queue, recipe_list)

        return meal_col

    def _add_meal_to_queue(self, recipe: str):
        # Getting HTML for specific recipe page for scraping
        ctx = make_context()
        try:
            sp = get_soup_from_html(recipe, ctx, timeout=20)
        except:
            self._scanned_sites += 1
            print('warning')
        self._pipeline.put((recipe, sp))

    def _format_meal_from_soup(self, cat: str, meal_col: MealCollection, rec_lng: int):
        while rec_lng > self._scanned_sites:
            try:
                recipe, sp = self._pipeline.get(timeout=1)
                self._scanned_sites += 1
                print(recipe)
            except:
               print(rec_lng, self._scanned_sites)
               continue
            try:
                meal_name = self._get_recipe_name(sp)
                nutrition_data = self._get_nutrient_data_for_meal(sp)
                ingredient_data = self._get_cooking_ingredients(sp)
                instruction_dict = self._get_meal_instructions(sp)
                scope_dict = self._get_recipe_scope(sp)
                meal_rating = self._get_recipe_rating(sp)
                rt_count = self._get_recipe_rating_count(sp)

                meal = MealInfo(url=recipe,
                                category=cat,
                                name=meal_name,
                                ingredients=ingredient_data,
                                nutrition=nutrition_data,
                                instructions=instruction_dict,
                                scope=scope_dict,
                                rating=meal_rating,
                                rt_count=rt_count)

                meal_col.add_meals_to_collection(meal)
            except Exception as e:
                logger.critical(f'FAILURE TO CAPTURE {recipe}\nError: {e}')
                continue

    def _get_meal_categories(self) -> dict:
        recipe_categories = {}
        soup = get_soup_from_html(self.base_url, self._context)
        tags = soup('a', class_='see-all-heading')
        if not tags:
            logger.critical(f'Unable to find any categories in {self.base_url}!')
            return recipe_categories

        for tag in tags:
            link = tag.get('href')
            cat = find_in_url(link)
            if self._choose_cats:
                add = input(f'Include recipes in: {cat}? Y/N')
                if add.lower() == 'y':
                    recipe_categories[cat] = link
            else:
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
                    option_page = get_soup_from_html(lnk, self._context, page)
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

                        if '/recipe/' in raw_link: # We only want links to recipes, not blogs or ads, etc
                            corrected_link = prepend_root_to_url(raw_link, self.base_url)
                            rec_id = find_in_url(corrected_link, -2, False)
                            if rec_id not in completed_parses: #Sometimes one recipe exists in multiple categories! Only keep the first occurence.
                                recipe_links_by_cat[cgy].add(corrected_link)
                                completed_parses.add(rec_id)
                            else:
                                logger.info(f'{corrected_link} already exists')
                print(f'{cgy}: {len(list(recipe_links_by_cat[cgy]))} so far!') #Just a sanity check.
                page_num += 1 # 'turning' the page
        return recipe_links_by_cat

    # TODO: Some recipes dont have a pop-up window for the nutrition facts and are being skipped. find a way to capture that different structure of HTML.
    @staticmethod
    def _get_nutrient_data_for_meal(soup) -> dict:
        content = {}
        sect = get_website_chunk_by_class(soup,
                                          'section',
                                          'recipe-nutrition ng-dialog component nutrition-section container')
        cal_sect = get_website_chunk_by_class(sect,
                                              'span',
                                              'semi-bold')
        # TODO: Change this quick and dirty method of grabbing calories into something more sustainable
        cal_name = cal_sect.next.replace(':', '')
        cal_vals = [cal_sect.nextSibling.replace(' ', ''), '']
        cal_load = {'nutrient-value': cal_vals}
        content[cal_name] = cal_load
        # iterate through all 'div' sections that are a 'nutrient-row' class
        for div in sect.find_all('div', class_='nutrition-row'):
            # iterate through each nutrient NAME only
            for span in div.find_all('span', class_='nutrient-name'):
                # iterate through nutrient qty and %DV for nutrient
                try:
                    # Get nutrient name
                    nutr_name = next(span.stripped_strings)
                    rm_colon_name = nutr_name.replace(':', '')
                    # Get Nutrient Data
                    nutrient_values = format_dict_from_soup(div, 'value')
                    content[rm_colon_name] = nutrient_values
                except:
                    print(f"couldn't parse {span}")
                    continue
        return content

    @staticmethod
    def _get_cooking_ingredients(soup) -> list[dict]:
        item_list = []
        ingredients_table = get_website_chunk_by_class(soup,
                                                       'ul',
                                                       'ingredients-section')

        #ing_components = ingredients_table.find_all('span', class_='ingredients-item-name')
        ing_components = ingredients_table.find_all('input')


        for item in ing_components:

            try:
                amt = item['data-init-quantity']
            except:
                amt = .01
            
            try:
                name = item['data-ingredient']
            except:
                continue

            info_dict = {
                'quantity': amt,
                'ingredient': name
            }

            item_list.append(info_dict)
        return item_list

    # TODO: Instruction steps that contain links are not populating. they appear as 'None.' Find out why!
    @staticmethod
    def _get_meal_instructions(soup) -> dict:
        item_dict = {}
        instructions_table = get_website_chunk_by_class(soup,
                                                        'ul',
                                                        'instructions-section')

        inst_components = instructions_table.find_all('p')

        for step, item in enumerate(inst_components):
            item_str = str(item.string)
            item_dict[step + 1] = item_str
        return item_dict

    @staticmethod
    def _get_recipe_name(soup) -> str:
        title = get_website_chunk_by_class(soup,
                                           'h1',
                                           'headline heading-content elementFont__display')
        return title.string

    @staticmethod
    def _get_recipe_scope(soup) -> dict:
        scope_table = get_website_chunk_by_class(soup, 
                                                 'div', 
                                                 'component breadcrumbs')

        full_tp_list = list(enumerate(scope_table.stripped_strings))
        scope_tp_list = full_tp_list[:-1]  # the final element is the recipe name itself, which will obviously be unique
        return dict(scope_tp_list)

    @staticmethod
    def _get_recipe_rating(soup) -> float:
        rating_section = get_website_chunk_by_class(soup, 
                                                 'span', 
                                                 'review-star-text')

        try:
            rating_string = rating_section.text
            rating_number = re.findall(r'[0-9\.]+', rating_string)  
            rating_float = float(rating_number[0])
        except:
            rating_float = 0.0
        return rating_float

    @staticmethod
    def _get_recipe_rating_count(soup) -> int:
        rt_count_section = get_website_chunk_by_class(soup, 
                                                 'span', 
                                                 'ugc-ratings-item')
        try:
            count_string = rt_count_section.text
            count_number = re.findall(r'[0-9,]+', count_string)
            count_stripped = count_number[0].replace(',','')
            count_int = int(count_stripped)
        except:
            count_int = 0
        return count_int

if __name__ == '__main__':
    test_connect = MySqlManager(database='mealplanner')
    test_connect.rebuild_database()
    scr = RecipeWebScrapeManager(page_limit=2, choose_cats=True)
    scr.dump_scrape_data_to_db(dump_limit=10, db=test_connect)
    # df = test_connect.read_to_dataframe(pull_meals)
    