from Objects.meal_collection import MealCollection
import mysql.connector
from mysql.connector.connection import MySQLConnection
from Queries.MySql_init import init_query
from Queries.MySql_insert import insert_meals, insert_ingredients, insert_instructions, insert_nutrition
from typing import Union
import logging

__author__ = 'bmarx'

logger = logging.getLogger(__name__)


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
            self.cursor.execute(init_query, multi=True)
            logger.info('Successfully built database!')
        except Exception as e:
            logger.critical(f'Unable to create database!\nError: {e}')

    # TODO: Create loops to capture data for each table
    def bulk_insert_to_db(self, data: list) -> None:
        

        self._bulk_insert_meals()
        self._bulk_insert_ingredients()
        self._bulk_insert_instructions()
        self._bulk_insert_nutrition()
        
        pass

    def _bulk_insert_meals(self, data) -> None:

        self.cursor.executemany(insert_meals)
        pass

    def _bulk_insert_ingredients(self) -> None:
        self.cursor.executemany(insert_ingredients)
        pass

    def _bulk_insert_nutrition(self) -> None:
        self.cursor.executemany(insert_nutrition)
        pass

    def _bulk_insert_instructions(self) -> None:
        self.cursor.executemany(insert_instructions)
        pass


if __name__ == '__main__':
    test_connect = MySqlManager()
    test_connect.rebuild_database()
    print('debug')