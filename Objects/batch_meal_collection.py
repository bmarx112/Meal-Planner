from genericpath import isfile
from Objects.meal_collection import MealCollection
from Data_Management.MySQL.mysql_manager import MySqlManager
from typing import Union, List
from Objects.meal_info import MealInfo
from collections import defaultdict
import pandas as pd
from Data_Management.CSV.data_export import csv_path
import logging

__author__ = 'bmarx'

logger = logging.getLogger(__name__)


class BatchMealCollection(MealCollection):

    def __init__(self,
                 meal_list: Union[None, List[MealInfo]] = None,
                 item_limit: int = 100,
                 write_to_file: bool = False,
                 write_to_db: bool = False,
                 path: str = csv_path):
        super().__init__(meal_list)
        self.class_capacity = item_limit
        self.path = path
        self.is_file = False
        self._to_file = write_to_file
        self._to_db = write_to_db

        if self._to_db:
            self.sql_mgr = MySqlManager()

    def add_meals_to_collection(self, addition: Union[MealInfo, List[MealInfo]]):
        # accepts lists and single values. need to use different methods for either case
        if isinstance(addition, list):
            self.collection.extend(addition)
        else:
            self.collection.append(addition)
        
        if len(self.collection) == self.class_capacity:

            if self._to_file:
                self.dump_data_to_file()
                logger.info(f'Dumped contents to {self.path}')

            if self._to_db:
                self.dump_data_to_db()
                logger.info(f'Dumped contents to {self.sql_mgr.database}')

            self.collection = []
            print('Emptied!')
            


    def dump_data_to_file(self):
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

    # TODO: build this method out and format data in an ingestible way for sqlmanager
    def dump_data_to_db(self):

        db_data = self.format_mealcollection_as_list()
        self.sql_mgr.bulk_insert_into_db(db_data)
