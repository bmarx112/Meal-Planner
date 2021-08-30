from Web_Scraper.recipe_web_scrape_manager import RecipeWebScrapeManager
from Data_Management.MySQL.mysql_manager import MySqlManager

test_connect = MySqlManager(database='mealplanner_test')
test_connect.rebuild_database()
scr = RecipeWebScrapeManager(page_limit=1)
scr.dump_scrape_data_to_db(dump_limit=1, db=test_connect)