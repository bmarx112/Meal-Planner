import sys
sys.path.insert(0, r'C:\Users\bmarx\Coding Projects\Meal Planner')
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