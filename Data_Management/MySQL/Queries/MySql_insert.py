
insert_meals = '''INSERT INTO Meal (Recipe_Id,
                                    Meal_Name,
                                    Meal_Category,
                                    Meal_URL,
                                    Meal_Rating,
                                    Num_Ratings)
                                VALUES ( %s,%s,%s,%s,%s,%s)
'''

insert_ingredients = '''INSERT INTO Ingredients (Recipe_Id,
                                                 Ingredient_Name)
                                            VALUES ( %s,%s)
'''

insert_instructions = '''INSERT INTO Instructions (Recipe_Id,
                                                   Step_Sequence,
                                                   Instruction)
                                                VALUES ( %s,%s,%s)
'''

insert_nutrition = '''INSERT INTO Nutrition (Recipe_Id,
                                             Element,
                                             Quantity,
                                             Unit)
                                        VALUES ( %s,%s,%s,%s)
'''

insert_mealscope = '''INSERT INTO MealScope (Recipe_Id,
                                             Levelno,
                                             Level_Desc)
                                                VALUES ( %s,%s,%s)
'''