import collections
import six
from Objects.meal_collection import MealCollection
from Objects.batch_meal_collection import BatchMealCollection
from typing import Union

def iterable(arg):
    return (
        isinstance(arg, collections.Iterable)
        and not isinstance(arg, six.string_types)
    )

def format_mealcollection_as_list(col: Union[MealCollection, BatchMealCollection]):
    formatted_data = []

    for meal in col.collection:
        data = meal.meal_info_as_dict
        formatted_data.append(data)
    
    return formatted_data
