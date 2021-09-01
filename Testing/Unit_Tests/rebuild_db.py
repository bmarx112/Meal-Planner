import sys
sys.path.insert(0, r'C:\Users\bmarx\Coding Projects\Meal Planner')
from Web_Scraper.recipe_web_scrape_manager import RecipeWebScrapeManager
from Data_Management.MySQL.mysql_manager import MySqlManager

testing_query = '''SELECT COUNT(Meal.Meal_Category) as count
                   FROM Meal
                '''

# Rebuild the db and clear all the rows
test_connect = MySqlManager(database='mealplanner_test')
test_connect.rebuild_database()
test_connect.execute_query(testing_query)

row_initial = test_connect.cursor.fetchone()[0]

assert row_initial == 0

scr = RecipeWebScrapeManager(page_limit=1, choose_cats=True)
scr.dump_scrape_data_to_db(dump_limit=10, db=test_connect)
test_connect.execute_query(testing_query)

row_final = test_connect.cursor.fetchone()[0]

assert row_final > 0