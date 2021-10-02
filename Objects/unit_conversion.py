
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

WEIGHT_GOAL_TARGETS = {
                        'maintain': {
                                  'carbs': 0.4,
                                  'protein': 0.3,
                                  'fat': 0.3
                                  },
                        'gain': {
                                  'carbs': 0.4,
                                  'protein': 0.3,
                                  'fat': 0.3
                                  },
                        'lose': {
                                  'carbs': 0.4,
                                  'protein': 0.4,
                                  'fat': 0.2
                                  },
                        }

CALORIE_TO_NUTRIENT = {
                        'carbs': 1/4,
                        'protein': 1/4,
                        'fat': 1/9
                      }

CONVERSION_TABLE = {
                    ('lb', 'kg'): 0.4535924,
                    ('kg', 'lb'): 2.204623,
                    ('ft', 'cm'): 30.48,
                    ('m', 'cm'): 100,
                    ('cm', 'ft'): 0.0328084,
                    ('cm', 'm'): 0.01
                    }

ACTIVITY_ADJUSTMENTS = {
                        'none': 1.2,
                        'low': 1.375,
                        'medium': 1.55,
                        'high': 1.725,
                        'very high': 1.9
                      }