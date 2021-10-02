import sys
sys.path.insert(0, r'C:\Users\bmarx\Coding Projects\Meal Planner')
import logging
from Utilities.helper_functions import convert_unit
from Objects.unit_conversion import WEIGHT_GOAL_TARGETS, CALORIE_TO_NUTRIENT, ACTIVITY_ADJUSTMENTS

__author__ = 'bmarx'

logger = logging.getLogger(__name__)

# TODO: Add in remainder of nutrients

class NutrientRequirementManager:
    
    def __init__(self,
                 weight: float,
                 height: float,
                 age: float,
                 gender: str,
                 weight_goal: str = 'maintain',
                 activity: str = 'medium',
                 wgt_unit: str = 'kg',
                 hgt_unit: str = 'cm') -> None:
        self._weight = weight if wgt_unit == 'kg' else convert_unit(weight, wgt_unit, 'kg')
        self._height = height if hgt_unit == 'cm' else convert_unit(height, hgt_unit, 'cm')
        self._age = age
        self._gender = gender.lower()
        self._weight_goal = weight_goal.lower()
        self._activity_level = activity.lower()
        self._calories = None
        self._sugars = None
        self._carbohydrates = None
        self._proteins = None
        self._fat = None
    
    @property
    def calories(self):
        if not self._calories:
            self._calories = self._get_calorie_requirements()
        return self._calories

    @property
    def carbohydrates(self):
        if not self._carbohydrates:
            self._carbohydrates = self._calculate_nutrient_from_calories(cals=self.calories,
                                                                        tgt=self._weight_goal, 
                                                                        nutrient='carbs')
        return self._carbohydrates

    @property
    def fat(self):
        if not self._fat:
            self._fat = self._calculate_nutrient_from_calories(cals=self.calories,
                                                                tgt=self._weight_goal, 
                                                                nutrient='fat')
        return self._fat

    @property
    def protein(self):
        if not self._proteins:
            self._proteins = self._calculate_nutrient_from_calories(cals=self.calories,
                                                                    tgt=self._weight_goal, 
                                                                    nutrient='protein')
        return self._proteins
    
    @property
    def sugar(self):
        if not self._sugars:
            self._sugars = self._get_sugar_requirements()
        return self._sugars
    
    def get_daily_requirements(self) -> dict:
        daily_reqs = {
            'calories': self.calories,
            'carbohydrates': self.carbohydrates,
            'fat': self.fat,
            'protein': self.protein,
            'sugar': self.sugar
                    }
        
        return daily_reqs

    def _get_calorie_requirements(self) -> float:

        bmr = self._calculate_bmr()
        try:
            activity_factor = ACTIVITY_ADJUSTMENTS[self._activity_level]
        except:
            activity_factor = 1
        req_calories = bmr * activity_factor

        return req_calories

    def _get_sugar_requirements(self) -> float:
        '''
        Men: 150 calories per day (37.5 grams or 9 teaspoons)
        Women: 100 calories per day (25 grams or 6 teaspoons)
        '''

        if self._gender == 'male':
            sugar_grams = 37.5

        elif self._gender == 'female':
            sugar_grams = 25
        
        else:
            logger.info('No gender specified')
            return 31.25
        
        return sugar_grams

    @staticmethod
    def _calculate_nutrient_from_calories(cals: float, tgt: str, nutrient: str) -> float:
        '''
        Used to determine nutrient reqs in grams for those which can be derived from daily calorie reqs
        '''
        try:
            pct_allocation = WEIGHT_GOAL_TARGETS[tgt][nutrient]
        except:
            return 0
        cal_portion = cals * pct_allocation
        cal_to_gram = CALORIE_TO_NUTRIENT[nutrient]
        req_grams = cal_portion * cal_to_gram
        return req_grams

    def _calculate_bmr(self):
        '''
        Using the Mifflin-St Jeor Equation to calculate caloric requirements:
        BMR: Base Metabolic Rate. It is the calories needed to maintain homeostasis with no activity.
        Male: BMR = 10W + 6.25H - 5A + 5
        Female: BMR = 10W + 6.25H - 5A - 161
        where:
        W is body weight in kg
        H is body height in cm
        A is age
        '''
        bmr = 10*self._weight + 6.25*self._height - 5*self._age

        try:
            gender_cleansed = self._gender
        except:
            logger.info('No gender specified')
            return bmr

        if gender_cleansed == 'male':
            bmr += 5

        elif gender_cleansed == 'female':
            bmr -= 161
        
        return bmr


if __name__ == '__main__':
    
    test_guy = NutrientRequirementManager(weight=177,
                                          height=6.08,
                                          age=26.5,
                                          gender='male',
                                          weight_goal='gain',
                                          activity='medium',
                                          wgt_unit='lb',
                                          hgt_unit='ft')
    reqs = test_guy.get_daily_requirements()
    print(reqs)