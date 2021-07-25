from Utilities.web_assist import make_context, get_html_for_soup, find_in_url
from datetime import datetime as dt


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
    [print(i) for i, _ in scr.meal_categories.items()]