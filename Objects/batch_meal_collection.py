from genericpath import isfile
from Objects.meal_collection import MealCollection
from typing import Union, List
from Objects.meal_info import MealInfo
from collections import defaultdict
import pandas as pd
from Data_Management.data_export import csv_path
import logging

__author__ = 'bmarx'

logger = logging.getLogger(__name__)


class BatchMealCollection(MealCollection):

    def __init__(self,
                 meal_list: Union[None, List[MealInfo]] = None,
                 item_limit: int = 100,
                 path: str = csv_path):
        super().__init__(meal_list)
        self.class_capacity = item_limit
        self.path = path
        self.is_file = False

    def add_meals_to_collection(self, addition: Union[MealInfo, List[MealInfo]]):
        # accepts lists and single values. need to use different methods for either case
        if isinstance(addition, list):
            self.collection.extend(addition)
        else:
            self.collection.append(addition)
        
        if len(self.collection) == self.class_capacity:
            self.dump_data_to_file()
            self.collection = []
            print('Dumped!')
            logger.info(f'Dumped contents to {self.path}')


    def dump_data_to_file(self) -> pd.DataFrame:
        structure = defaultdict(list)

        for meal in self.collection:
            data = meal.meal_info_as_dict

            for cat, val in data.items():
                structure[cat].append(val)

        frame = pd.DataFrame(structure)

        if not self.is_file:
            frame.to_csv(self.path, mode='a', index=False)
            self.is_file = True
        else:
            frame.to_csv(self.path, mode='a', index=False, header=False)