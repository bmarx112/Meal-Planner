from Web_Scraper.recipe_web_scrape_manager import RecipeWebScrapeManager
from Data_Management.MySQL.mysql_manager import MySqlManager

testing_query = '''SELECT COUNT(Meal.Meal_Category) as count
                   FROM Meal
                '''
test_connect = MySqlManager(database='mealplanner_test')
scr = RecipeWebScrapeManager(page_limit=1)
scr.dump_scrape_data_to_db(dump_limit=1, db=test_connect)
test_connect.execute_query(testing_query)

rows = test_connect.cursor.fetchone()
print(rows)