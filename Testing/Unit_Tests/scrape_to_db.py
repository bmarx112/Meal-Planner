import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from Web_Scraper.recipe_web_scrape_manager import RecipeWebScrapeManager
from Data_Management.MySQL.mysql_manager import MySqlManager

test_connect = MySqlManager(database='mealplanner')
test_connect.rebuild_database()
scr = RecipeWebScrapeManager(page_limit=10, choose_cats=True)
scr.dump_scrape_data_to_db(dump_limit=100, db=test_connect)