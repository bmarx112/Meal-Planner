from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import time
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
all_cats = tuple([i for i in ui_web_scraper.all_categories.keys()])
# TODO: Make app class 

def run_web_scraper(*args):    
    set_scrape_parameters()
    ui_sql_manager.rebuild_database()
    pbar.start()
    ptext['text'] = 'Capturing Recipe Data...'
        
    ui_web_scraper.dump_scrape_data_to_db(ui_sql_manager)
    ptext['text'] = 'Capture Complete.'
    pbar.stop()
    
def monitor_scrape_status(thread: Future):
    
    while thread.running():
        ptext['text'] = 'Capturing Recipe Data...'
        time.sleep(8)
    if thread.done():
        ptext['text'] = 'Capture Complete.'
    pbar.stop()

def select_categories_for_scrape():
    selected_cats = set(lbox.curselection())
    ui_web_scraper.set_categories_from_index_set(index_set=selected_cats)

def set_scrape_parameters():
    ui_web_scraper.website_page_limit = int(page_lmt.get())
    ui_web_scraper.dump_limit = int(chunk_size.get())
    select_categories_for_scrape()

# Intitialization
root = Tk()
root.option_add('*tearOff', FALSE)
root.title('Meal Planner Control')

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

# TODO: Add Progress bar/indicator for scrape process 
catlabel = ttk.Label(db_frame, text="Select Meal Categories:")
catlabel.grid(column=0, row=2, sticky=W)

pglable = ttk.Label(db_frame, text="Determine Num Web Pages to Parse:")
pglable.grid(column=0, row=0, sticky=W)

cklable = ttk.Label(db_frame, text="Determine Chunk Size for SQL Upload:")
cklable.grid(column=0, row=1, sticky=W)

pg_limit = ttk.Entry(db_frame, textvariable=page_lmt)
pg_limit.grid(column=1, row=0, sticky=W)

ck_size = ttk.Entry(db_frame, textvariable=chunk_size)
ck_size.grid(column=1, row=1, sticky=W)

lbox = Listbox(db_frame, listvariable=cat_list, selectmode='extended', height=15)
lbox.grid(column=0, row=3, rowspan=6, sticky=(N,S,E,W))

ptext = ttk.Label(db_frame, text='Data Capture Not Started.')
ptext.grid(column=3, row=0, sticky=W)
pbar = ttk.Progressbar(db_frame, orient=HORIZONTAL, length=100, mode='indeterminate')
pbar.grid(column=3, row=1, sticky=W)

generate_data = ttk.Button(db_frame, text="Get Recipes", command=run_web_scraper)
generate_data.grid(column=0, row=10)

generate_data.bind("<Return>", run_web_scraper)

root.mainloop()