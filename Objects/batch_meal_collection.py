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

'''
Version of MealCollection that dumps its contents to a database once a certain
amount of items have been added. Purpose is to avoid using all the RAM 
when a lot of data is being scraped.
'''

class BatchMealCollection(MealCollection):

    def __init__(self,
                 meal_list: Union[None, List[MealInfo]] = None,
                 item_limit: int = 100,
                 write_to_db: bool = False):
        super().__init__(meal_list)
        self.class_capacity = item_limit
        self.is_file = False
        self._to_db = write_to_db
        # TODO: pass db credentials to manager here, or refactor.
        if self._to_db:
            self.sql_mgr = MySqlManager()

    def add_meals_to_collection(self, addition: Union[MealInfo, List[MealInfo]]):
        # accepts lists and single values. need to use different methods for either case
        if isinstance(addition, list):
            self.collection.extend(addition)
        else:
            self.collection.append(addition)
        
        if len(self.collection) >= self.class_capacity:

            self.dump_data_to_db()
            logger.info(f'Dumped contents to {self.sql_mgr.database}')

            self.collection = []
            
    def dump_data_to_db(self):

        db_data = self.format_mealcollection_as_list()
        self.sql_mgr.bulk_insert_into_db(db_data)
