def model_nutrition_query_with_doubled(nutrients: list, calorie_cutoff: float = 1000) -> str:
    
    valid_elements = '(\'' + '\', \''.join(nutrients) + '\')'

    pull_nutrients = f'''
    SELECT m.Meal_Category, m.Recipe_Id, n.Element, n.Quantity
    FROM Meal m
    JOIN nutrition n
    ON m.Recipe_Id = n.Recipe_Id
    WHERE m.Meal_Category IN ('breakfast and brunch', 'lunch', 'dinner')
    AND n.Element IN {valid_elements}
    AND m.Recipe_Id in  (
        SELECT n.Recipe_Id
        from nutrition n
        where n.Element = 'Calories' AND n.Quantity <= {calorie_cutoff}
        GROUP BY n.Recipe_Id
    )
    UNION ALL
    SELECT m.Meal_Category, CONCAT(m.Recipe_Id, '_2') as Recipe_Id, n.Element, n.Quantity * 2 as Quantity
    FROM Meal m
    JOIN nutrition n
    ON m.Recipe_Id = n.Recipe_Id
    WHERE m.Meal_Category IN ('breakfast and brunch', 'lunch', 'dinner')
    AND n.Element IN {valid_elements}
    AND m.Recipe_Id in  (
        SELECT n.Recipe_Id
        from nutrition n
        where n.Element = 'Calories' AND n.Quantity <= {calorie_cutoff}
        GROUP BY n.Recipe_Id
    )
    '''

    return pull_nutrients

def model_nutrition_query_with_doubled_and_tripled(nutrients: list) -> str:
    
    valid_elements = '(\'' + '\', \''.join(nutrients) + '\')'

    pull_nutrients = f'''
    SELECT m.Meal_Category, m.Recipe_Id, n.Element, n.Quantity
    FROM Meal m
    JOIN nutrition n
    ON m.Recipe_Id = n.Recipe_Id
    WHERE m.Meal_Category IN ('breakfast and brunch', 'lunch', 'dinner')
    AND n.Element IN {valid_elements}
    UNION ALL
    SELECT m.Meal_Category, CONCAT(m.Recipe_Id, '_2') as Recipe_Id, n.Element, n.Quantity * 2 as Quantity
    FROM Meal m
    JOIN nutrition n
    ON m.Recipe_Id = n.Recipe_Id
    WHERE m.Meal_Category IN ('breakfast and brunch', 'lunch', 'dinner')
    AND n.Element IN {valid_elements}
    UNION ALL
    SELECT m.Meal_Category, CONCAT(m.Recipe_Id, '_3') as Recipe_Id, n.Element, n.Quantity * 3 as Quantity
    FROM Meal m
    JOIN nutrition n
    ON m.Recipe_Id = n.Recipe_Id
    WHERE m.Meal_Category IN ('breakfast and brunch', 'lunch', 'dinner')
    AND n.Element IN {valid_elements}
    '''

    return pull_nutrients

def model_nutrition_query_doubled(nutrients: list) -> str:
    
    valid_elements = '(\'' + '\', \''.join(nutrients) + '\')'

    pull_nutrients = f'''
    SELECT m.Meal_Category, CONCAT(m.Recipe_Id, '_2') as Recipe_Id, n.Element, n.Quantity * 2 as Quantity
    FROM Meal m
    JOIN nutrition n
    ON m.Recipe_Id = n.Recipe_Id
    WHERE m.Meal_Category IN ('breakfast and brunch', 'lunch', 'dinner')
    AND n.Element IN {valid_elements}
    '''

    return pull_nutrients

def model_ingredient_query() -> str:
    
    pull_ingredients = '''
        SELECT m.Meal_Category, i.Recipe_Id, i.Ingredient_Name, i.Ingredient_Quantity
        FROM ingredients i 
        JOIN Meal m
        ON m.Recipe_Id = i.Recipe_Id
        UNION ALL
        SELECT m.Meal_Category, CONCAT(i.Recipe_Id, '_2') as Recipe_Id, i.Ingredient_Name, i.Ingredient_Quantity * 2 as Ingredient_Quantity
        FROM ingredients i
        JOIN Meal m
        ON m.Recipe_Id = i.Recipe_Id
        '''

    return pull_ingredients

def model_output_recipe_names(nutrients: list) -> str:

    valid_elements = '(\'' + '\', \''.join(nutrients) + '\')'

    pull_names = f'''
        SELECT Meal_Category, Meal_Name, Recipe_Id
        FROM (
            SELECT Meal_Category, CAST(Recipe_Id as CHAR) as Recipe_Id, Meal_Name
            FROM Meal m
            UNION ALL
            SELECT Meal_Category, CONCAT(Recipe_Id, '_2') as Recipe_Id, CONCAT(Meal_Name, ' x2') as Meal_Name 
            FROM Meal m
        ) source
        WHERE CAST(Recipe_Id as CHAR) in {valid_elements}
    '''

    return pull_names

def recipes_in_database() -> str:

    recipe_count = '''
        SELECT COUNT(Recipe_Id) as count
        FROM Meal
    '''

    return recipe_count