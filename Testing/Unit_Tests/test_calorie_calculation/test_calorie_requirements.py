import sys
sys.path.insert(0, r'C:\Users\bmarx\Coding Projects\Meal Planner')
from Model.Inputs.calorie_requirements import get_calorie_requirements
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

        calc_calories = get_calorie_requirements(kg=person.weight, 
                                                 height_cm=person.height, 
                                                 age=person.age,
                                                 gender=person.gender)

        expected_cals = 2093.75
        self.assertEqual(calc_calories, expected_cals)

    def test_calories_for_female(self):
        sex = 'FeMale'
        person = TestPerson(weight=self.weight,
                            height=self.height,
                            age=self.age,
                            gender=sex)

        calc_calories = get_calorie_requirements(kg=person.weight, 
                                                 height_cm=person.height, 
                                                 age=person.age,
                                                 gender=person.gender)

        expected_cals = 1927.75
        self.assertEqual(calc_calories, expected_cals)

    def test_calories_no_gender(self):
        person = TestPerson(weight=self.weight,
                            height=self.height,
                            age=self.age)

        calc_calories = get_calorie_requirements(kg=person.weight, 
                                                 height_cm=person.height, 
                                                 age=person.age,
                                                 gender=person.gender)

        expected_cals = 2088.75
        self.assertEqual(calc_calories, expected_cals)

if __name__=='__main__':
    unittest.main()