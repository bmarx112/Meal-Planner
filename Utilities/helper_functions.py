import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Objects.unit_conversion import CONVERSION_TABLE


def convert_unit(qty: float, bfr: str, afr: str) -> float:
    try:
        scalar_factor = CONVERSION_TABLE[(bfr, afr)]
        return qty * scalar_factor
    except:
        return qty

        
if __name__ == '__main__':
    num = convert_unit(170, 'lb', 'kg')
    print(num)