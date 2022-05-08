from tkinter import *
from tkinter import ttk

import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Data_Management.MySQL.Queries.MySql_model_input import recipes_in_database
from Data_Management.MySQL.mysql_manager import MySqlManager
from Web_Scraper.recipe_web_scrape_manager import RecipeWebScrapeManager

ui_web_scraper = RecipeWebScrapeManager()
ui_sql_manager = MySqlManager()

count_df = ui_sql_manager.read_to_dataframe(query=recipes_in_database())
recipe_num = count_df['count'].values[0]
all_cats = tuple([i for i in ui_web_scraper.all_categories.keys()])


def update_web_scraper(*args):
    ui_web_scraper.base_url = url.get()
    ui_web_scraper.website_page_limit = int(page_lmt.get())
    ui_web_scraper.dump_limit = int(chunk_size.get())

def select_categories_for_scrape():
    selected_cats = set(lbox.curselection())
    ui_web_scraper.set_categories_from_index_set(index_set=selected_cats)
    print(ui_web_scraper.meal_categories)

# Intitialization
root = Tk()
root.option_add('*tearOff', FALSE)
root.title("Meal Planner Control")

# Define tkinter variables
feet = StringVar(value=100)
meters = StringVar()
url = StringVar(value='https://www.allrecipes.com')
page_lmt = StringVar(value=100)
chunk_size = StringVar(value=150)
cat_list = StringVar(value=all_cats)

# Create tabbed menu
tab_control = ttk.Notebook(root)
data_mgmt = ttk.Frame(tab_control)
tab_control.add(data_mgmt, text='Data Management')
model = ttk.Frame(tab_control)
tab_control.add(model, text='Meal Planning')
tab_control.pack(expand=1, fill='both')

# Data Mgmt Tab Config
db_frame = ttk.Frame(data_mgmt, padding="3 3 12 12")
db_frame.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

lblabel = ttk.Label(db_frame, text="Select Meal Categories:")
lblabel.grid(column=0, row=0, sticky=W)

lbox = Listbox(db_frame, listvariable=cat_list, selectmode='extended', height=15)
lbox.grid(column=0, row=1, rowspan=6, sticky=(N,S,E,W))

cat_entry = ttk.Button(db_frame, text="Use Selected Categories", command=select_categories_for_scrape)
cat_entry.grid(column=0, row=8)

rec = ttk.Label(db_frame, text=recipe_num)
rec.grid(column=2, row=3)

cat_entry.bind("<Return>", select_categories_for_scrape)

root.mainloop()