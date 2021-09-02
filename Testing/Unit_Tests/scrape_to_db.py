import sys
sys.path.insert(0, r'C:\Users\bmarx\Coding Projects\Meal Planner')
from Web_Scraper.recipe_web_scrape_manager import RecipeWebScrapeManager
from Data_Management.MySQL.mysql_manager import MySqlManager

test_connect = MySqlManager(database='mealplanner')
test_connect.rebuild_database()
scr = RecipeWebScrapeManager(page_limit=1, choose_cats=True)
scr.dump_scrape_data_to_db(dump_limit=10, db=test_connect)