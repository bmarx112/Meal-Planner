from collections import defaultdict
import csv

dict_temp = defaultdict(set)
with open('C:\\Users\\bmarx\Coding Projects\\Meal Planner\\recipeURLs.csv') as f:
   for line in csv.DictReader(f, fieldnames=('category', 'url')):
      dict[line['category']].add(line['url'])
    
