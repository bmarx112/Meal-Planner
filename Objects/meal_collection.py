from Data_Management.MySQL.mysql_manager import MySqlManager
from typing import Union, List
from Objects.meal_info import MealInfo
from Data_Management.CSV.data_export import csv_path
import logging

__author__ = 'bmarx'

logger = logging.getLogger(__name__)


class MealCollection:

    def __init__(self,
                 db: MySqlManager,
                 item_limit: int = None,
                 meal_list: Union[None, List[MealInfo]] = None
                 ):
        self.class_capacity = item_limit or 100000000  # arbitrarily high limit
        self.collection = meal_list or []
        self.sql_mgr = db

    def add_meals_to_collection(self, addition: Union[MealInfo, List[MealInfo]]):
        # accepts lists and single values. need to use different methods for either case
        if isinstance(addition, list):
            self.collection.extend(addition)
        else:
            self.collection.append(addition)

        if len(self.collection) >= self.class_capacity:

            self.dump_data_to_db()

    def dump_data_to_db(self):

        db_data = self.format_mealcollection_as_list()
        self.sql_mgr.bulk_insert_into_db(db_data)
        logger.info(f'Dumped contents to {self.sql_mgr.database}')
        self.collection = []

    def format_mealcollection_as_list(self):
        formatted_data = []

        for meal in self.collection:
            data = meal.meal_info_as_dict
            formatted_data.append(data)
        
        return formatted_data

    def __repr__(self):
        return f'Collection of {len(self.collection)} Meals'
