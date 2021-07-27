from collections import defaultdict
from Utilities.web_assist import (prepend_root_to_url, make_context, get_html_for_soup, find_in_url, 
            get_website_chunk_by_class, format_dict_from_soup)
from datetime import datetime as dt
from Objects.meal_info import MealInfo


class RecipeWebScrapeManager:

    def __init__(self,
                 url: str = 'https://www.allrecipes.com',
                 page_limit: int = 100):
        self.base_url = url
        self._website_page_limit = page_limit
        self._context = make_context()
        self._meal_categories = None
        self._recipe_link_dict = None
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
        meals = []
        for category, recipe_set in self.recipe_link_dict.items():
            # iterate through each recipe in the set
            for recipe in list(recipe_set):
                print(recipe)
                meal_name = self._get_recipe_name(recipe)
                nutrition_data = self._get_nutrient_data_for_meal(recipe)
                ingredient_data = self._get_cooking_ingredients(recipe)
                instruction_dict = self._get_meal_instructions(recipe)
                meal = MealInfo(url=recipe, 
                                 category=category,
                                 name=meal_name,
                                 ingredients=ingredient_data,
                                 nutrition=nutrition_data,
                                 instructions=instruction_dict)
                meals.append(meal)
        return meals


    def _get_nutrient_data_for_meal(self, recipe_link: str) -> dict:
        content = {}
        sect = get_website_chunk_by_class(recipe_link, 
                                          self._context, 
                                          'section', 
                                          'recipe-nutrition ng-dialog component nutrition-section container')
        # iterate through all 'div' sections that are a 'nutrient-row' class
        for div in sect.find_all('div', class_='nutrition-row'):
            # iterate through each nutrient NAME only
            for span in div.find_all('span', class_='nutrient-name'):
                #iterate through nutrient qty and %DV for nutrient
                try:
                    nutrient_values = format_dict_from_soup(div, 'value')
                    content[next(span.stripped_strings)] = nutrient_values
                except:
                    print('couldnt parse %s' % recipe_link)
                    continue
        return content

# TODO: refactor the find_all and for-loop into a separate function in web_assist
    def _get_cooking_ingredients(self, recipe_link: str) -> list:
        item_list = []
        ingredients_table = get_website_chunk_by_class(recipe_link, 
                                                       self._context, 
                                                       'ul', 
                                                       'ingredients-section')

        ing_components = ingredients_table.find_all('span', class_='ingredients-item-name')

        for item in ing_components:
            item_list.append(item.string)
        return item_list


    def _get_meal_instructions(self, recipe_link: str) -> dict:
        item_dict = {}
        instructions_table = get_website_chunk_by_class(recipe_link, 
                                                        self._context, 
                                                        'ul', 
                                                        'instructions-section')

        inst_components = instructions_table.find_all('p')

        for step, item in enumerate(inst_components):
            item_dict[step+1] = item.string
        return item_dict


    def _get_recipe_name(self, recipe_link: str) -> str:
        title = get_website_chunk_by_class(recipe_link,
                                            self._context,
                                            'h1',
                                            'headline heading-content')
        return title.string


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


    #TODO: Remove duplicate recipes that exist in multiple categories. Allow first occurence to remain.
    def _get_recipe_links(self):
        recipe_links_by_cat = defaultdict(set)

        for cgy, lnk in self.meal_categories.items():
            page_num = 1
            valid_page = True

            while valid_page and page_num <= self._website_page_limit:
                page = '?page=' + str(page_num)
                try:
                    option_page = get_html_for_soup(lnk, self._context, page)
                    # print(lnk + page)
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
    scr = RecipeWebScrapeManager(page_limit=1)
    the_list = scr.scraped_meal_info
    print(the_list)
    ''' with open('recipeURLs.csv', 'r') as file:
    csv_reader = csv.reader(file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            continue
        else:
            test_dict[row[0]] = row[1] '''