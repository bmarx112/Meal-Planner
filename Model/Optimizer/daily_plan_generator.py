import os.path
import sys
import scipy.spatial as sp
from numpy.core.arrayprint import printoptions
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
from matplotlib import pyplot

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
                 past_plans = None,
                 num_iterations: int=10000) -> None:
        self._sql_connection = db_connection
        self._user_daily_vals = user_nutrition_targets
        self._user_vals_df = pd.DataFrame
        self._valid_nutrients = list(self._user_daily_vals.get_daily_requirements().keys())
        self._num_valid_nutrients = None
        self._meal_search_space_normalized = pd.DataFrame()
        self._meal_search_space_base = pd.DataFrame()
        self._meal_nutr_data = pd.DataFrame()
        self._meal_categories = ['breakfast and brunch', 'lunch', 'dinner']
        self._n_iter = num_iterations

    @property
    def user_vals_df(self) -> DataFrame:
        if self._user_vals_df.empty:
            self._user_vals_df = pd.DataFrame.from_dict(data=self._user_daily_vals.get_daily_requirements(),
                                                        orient='index',
                                                        columns=['Quantity'])
            self._user_vals_df = self._user_vals_df.reset_index()
        return self._user_vals_df

    @property
    def num_valid_nutrients(self) -> int:
        if not self._num_valid_nutrients:
            self._num_valid_nutrients = len(self._valid_nutrients)
        return self._num_valid_nutrients

    @property
    def meal_nutr_data(self) -> DataFrame:  # TODO: Put these steps in a method
        if self._meal_nutr_data.empty:
            query_df = self._sql_connection.read_to_dataframe(query=model_input_query(self._valid_nutrients))

            nutr_series = pd.Series(self._valid_nutrients).rename('element')
            meal_ids = query_df.groupby(['Meal_Category', 'Recipe_Id']).size().to_frame(name = 'count').reset_index()
            meal_ids = meal_ids.drop(['count'], axis=1)
            nutr_meal_mask = cartesian_product_generalized(left=nutr_series, right=meal_ids).rename(columns={0: 'Element', 1: 'Meal_Category', 2: 'Recipe_Id'})
            # Filling NAs with 0 is raising Z score for values already populated
            full_set = nutr_meal_mask.merge(right=query_df, on=['Recipe_Id', 'Element', 'Meal_Category'], how='left').fillna(0)
            self._meal_nutr_data = full_set
            
        return self._meal_nutr_data

    @property
    def meal_search_space_normalized(self) -> DataFrame:  # TODO: Put these steps in a method
        if self._meal_search_space_normalized.empty:
            normalized_qtys = pd.DataFrame(self.meal_nutr_data.groupby(['Meal_Category', 'Element']).transform(lambda x: (x - x.mean()) / x.std())).drop(['Recipe_Id'], axis=1)
            full_set = self.meal_nutr_data
            full_set['normalized_qtys'] = normalized_qtys.values
            full_set = full_set.pivot(index=['Meal_Category', 'Recipe_Id'], columns='Element', values='normalized_qtys').reset_index()
            self._meal_search_space_normalized = full_set
            
        return self._meal_search_space_normalized

    @property
    def meal_search_space_base(self) -> DataFrame:  # TODO: Put these steps in a method
        if self._meal_search_space_base.empty:
            full_set = self.meal_nutr_data
            full_set = full_set.pivot(index=['Meal_Category', 'Recipe_Id'], columns='Element', values='Quantity').reset_index()
            self._meal_search_space_base = full_set
        
        return self._meal_search_space_base

    def _generate_candidate(self, current_state: DataFrame) -> list:  # TODO: This is switching between two meals over and over.
        new_arrays = []
        for meal in self._meal_categories:

            current_meal = current_state[current_state['Meal_Category'] == meal]
            current_meal_id = current_meal['Recipe_Id'].reset_index(drop=True)[0]
            current_vector = current_meal.drop(['Meal_Category', 'Recipe_Id'], axis=1).to_numpy()

            # Exclude current state meal and turn search space df into (n, len(nutrients)) numpy array
            cat_search_space = self.meal_search_space_normalized[self.meal_search_space_normalized['Meal_Category'] == meal]
            cat_search_space = cat_search_space[cat_search_space['Recipe_Id'] != current_meal_id].reset_index(drop=True)
            vectorized_search_space = cat_search_space.drop(['Meal_Category', 'Recipe_Id'], axis=1).to_numpy()

            perturbation = 4.0 * np.random.rand(self.num_valid_nutrients) - 2.0  # Uniform Sampling
            rnd_target = perturbation + current_vector
            #print(rnd_target)
            # Using Manhatten distance since we are in high dimensional space 
            dist = sp.distance.cdist(vectorized_search_space, rnd_target, metric='cityblock')
            closest_distance_in_cat_id = np.argmin(dist, axis=0)[0]

            closest_recipe_in_cat = cat_search_space.iloc[[closest_distance_in_cat_id], :]
            candidate_recipe_id = closest_recipe_in_cat['Recipe_Id'].reset_index(drop=True)[0]
            ph_id = cat_search_space['Recipe_Id'].sample(n=1).reset_index(drop=True)[0]
            new_arrays.append(candidate_recipe_id)
            #new_arrays.append(ph_id)

        return new_arrays


    # TODO: add weights to pct diff values before summing
    def _objective(self, meal_list: list) -> float:
        state_df = self.meal_search_space_base[self.meal_search_space_base['Recipe_Id'].isin(meal_list)]
        state_df = state_df.drop(['Meal_Category', 'Recipe_Id'], axis=1)

        daily_nutr_qtys = pd.DataFrame(state_df.groupby([True]*len(state_df)).sum())        
        daily_nutr_qtys = daily_nutr_qtys.melt(var_name='Element', value_name='Sum_Quantity')

        comparison_df = daily_nutr_qtys.merge(right=self.user_vals_df, right_on=['index'], left_on=['Element'], how='inner')
        comparison_df['pct_difference'] = abs((comparison_df['Quantity'] - comparison_df['Sum_Quantity']) / ((comparison_df['Quantity'] + comparison_df['Sum_Quantity']) / 2))

        energy = comparison_df['pct_difference'].sum()

        return energy

    # TODO: refine/complete simulated annealing algorithm
    def simulated_annealing(self, temp):

        # generate an initial meal set
        current_state = self.meal_search_space_normalized.sample(frac=1).groupby('Meal_Category', sort=False).head(1)
        current_ids = current_state['Recipe_Id'].reset_index(drop=True).tolist()
        # evaluate the initial point
        current_eval = self._objective(current_ids)
        best, best_eval = current_ids, current_eval
        # current working solution
        scores = []
        # run the algorithm
        for i in range(self._n_iter):
            # take a step
            candidate_ids = self._generate_candidate(current_state)
            candidate_state = self.meal_search_space_normalized[self.meal_search_space_normalized['Recipe_Id'].isin(candidate_ids)]
            # evaluate candidate point
            candidate_eval = self._objective(candidate_ids)
            
            # check for new best solution
            if candidate_eval < current_eval:
                # store new best point
                best, best_eval = candidate_ids, candidate_eval
                scores.append(best_eval)
                # report progress
                # print('>%d f(%s) = %.5f' % (i, best, best_eval))
            # difference between candidate and current point evaluation
            diff = candidate_eval - current_eval
            # calculate temperature for current epoch
            t = temp / float(i + 1)
            # calculate metropolis acceptance criterion
            metropolis = exp(-diff / t)
            # check if we should keep the new point
            if diff < 0 or rand() < metropolis:
                # store the new current point
                current_state, current_eval = candidate_state, candidate_eval
        return [best, best_eval, scores]

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

    test_plan = DailyPlanGenerator(db_connection=test_connect,
                                    user_nutrition_targets=test_guy,
                                    num_iterations=2000)

    seed(1)
    temps = [200, 100, 50, 25]
    for tmp in temps:
        best, score, scores = test_plan.simulated_annealing(temp=tmp)
        print('f(%s) = %f' % (best, score))
        pyplot.plot(scores, '.-')
        pyplot.xlabel('Improvement Number')
        pyplot.ylabel('Evaluation f(x)')
        pyplot.show()

"""     ind0 = test_plan.meal_search_space_normalized
    current_state = ind0[ind0['Recipe_Id'].isin([16239, 223042, 16895])]
    candidates = test_plan._generate_candidate(current_state)
    candidate_df = ind0[ind0['Recipe_Id'].isin(candidates)]
    #print(rand_v)
    obj = test_plan._objective(meal_list=candidates)
    print(ind0) """
