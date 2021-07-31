'''
Queries used in MySQLManager
'''


insert_meals = '''INSERT INTO Meal (Recipe_Id,
                                    Meal_Name,
                                    Meal_URL)
                                VALUES ( %d,%s,%s)
'''

insert_ingredients = '''INSERT INTO Ingredients (Recipe_Id,
                                                 Ingredient_Name)
                                            VALUES ( %d,%s)
'''

insert_instructions = '''INSERT INTO Instructions (Recipe_Id,
                                                   Step_Sequence,
                                                   Instruction)
                                                VALUES ( %d,%d,%s)
'''

insert_nutrition = '''INSERT INTO Nutrition (Recipe_Id,
                                             Element,
                                             Quantity,
                                             Unit,
                                             Daily_Val)
                                        VALUES ( %d,%s,%d,%s,%d)
'''