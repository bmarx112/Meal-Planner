import logging

__author__ = 'bmarx'

logger = logging.getLogger(__name__)

# TODO: Turn this into a req manager class instead of a list of functions

def get_calorie_requirements(kg: float, height_cm: float, age: float, gender: str = None) -> float:
    '''
    Using the Mifflin-St Jeor Equation to calculate caloric requirements:
    Male: BMR = 10W + 6.25H - 5A + 5
    Female: BMR = 10W + 6.25H - 5A - 161
    where:
    W is body weight in kg
    H is body height in cm
    A is age
    '''

    req_calories = 10*kg + 6.25*height_cm + 5*age

    try:
        gender_cleansed = gender.lower()
    except:
        logger.info('No gender specified')
        return req_calories

    if gender_cleansed == 'male':
        req_calories += 5

    elif gender_cleansed == 'female':
        req_calories -= 161
    
    return req_calories

def get_sugar_requirements(gender: str = None) -> float:
    '''
    Men: 150 calories per day (37.5 grams or 9 teaspoons)
    Women: 100 calories per day (25 grams or 6 teaspoons)
    '''
    try:
        gender_cleansed = gender.lower()
    except:
        logger.info('No gender specified')
        return 31.25

    if gender_cleansed == 'male':
        sugar_grams = 37.5

    elif gender_cleansed == 'female':
        sugar_grams = 25
    
    return sugar_grams

def get_carbohydrate_requirements(calories: float = 2000) -> float:
    '''
    From bodybuilding.com
    calorie count is split into macronutrient percentages in the following ratios, 
    based on splits commonly recommended by our nutrition experts for muscle gain, 
    weight loss, and weight maintenance. 

    (carbohydrates/protein/fats)
    Weight loss: 40/40/20 
    Weight gain: 40/30/30
    Weight maintenance: 40/30/30

    These daily grams of each "macro" come from applying those percentages to your daily calorie number. 
    Each gram of a macronutrient is "worth" this many calories:
    Protein: 4 calories
    Carbs: 4 calories
    Fats: 9 calories
    '''

    carb_grams = calories / 40

    return carb_grams