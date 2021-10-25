import os.path
import sys
from numpy.core.numeric import full
from pandas.core.frame import DataFrame
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import pandas as pd
import numpy as np
from numpy import asarray
from numpy import exp
from numpy.random import randn
from numpy.random import rand
from numpy.random import seed
from Utilities.helper_functions import cartesian_product_generalized
from Model.Inputs.nutrition_requirements import NutrientRequirementManager
from Data_Management.MySQL.mysql_manager import MySqlManager
from Data_Management.MySQL.Queries.MySql_model_input import model_input_query

import logging

__author__ = 'bmarx'

logger = logging.getLogger(__name__)

class DailyPlanGenerator:

    

    def __init__(self,
                 db_connection: MySqlManager,
                 user_nutrition_targets: NutrientRequirementManager,
                 past_plans = None) -> None:
        self._sql_connection = db_connection
        self._user_daily_vals = user_nutrition_targets
        self._valid_nutrients = list(self._user_daily_vals.get_daily_requirements().keys())
        self._meal_search_space = None
        self._meal_categories = ['breakfast and brunch', 'lunch', 'dinner']

    @property
    def meal_search_space(self):  # TODO: Put these steps in a method
        if not self._meal_search_space:
            query_df = self._sql_connection.read_to_dataframe(query=model_input_query(self._valid_nutrients))

            nutr_series = pd.Series(self._valid_nutrients).rename('element')
            meal_ids = query_df.groupby(['Meal_Category', 'Recipe_Id']).size().to_frame(name = 'count').reset_index()
            meal_ids = meal_ids.drop(['count'], axis=1)
            nutr_meal_mask = cartesian_product_generalized(left=nutr_series, right=meal_ids).rename(columns={0: 'Element', 1: 'Meal_Category', 2: 'Recipe_Id'})

            full_set = nutr_meal_mask.merge(right=query_df, on=['Recipe_Id', 'Element', 'Meal_Category'], how='left').fillna(0)
            # Filling NAs with 0 is raising Z score for values already populated
            normalized_qtys = pd.DataFrame(full_set.groupby(['Meal_Category', 'Element']).transform(lambda x: (x - x.mean()) / x.std())).drop(['Recipe_Id'], axis=1)
            full_set['normalized_qtys'] = normalized_qtys.values
            full_set = full_set.sort_values(['Recipe_Id', 'Element']).reset_index()

            self._meal_search_space = full_set
            
        return self._meal_search_space

    def _generate_candidate(self, current_state: DataFrame):
        new_arrays = []
        for meal in self._meal_categories:
            cat_search_space = self._meal_search_space[self._meal_search_space['Meal_Category'] == meal]
            cat_current_meal = current_state[current_state['Meal_Category'] == meal]

            perturbation = 0.5 * np.random.rand(len(self._valid_nutrients)) - 0.25  # Uniform Sampling
            current_vector = cat_current_meal['normalized_qtys'].to_numpy()
            rnd_target = perturbation + current_vector
            new_arrays.append(rnd_target)
        return new_arrays


    # TODO: add objective function
    def _objective(self, x):
        return x[0]**2.0

    # TODO: refine/complete simulated annealing algorithm
    def simulated_annealing(objective, bounds, n_iterations, step_size, temp):


        # generate an initial point
        best = bounds[:, 0] + rand(len(bounds)) * (bounds[:, 1] - bounds[:, 0])
        # evaluate the initial point
        best_eval = objective(best)
        # current working solution
        curr, curr_eval = best, best_eval
        # run the algorithm
        for i in range(n_iterations):
            # take a step
            candidate = curr + randn(len(bounds)) * step_size
            # evaluate candidate point
            candidate_eval = objective(candidate)
            # check for new best solution
            if candidate_eval < best_eval:
                # store new best point
                best, best_eval = candidate, candidate_eval
                # report progress
                print('>%d f(%s) = %.5f' % (i, best, best_eval))
            # difference between candidate and current point evaluation
            diff = candidate_eval - curr_eval
            # calculate temperature for current epoch
            t = temp / float(i + 1)
            # calculate metropolis acceptance criterion
            metropolis = exp(-diff / t)
            # check if we should keep the new point
            if diff < 0 or rand() < metropolis:
                # store the new current point
                curr, curr_eval = candidate, candidate_eval
        return [best, best_eval]


""" 
    # seed the pseudorandom number generator
    seed(1)
    # define range for input
    bounds = asarray([[-5.0, 5.0]])
    # define the total iterations
    n_iterations = 1000
    # define the maximum step size
    step_size = 0.1
    # initial temperature
    temp = 10
    # perform the simulated annealing search
    best, score = simulated_annealing(objective, bounds, n_iterations, step_size, temp)
    print('Done!')
    print('f(%s) = %f' % (best, score)) """

if __name__ == '__main__':
    test_connect = MySqlManager()
    test_guy = NutrientRequirementManager(weight=177,
                                          height=6.08,
                                          age=26.5,
                                          gender='male',
                                          weight_goal='gain',
                                          activity='medium',
                                          wgt_unit='lb',
                                          hgt_unit='ft')

    test_plan = DailyPlanGenerator(db_connection=test_connect, \
                                    user_nutrition_targets=test_guy)

    ind = test_plan.meal_search_space
    ind = ind[ind['Recipe_Id'].isin([16239, 223042, 16895])]
    rand_v = test_plan._generate_candidate(ind)
    print(rand_v)