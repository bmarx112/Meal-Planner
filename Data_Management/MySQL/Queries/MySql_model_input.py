def model_input_query(nutrients: list) -> str:
    
    valid_elements = s = '(\'' + '\', \''.join(nutrients) + '\')'

    pull_nutrients = f'''
    SELECT m.Meal_Category, m.Recipe_Id, n.Element, n.Quantity
    FROM Meal m
    JOIN nutrition n
    ON m.Recipe_Id = n.Recipe_Id
    WHERE m.Meal_Category IN ('breakfast and brunch', 'lunch', 'dinner')
    AND n.Element IN {valid_elements}
    '''

    return pull_nutrients