import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from Model.Inputs.nutrition_requirements import NutrientRequirementManager
import unittest
from Testing.Unit_Tests.test_calorie_calculation.calorie_test_mock_objects import TestPerson

class CalorieCalcTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.weight = 80.0
        self.height = 185.0
        self.age = 26.5

    def test_calories_for_male(self):
        sex = 'Male'
        person = TestPerson(weight=self.weight,
                            height=self.height,
                            age=self.age,
                            gender=sex)

        nutr = NutrientRequirementManager(weight=person.weight, 
                                                 height=person.height, 
                                                 age=person.age,
                                                 gender=person.gender)

        calc_calories = nutr.calories
        expected_cals = 2834.5625
        self.assertAlmostEqual(calc_calories, expected_cals, places=3)

    def test_calories_for_female(self):
        sex = 'FeMale'
        person = TestPerson(weight=self.weight,
                            height=self.height,
                            age=self.age,
                            gender=sex)

        nutr = NutrientRequirementManager(weight=person.weight, 
                                                 height=person.height, 
                                                 age=person.age,
                                                 gender=person.gender)

        calc_calories = nutr.calories
        expected_cals = 2577.2625
        self.assertAlmostEqual(calc_calories, expected_cals, places=3)

    def test_calories_no_gender(self):
        person = TestPerson(weight=self.weight,
                            height=self.height,
                            age=self.age)

        nutr = NutrientRequirementManager(weight=person.weight, 
                                                 height=person.height, 
                                                 age=person.age,
                                                 gender=person.gender)

        calc_calories = nutr.calories
        expected_cals = 2826.8125
        self.assertAlmostEqual(calc_calories, expected_cals, places=3)

if __name__=='__main__':
    unittest.main()