from Utilities.web_assist import find_in_url

class MealInfo:

    def __init__(self,
                 url: str,
                 category: str,
                 name: str,
                 ingredients: list,
                 nutrition: dict,
                 instructions: dict,
                 scope: dict,
                 rating: float,
                 rt_count: int):
        self.url = str(url)
        self.recipe_id = int(find_in_url(self.url, -2, False))
        self.category = category
        self.meal_name = str(name)
        self.ingredient_dict_list = ingredients
        self.nutrition_facts = nutrition
        self.cooking_instructions = instructions
        self.recipe_scope = scope
        self.rating = rating
        self.rt_count = rt_count
        self._meal_dict = None

    @property
    def meal_info_as_dict(self):
        if self._meal_dict is None:
            self._meal_dict = self._compile_meal_dict()
        return self._meal_dict

    def _compile_meal_dict(self):
        comp = {key: value for key, value in self.__dict__.items() if not key.startswith('_') and not callable(key)}
        return comp

    def __repr__(self):
        return f'{self.recipe_id}: {self.meal_name}'
