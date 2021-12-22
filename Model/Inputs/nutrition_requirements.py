import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
import logging
from Utilities.helper_functions import convert_unit
from Objects.unit_conversion import WEIGHT_GOAL_TARGETS, CALORIE_TO_NUTRIENT, ACTIVITY_ADJUSTMENTS
from Objects.nutrient_statics import req_calcium, req_vit_c, req_sodium, req_folate, req_cholesterol

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
        self._gender = gender.lower() if gender else None
        self._weight_goal = weight_goal.lower()
        self._activity_level = activity.lower()
        self.calories = self._get_calorie_requirements()
        self.sugar = self._get_daily_sugar_requirements()
        self.carbohydrates = self._calculate_nutrient_from_calories(cals=self.calories,
                                                                        tgt=self._weight_goal, 
                                                                        nutrient='carbs')
        self.protein = self._calculate_nutrient_from_calories(cals=self.calories,
                                                                    tgt=self._weight_goal, 
                                                                    nutrient='protein')
        self.fat = self._calculate_nutrient_from_calories(cals=self.calories,
                                                                tgt=self._weight_goal, 
                                                                nutrient='fat')
        self.saturated_fat = self._calculate_nutrient_from_calories(cals=self.calories,
                                                                    tgt=self._weight_goal, 
                                                                    nutrient='saturated_fat')
        self.calcium = req_calcium
        self.dietary_fiber = self._get_daily_fiber_requirements()
        self.vitamin_a = self._get_daily_vitamin_a_requirements()
        self.vitamin_c = req_vit_c
        self.vitamin_b6 = self._get_daily_vitamin_b6_requirements()
        self.sodium = req_sodium
        self.folate = req_folate
        self.cholesterol = req_cholesterol
        self.niacin = self._get_daily_niacin_requirements()
        self.iron = None  # TODO: Enter logic into iron method
        self.magnesium = None  # TODO: Add Magnesium Method
        self.potassium = None  # TODO: Add Potassium Method
        self.thiamin = None  # TODO: Add Thiamin Method


    def get_daily_requirements(self) -> dict:  # TODO: Add remaining nutrients to dict
        daily_reqs = {
            'Calories': self.calories,
            'carbohydrates': self.carbohydrates,
            'fat': self.fat,
            'saturated fat': self.saturated_fat,
            'protein': self.protein,
            'sugars': self.sugar,
            'calcium': self.calcium,
            'dietary fiber': self.dietary_fiber,
            'vitamin a iu': self.vitamin_a,
            'vitamin c': self.vitamin_c,
            'vitamin b6': self.vitamin_b6,
            'sodium': self.sodium,
            'folate': self.folate,
            'cholesterol': self.cholesterol,
            'niacin equivalents': self.niacin
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

    def _get_daily_sugar_requirements(self) -> float:
        '''
        Men: 150 calories per day (37.5 grams or 9 teaspoons)
        Women: 100 calories per day (25 grams or 6 teaspoons)
        '''

        if self._gender == 'male':
            req_sugar = 37.5

        elif self._gender == 'female':
            req_sugar = 25
        
        else:
            logger.info('No gender specified')
            return 31.25
        
        return req_sugar

    def _get_daily_fiber_requirements(self) -> float:
        '''
        Per WebMD: Women need 25 grams of fiber per day, and men need 38 grams per day, according to the Institute of Medicine.
        '''

        if self._gender == 'male':
            req_fiber = 38

        elif self._gender == 'female':
            req_fiber = 25
        
        else:
            logger.info('No gender specified')
            req_fiber = 31.5
        
        return req_fiber
    
    def _get_daily_vitamin_b6_requirements(self) -> float:
        '''
        recommended daily amount of vitamin B-6 for adults 50 and younger is 1.3 milligrams. 
        After age 50, the recommended daily amount is 1.5 milligrams for women and 1.7 milligrams for men.
        '''

        if self._age <= 50:
            return 1.3
        
        if self._gender == 'male':
            req_b6 = 1.7

        elif self._gender == 'female':
            req_b6 = 1.5
        
        else:
            logger.info('No gender specified')
            req_b6 = 1.6
        
        return req_b6

    def _get_daily_vitamin_a_requirements(self) -> float:
        '''
        daily amount of vitamin A is 900 micrograms (mcg) for adult men and 700 mcg for adult women.
        1 IU = 0.3 mcg
        '''

        if self._gender == 'male':
            req_vit_a = 900 / 0.3

        elif self._gender == 'female':
            req_vit_a = 700 / 0.3
        
        else:
            logger.info('No gender specified')
            req_vit_a = 800 / 0.3
        
        return req_vit_a

    def _get_daily_iron_requirements(self) -> float:
        '''
        daily amount of vitamin A is 900 micrograms (mcg) for adult men and 700 mcg for adult women.
        1 IU = 0.3 mcg
        '''

        if self._gender == 'male':
            
            req_vit_a = 900 / 0.3

        elif self._gender == 'female':
            req_vit_a = 700 / 0.3
        
        else:
            logger.info('No gender specified')
            req_vit_a = 800 / 0.3
        
        return req_vit_a

    def _get_daily_niacin_requirements(self) -> float:
        '''
        recommended daily amount of niacin for adult males is 16 milligrams (mg) a day and for adult women who aren't pregnant, 14 mg a day.
        '''

        if self._gender == 'male':
            req_niacin = 16

        elif self._gender == 'female':
            req_niacin = 14
        
        else:
            logger.info('No gender specified')
            req_niacin = 15
        
        return req_niacin

    def _get_daily_iron_requirements(self) -> float:

        if self._gender == 'male':
            if self._age <= 0.5:
                req_iron = 0.27
            elif self._age <= 1.0:
                req_iron = 11
            elif self._age <= 3.0:
                req_iron = 7
            elif self._age <= 8:
                req_iron = 10
            elif self._age <= 13:
                req_iron = 8
            elif self._age <= 18:
                req_iron = 11
            else:
                req_iron = 8
            

        elif self._gender == 'female':
            if self._age <= 0.5:
                req_iron = 0.27
            elif self._age <= 1.0:
                req_iron = 11
            elif self._age <= 3.0:
                req_iron = 7
            elif self._age <= 8:
                req_iron = 10
            elif self._age <= 13:
                req_iron = 8
            elif self._age <= 18:
                req_iron = 15
            elif self._age <= 50:
                req_iron = 18
            else:
                req_iron = 8
        
        else:
            logger.info('No gender specified')
            if self._age <= 0.5:
                req_iron = 0.27
            elif self._age <= 1.0:
                req_iron = 11
            elif self._age <= 3.0:
                req_iron = 7
            elif self._age <= 8:
                req_iron = 10
            elif self._age <= 13:
                req_iron = 8
            elif self._age <= 18:
                req_iron = 13
            elif self._age <= 50:
                req_iron = 13
            else:
                req_iron = 8
        
        return req_iron


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
    print(list(reqs.keys()))