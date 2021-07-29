from collections import defaultdict
from Objects.meal_info import MealInfo
from typing import List, Union
import logging

__author__ = 'bmarx'

logger = logging.getLogger(__name__)

class MealCollection:

    def __init__(self,
                 meal_list: Union[None, List[MealInfo]] = None):
        self.collection = meal_list or []
        self._frame = None

    @property
    def frame(self):
        if self._frame is None:
            self._frame = self.export_as_dataframe()
        return self._frame

    def add_meals_to_collection(self, addition: Union[MealInfo, List[MealInfo]]):
        # accepts lists and single values. need to use different methods for either case
        if isinstance(addition, list):
            self.collection.extend(addition)
        else:
            self.collection.append(addition)

    def __repr__(self):
        return f'Collection of {len(self.collection)} Meals'
