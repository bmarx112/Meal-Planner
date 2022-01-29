from collections import defaultdict
import os.path
import sys
from typing import List
from pandas.core.series import Series
import scipy.spatial as sp
from pandas.core.frame import DataFrame
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import pandas as pd
import numpy as np
from numpy import asarray
from numpy import exp
from numpy.random import randn
from numpy.random import rand
from numpy.random import seed
from matplotlib import pyplot, use

from Utilities.helper_functions import cartesian_product_generalized, timeit
from Model.Inputs.nutrition_requirements import NutrientRequirementManager
from Data_Management.MySQL.mysql_manager import MySqlManager
from Data_Management.MySQL.Queries.MySql_model_input import model_ingredient_query, model_nutrition_query_with_doubled, model_output_recipe_names, model_nutrition_query_with_doubled_and_tripled

import logging

__author__ = 'bmarx'

logger = logging.getLogger(__name__)

default_weights = [1]*16  # TODO: add this to new file to hold static values

class PlanGenerator:

    def __init__(self,
                 db_connection: MySqlManager,
                 user_nutrition_targets: NutrientRequirementManager,
                 num_iterations: int=10000,
                 nutrient_weights: list=default_weights,
                 temp: int = 150,
                 similarity_smoothing_factor: float = 0.75,
                 perturbation_size: float = 2) -> None:
        self._sql_connection = db_connection
        self._user_daily_vals = user_nutrition_targets
        self._user_vals_df = pd.DataFrame
        self._valid_nutrients = list(self._user_daily_vals.get_daily_requirements().keys())
        self.num_valid_nutrients = len(self._valid_nutrients)
        self._meal_search_space_base = pd.DataFrame()
        self.meal_nutr_data = self._generate_meal_nutrition_dataset()
        self.meal_search_space_normalized = self._generate_normalized_nutrition_dataset()
        self.meal_ingredients_df = self._sql_connection.read_to_dataframe(query=model_ingredient_query())
        self._meal_categories = ['breakfast and brunch', 'lunch', 'dinner']  # TODO: add this to new file to hold static values
        self._n_iter = num_iterations
        self._temp = temp
        self._weight_list = nutrient_weights
        self._similarity_smoothing_factor = similarity_smoothing_factor
        self.objective_function_weights = pd.Series(self._weight_list)
        self.past_plans = {}
        self.perturbation_size = perturbation_size
        

    @property
    def user_vals_df(self) -> DataFrame:
        if self._user_vals_df.empty:
            self._user_vals_df = pd.DataFrame.from_dict(data=self._user_daily_vals.get_daily_requirements(),
                                                        orient='index',
                                                        columns=['Quantity'])
            self._user_vals_df = self._user_vals_df.reset_index()
            self._user_vals_df = self._user_vals_df.rename(columns={'index': 'Element'})                                            
        return self._user_vals_df

    @property
    def meal_search_space_base(self) -> DataFrame:
        if self._meal_search_space_base.empty:
            full_set = self.meal_nutr_data
            full_set = full_set.pivot(index=['Meal_Category', 'Recipe_Id'], columns='Element', values='Quantity').reset_index()
            self._meal_search_space_base = full_set
        
        return self._meal_search_space_base
    
    def _generate_meal_nutrition_dataset(self) -> DataFrame:
        query_df = self._sql_connection.read_to_dataframe(query=model_nutrition_query_with_doubled(self._valid_nutrients, calorie_cutoff=1500))
        nutr_series = pd.Series(self._valid_nutrients).rename('element')

        query_df['Recipe_Id'] = query_df['Recipe_Id'].astype('str')

        meal_ids = query_df.groupby(['Meal_Category', 'Recipe_Id']).size().to_frame(name = 'count').reset_index()
        meal_ids = meal_ids.drop(['count'], axis=1)

        nutr_meal_mask = cartesian_product_generalized(left=nutr_series, right=meal_ids).rename(columns={0: 'Element', 1: 'Meal_Category', 2: 'Recipe_Id'})

        # Filling NAs with 0 is raising Z score for values already populated
        full_set = nutr_meal_mask.merge(right=query_df, on=['Recipe_Id', 'Element', 'Meal_Category'], how='left').fillna(0)

        return full_set
    
    def _generate_normalized_nutrition_dataset(self) -> DataFrame:
        modified_df = self.meal_nutr_data.drop(['Recipe_Id'], axis=1)
        normalized_qtys = pd.DataFrame(modified_df.groupby(['Meal_Category', 'Element']).transform(lambda x: (x - x.mean()) / x.std()))

        full_set = self.meal_nutr_data
        full_set['normalized_qtys'] = normalized_qtys.values
        full_set = full_set.pivot(index=['Meal_Category', 'Recipe_Id'], columns='Element', values='normalized_qtys').reset_index()

        return full_set

    @timeit
    def generate_daily_plan(self) -> List:
        opt_output = self.simulated_annealing()
        #meal_plan = opt_output[0]
        return opt_output

    def generate_weekly_plan(self):
        week_plan = {}
        week_scores = {}
        for day in range(7):
            day_plan = self.generate_daily_plan()
            week_plan[day + 1] = day_plan[0]
            week_scores[day + 1] = day_plan[1]
            self._add_meals_to_previous_plan_dict(meals=day_plan, day=day+1)
            print(f'Plan for day {day + 1} complete!')
        return week_plan, week_scores

    def generate_weekly_plan_no_past(self):
        week_plan = {}
        week_scores = {}
        for day in range(7):
            day_plan = self.generate_daily_plan()
            week_plan[day + 1] = day_plan[0]
            week_scores[day + 1] = day_plan[1]
        print('DONE')
        return week_plan, week_scores

    def _add_meals_to_previous_plan_dict(self, meals: list, day: int) -> None:
        target_ingredients = self._get_ingredients(meal_list=meals)
        self.past_plans[day] = target_ingredients

    def reset_past_plans(self) -> None:
        self.past_plans = {}

    def _get_ingredients(self, meal_list) -> DataFrame:
        target_ingredients = self.meal_ingredients_df[self.meal_ingredients_df['Recipe_Id'].isin(meal_list)]
        return target_ingredients

    def _calculate_ingredient_similarity(self, meal_id_list: list) -> float:
        ingredients_df = self._get_ingredients(meal_list=meal_id_list)
        score = 0
        if self.past_plans == {}:
            return score
        current_day = max(self.past_plans.keys()) + 1
        # TODO: This is temporary until we add ingredient qtys into the calc
        for day, ing in self.past_plans.items():
            for category in self._meal_categories:
                past_ing_set = set(ing[ing['Meal_Category']==category]['Ingredient_Name'].unique())
                curr_ing_set = set(ingredients_df[ingredients_df['Meal_Category']==category]['Ingredient_Name'].unique())
                jaccard = self._calculate_jaccard(past_ing_set, curr_ing_set)
                days_from_current = current_day - day
                score += jaccard * ((1-self._similarity_smoothing_factor) ** days_from_current)

        return score

    @staticmethod
    def _calculate_jaccard(set_a: set, set_b: set) -> float:
        index = len(set_a.intersection(set_b)) / len(set_a.union(set_b))
        return index

    def _generate_candidate(self, current_state: DataFrame) -> list:
        perturbation = self.perturbation_size * np.random.rand(self.num_valid_nutrients) - (self.perturbation_size / 2)
        current_meal = current_state.sample(n=1)

        state_list = current_state['Recipe_Id'].tolist()
        replaced_item_loc = state_list.index(current_meal['Recipe_Id'].values[0])

        current_vector = current_meal.drop(['Meal_Category', 'Recipe_Id'], axis=1).to_numpy()
        category = current_meal['Meal_Category'].values[0]
        cat_meal_list = current_state[current_state['Meal_Category'] == category]['Recipe_Id'].tolist()
        # Exclude current state meals in cat. and turn search space df into (n, len(nutrients)) numpy array
        cat_search_space = self.meal_search_space_normalized[self.meal_search_space_normalized['Meal_Category'] == category]
        cat_search_space = cat_search_space[~cat_search_space['Recipe_Id'].isin(cat_meal_list)].reset_index(drop=True)
        vectorized_search_space = cat_search_space.drop(['Meal_Category', 'Recipe_Id'], axis=1).to_numpy()

        rnd_target = perturbation + current_vector

        # Using Manhatten distance since we are in high dimensional space 
        dist = sp.distance.cdist(vectorized_search_space, rnd_target, metric='cityblock')
        closest_distance_in_cat_id = np.argmin(dist, axis=0)[0]

        candidate_recipe_id = cat_search_space.iloc[[closest_distance_in_cat_id], 1].reset_index(drop=True)[0]

        state_list[replaced_item_loc] = candidate_recipe_id

        return state_list

    def blend_target_with_curr(self, meal_list: list) -> DataFrame:
        state_df = self.meal_search_space_base[self.meal_search_space_base['Recipe_Id'].isin(meal_list)]
        state_df = state_df.drop(['Meal_Category', 'Recipe_Id'], axis=1)

        daily_nutr_qtys = pd.DataFrame(state_df.groupby([True]*len(state_df)).sum())        
        daily_nutr_qtys = daily_nutr_qtys.melt(var_name='Element', value_name='Sum_Quantity')

        comparison_df = daily_nutr_qtys.merge(right=self.user_vals_df, on=['Element'], how='right')
        comparison_df['pct_difference'] = self._calcualte_pct_diff(quant_1=comparison_df['Quantity'], quant_2=comparison_df['Sum_Quantity'])

        comparison_df['weighted_diff'] = comparison_df['pct_difference'] * self.objective_function_weights

        return comparison_df

    def _calculate_energy(self, curr_state: list) -> float:
        compare_df = self.blend_target_with_curr(curr_state)

        energy = compare_df['weighted_diff'].sum()
        similarity_penalty = self._calculate_ingredient_similarity(meal_id_list=curr_state)
        energy += similarity_penalty
        return energy

    # TODO: refine/complete simulated annealing algorithm
    def simulated_annealing(self):
        stall_counter = 0
        cutoff_threshold = 200
        # generate an initial meal set
        current_state = self.meal_search_space_normalized.sample(frac=1).groupby('Meal_Category', sort=False).head(2)
        current_ids = current_state['Recipe_Id'].reset_index(drop=True).tolist()
        # evaluate the initial point
        current_eval = self._calculate_energy(current_ids)
        best, best_eval = current_ids, current_eval
        # current working solution
        scores = []
        # run the algorithm
        for i in range(self._n_iter):
            # take a step
            candidate_ids = self._generate_candidate(current_state)
            candidate_state = self.meal_search_space_normalized[self.meal_search_space_normalized['Recipe_Id'].isin(candidate_ids)]
            # evaluate candidate point
            candidate_eval = self._calculate_energy(candidate_ids)
            stall_counter += 1
            # check for new best solution
            if candidate_eval < current_eval:
                # store new best point
                best, best_eval = candidate_ids, candidate_eval
                scores.append(best_eval)
                # report progress
            # difference between candidate and current point evaluation
            diff = candidate_eval - current_eval
            # calculate temperature for current epoch
            t = self._temp / float(i + 1)
            # calculate metropolis acceptance criterion
            metropolis = exp(-diff / t)
            # check if we should keep the new point
            if diff < 0 or rand() < metropolis:
                # store the new current point
                current_state, current_eval = candidate_state, candidate_eval
                stall_counter = 0

            if stall_counter > cutoff_threshold:
                print('-----Reached Stall Limit-----')
                break
        return [best, best_eval, scores]

    @staticmethod
    def _calcualte_pct_diff(quant_1: Series, quant_2: Series) -> Series:
        quotient = (quant_1 - quant_2) / ((quant_1 + quant_2) / 2)
        abs_quotient = abs(quotient)

        return abs_quotient


if __name__ == '__main__':
    pd.set_option('display.max_rows', None)
    test_connect = MySqlManager(database='mealplanner_test')
    test_guy = NutrientRequirementManager(weight=182,
                                          height=6.08,
                                          age=27,
                                          gender='male',
                                          weight_goal='gain',
                                          activity='medium',
                                          wgt_unit='lb',
                                          hgt_unit='ft')

    weights = [2.5, 1.5,
               1, 1.5,
               1.2, 1.1,
               1, 1.5,
               0.25, 1,
               0.1, 1,
               0.25, 1,
               0.05, 0.05]

    test_plan = PlanGenerator(db_connection=test_connect,
                                    user_nutrition_targets=test_guy,
                                    num_iterations=3000,
                                    nutrient_weights=weights,
                                    similarity_smoothing_factor=0.15,
                                    temp=150,
                                    perturbation_size=1.5
                                    )

    seed(1112)
    interval = 250
    temps = [(i+1)*interval for i in range(4)]
    e, e_s = test_plan.generate_weekly_plan()
    # test_plan.reset_past_plans()
    # n, n_s = test_plan.generate_weekly_plan_no_past()
    rec_count = defaultdict(int)
    for key, value in e.items():
        print(f'{key}:')
        query_df = test_plan._sql_connection.read_to_dataframe(query=model_output_recipe_names(value))
        for l, i in query_df['Recipe_Id'].items():
            rec_count[i] += 1
        print(query_df)
        print('')

    for key, value in e_s.items():
        print(f'{key}:')
        print(value)
    #rec_count
    # print(i for i, ct in rec_count.items() if ct > 1)
    # temps = [100]*3
    # bfast = []
    # lunch = []
    # dinner = []
    # score_list = []
    # print('begin annealing')
    # for tmp in temps:
    #     best, score, scores = test_plan.simulated_annealing()
    #     print('f(%s, theta) = %f' % (best, score))
        
    #     bfast.append(best[0])
    #     lunch.append(best[1])
    #     dinner.append(best[2])

    #     score_list.append(score)

    #     comparison_df = test_plan.blend_target_with_curr(best)
    #     comparison_df = comparison_df.drop(['pct_difference'], axis=1)
    #     print(comparison_df)

    #     pyplot.plot(scores, '.-')
    #     pyplot.xlabel('Improvement Number')
    #     pyplot.ylabel('Evaluation f(x)')
    #     pyplot.show()

    # print(score_list)