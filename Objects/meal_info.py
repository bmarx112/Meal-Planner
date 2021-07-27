from typing import Union

class MealInfo():

    def __init__(self,
                 url: str,
                 category: str,
                 name: str,
                 ingredients: list,
                 nutrition: dict,
                 instructions: dict):
        self.url = url
        self.category = category
        self.meal_name = name
        self.ingredient_list = ingredients
        self.nutrition_facts = nutrition
        self.cooking_instructions = instructions