
insert_meals = '''INSERT INTO Meal (Recipe_Id,
                                    Meal_Name,
                                    Meal_URL,
                                    date_uploaded)
                                VALUES ( %s,%s,%s,%s)
'''

insert_ingredients = '''INSERT INTO Ingredients (Recipe_Id,
                                                 Ingredient_Name,
                                                 date_uploaded)
                                            VALUES ( %s,%s,%s)
'''

insert_instructions = '''INSERT INTO Instructions (Recipe_Id,
                                                   Step_Sequence,
                                                   Instruction,
                                                   date_uploaded)
                                                VALUES ( %s,%s,%s,%s)
'''

insert_nutrition = '''INSERT INTO Nutrition (Recipe_Id,
                                             Element,
                                             Quantity,
                                             Unit,
                                             date_uploaded)
                                        VALUES ( %s,%s,%s,%s,%s)
'''