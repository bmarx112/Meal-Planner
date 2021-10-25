import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Objects.unit_conversion import CONVERSION_TABLE
import pandas as pd
import numpy as np


def convert_unit(qty: float, bfr: str, afr: str) -> float:
    try:
        scalar_factor = CONVERSION_TABLE[(bfr, afr)]
        return qty * scalar_factor
    except:
        return qty

def cartesian_product(*arrays):
    la = len(arrays)
    dtype = np.result_type(*arrays)
    arr = np.empty([len(a) for a in arrays] + [la], dtype=dtype)
    for i, a in enumerate(np.ix_(*arrays)):
        arr[...,i] = a
    return arr.reshape(-1, la)  

def cartesian_product_generalized(left, right):
    la, lb = len(left), len(right)
    idx = cartesian_product(np.ogrid[:la], np.ogrid[:lb])
    return pd.DataFrame(
        np.column_stack([left.values[idx[:,0]], right.values[idx[:,1]]]))

        
if __name__ == '__main__':
    num = convert_unit(170, 'lb', 'kg')
    print(num)