from Objects.meal_info import MealInfo
from typing import List, Union


class MealCollection:

    def __init__(self,
                 meal_list: Union[None, List[MealInfo]] = None):
        self.collection = meal_list or []

    def add_meals_to_collection(self, addition: Union[MealInfo, List[MealInfo]]):
        # accepts lists and single values. need to use different methods for either case
        if isinstance(addition, list):
            self.collection.extend(addition)
        else:
            self.collection.append(addition)

    def __repr__(self):
        return f'Collection of {len(self.collection)} Meals'
