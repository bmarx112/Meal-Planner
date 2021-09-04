import logging

__author__ = 'bmarx'

logger = logging.getLogger(__name__)

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