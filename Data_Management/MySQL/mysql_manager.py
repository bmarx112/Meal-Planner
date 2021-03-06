import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from typing import List
import pandas as pd
import mysql.connector
from mysql.connector.connection import MySQLConnection
from Data_Management.MySQL.Queries.MySql_init import init_query
from Data_Management.MySQL.Queries.MySql_insert import (insert_meals, insert_ingredients, 
                                                        insert_instructions, insert_nutrition, insert_mealscope)
import logging
from Data_Management.MySQL.Queries.MySql_model_input import model_nutrition_query_with_doubled


__author__ = 'bmarx'

logger = logging.getLogger(__name__)


class MySqlManager:

    def __init__(self,
                 user: str = 'root',
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

    def execute_query(self, query: str, payload: List = None, commit: bool = False) -> None:
        try:
            if payload:
                self.cursor.executemany(query, payload)
            else:
                self.cursor.execute(query)

            if commit:
                self.mysql_connection.commit()

            logger.info('Query executed successfully.')
        except Exception as e:
            logger.critical(f'Unable to execute query! \nError: {e}\nPayload: {payload}')

    def read_to_dataframe(self, query: str) -> pd.DataFrame:
        sql_query_df = pd.read_sql(query, self.mysql_connection)
        return sql_query_df

    def rebuild_database(self) -> None:
        try:
            for i in init_query:
                self.execute_query(i, commit=True)
        except Exception as e:
            logger.critical(f'Unable to create database!\nError: {e}')

    def bulk_insert_into_db(self, data: list[dict]) -> None:
        # Data: List of dicts
        try:
            self._bulk_insert_meals(data)
            self._bulk_insert_ingredients(data)
            self._bulk_insert_instructions(data)
            self._bulk_insert_nutrition(data)
            self._bulk_insert_mealscope(data)
            self.mysql_connection.commit()

            logger.info(f'successfully uploaded {len(data)} items.') 
        except Exception as e:
            if str(e).startswith('1062'):
                logger.critical('Duplicate key error. Will not be loaded.')
            else:
                logger.critical(f'Unable to load data!\nError: {e}')

    def _bulk_insert_meals(self, data) -> None:
        injection = []
        for meal in data:
            mealdata = (
                        meal['recipe_id'],
                        meal['meal_name'],
                        meal['category'],
                        meal['url'],
                        meal['rating'],
                        meal['rt_count']
                        )
            injection.append(mealdata)
        self.execute_query(insert_meals, injection)
        
    def _bulk_insert_ingredients(self, data) -> None:
        injection = []
        for ing in data:
            for element in ing['ingredient_dict_list']:
                mealdata = (
                            ing['recipe_id'],
                            element['ingredient'],
                            element['quantity'],
                            element['unit']
                            )
                injection.append(mealdata)
        self.execute_query(insert_ingredients, injection)

    def _bulk_insert_nutrition(self, data) -> None:
        injection = []
        for nut in data:
            for name, value in nut['nutrition_facts'].items():
                # dict of dict of list
                quantity = float(value['nutrient-value'][0])
                mealdata = (
                            nut['recipe_id'],
                            name,
                            quantity,
                            value['nutrient-value'][1]
                            )
                injection.append(mealdata)
        self.execute_query(insert_nutrition, injection)

    def _bulk_insert_instructions(self, data) -> None:
        injection = []
        for inst in data:
            for num, step in inst['cooking_instructions'].items():
                int_num = int(num)
                mealdata = (
                            inst['recipe_id'],
                            int_num,
                            step
                            )
                injection.append(mealdata)

        self.execute_query(insert_instructions, injection)

    def _bulk_insert_mealscope(self, data) -> None:
        injection = []
        for scope in data:
            for lvl, scp in scope['recipe_scope'].items():
                mealdata = (
                            scope['recipe_id'],
                            lvl,
                            scp
                            )
                injection.append(mealdata)
        
        self.execute_query(insert_mealscope, injection)



if __name__ == '__main__':
    test_connect = MySqlManager()
    ls = ['Calories', 'carbohydrates', 'fat', 'saturated fat', 'protein', 'sugar', 'calcium', 'dietary fiber', 'vitamin a iu', 'vitamin c', 'vitamin b6', 'sodium', 'folate', 'cholesterol', 'niacin equivalents']
    df_output = test_connect.read_to_dataframe(query=model_nutrition_query_with_doubled(ls))
    print(df_output)
