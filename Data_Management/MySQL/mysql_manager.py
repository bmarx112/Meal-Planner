import mysql.connector
from mysql.connector.connection import MySQLConnection
from Data_Management.MySQL.Queries.MySql_init import init_query
from Data_Management.MySQL.Queries.MySql_insert import (insert_meals, insert_ingredients, 
                                                        insert_instructions, insert_nutrition)
from typing import Union
import logging
import datetime as dt

__author__ = 'bmarx'

logger = logging.getLogger(__name__)

# TODO: Consider adding meal category as a field in Meals table?
class MySqlManager:

    def __init__(self,
                 user: Union[str, None] = 'root',
                 password: str = None,
                 host: str = '127.0.0.1',
                 database: str = 'MealPlanner') -> None:
        self.username = user
        self._password = password
        self.host = host
        self.database = database
        self._mysql_connection = None
        self._cursor = None
    
    @property
    def mysql_connection(self) -> MySQLConnection:
        if self._mysql_connection is None:
            sql_args = {'host': self.host, 
                        'user': self.username, 
                        'database': self.database, 
                        'password': self._password}
            try:
                self._mysql_connection = mysql.connector.connect(**sql_args)
                logger.info('Successfully made connection!')
            except Exception as e:
                logger.critical(f'Unable to create connection!\nError: {e}')
        return self._mysql_connection
    
    @property
    def cursor(self):
        if self._cursor is None:
            self._cursor = self.mysql_connection.cursor()
        return self._cursor
    
    def rebuild_database(self) -> None:
        try:
            # self.cursor.execute(destroy_db_query, multi=True)
            self.cursor.execute(init_query, multi=True)
            logger.info('Successfully built database!')
        except Exception as e:
            logger.critical(f'Unable to create database!\nError: {e}')

    def bulk_insert_into_db(self, data: list[dict]) -> None:
        timestamp = dt.datetime.now()
        # Data: List of dicts
        try:
            self._bulk_insert_meals(data, timestamp)
        except Exception as e:
            print('first method failed\n',e)
        try:
            self._bulk_insert_ingredients(data, timestamp)
            self._bulk_insert_instructions(data, timestamp)
            self._bulk_insert_nutrition(data, timestamp)
            self.mysql_connection.commit()
            logger.warning(f'successfully uploaded {len(data)} items.') # TODO: make this info again after testing
        except Exception as e:
            logger.critical(f'Unable to load data!\nError: {e}')

    def _bulk_insert_meals(self, data, time: dt.datetime) -> None:
        injection = []
        for meal in data:
            mealdata = (
                        meal['recipe_id'],
                        meal['meal_name'],
                        meal['url'],
                        time
                        )
            injection.append(mealdata)

        self.cursor.executemany(insert_meals, injection)
        

    def _bulk_insert_ingredients(self, data, time: dt.datetime) -> None:
        injection = []
        for ing in data:
            for element in ing['ingredient_list']:
                mealdata = (
                            ing['recipe_id'],
                            element,
                            time
                            )
                injection.append(mealdata)
        self.cursor.executemany(insert_ingredients, injection)

    def _bulk_insert_nutrition(self, data, time: dt.datetime) -> None:
        injection = []
        for nut in data:
            for name, value in nut['nutrition_facts'].items():
                # dict of dict of list
                quantity =  float(value['nutrient-value'][0])
                mealdata = (
                            nut['recipe_id'],
                            name,
                            quantity,
                            value['nutrient-value'][1],
                            time
                            )
                injection.append(mealdata)
        self.cursor.executemany(insert_nutrition, injection)

    def _bulk_insert_instructions(self, data, time: dt.datetime) -> None:
        injection = []
        for inst in data:
            for num, step in inst['cooking_instructions'].items():
                int_num = int(num)
                mealdata = (
                            inst['recipe_id'],
                            int_num,
                            step,
                            time
                            )
                injection.append(mealdata)

        self.cursor.executemany(insert_instructions, injection)


if __name__ == '__main__':
    test_connect = MySqlManager()
    test_connect.rebuild_database()
    print('debug')