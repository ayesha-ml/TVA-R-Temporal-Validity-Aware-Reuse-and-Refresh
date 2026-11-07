import json
import math
from typing import Dict, Union, Optional

class SurvivalEngine:
    # loading empirical decay rates from calibrated json artifact
    def __init__(self, rates_file_path: str = "data/calibrated_rates.json"):
        with open(rates_file_path, "r") as f:
            self.calibrated_rates = json.load(f)

    # retrieving empirical decay rate lambda for specific volatility category
    def get_decay_rate(self, category: str) -> float:
        category_clean = category.lower().strip()
        if category_clean in self.calibrated_rates:
            return float(self.calibrated_rates[category_clean]["fitted_lambda"])
        # default fallback to static zero decay rate if category unknown
        return 0.0

    # computing validity score V using exponential survival function
    def compute_validity(self, age_hours: float, category: str) -> float:
        if age_hours <= 0:
            return 1.0
        
        lambda_c = self.get_decay_rate(category)
        if lambda_c == 0.0:
            return 1.0
            
        validity = math.exp(-lambda_c * age_hours)
        return max(0.0, min(1.0, validity))

    # computing half life in hours for given volatility category
    def get_half_life(self, category: str) -> Union[float, str]:
        lambda_c = self.get_decay_rate(category)
        if lambda_c == 0.0:
            return "inf"
        return math.log(2) / lambda_c

# helper function for direct module access
def calculate_validity(age_hours: float, category: str, rates_file: str = "data/calibrated_rates.json") -> float:
    engine = SurvivalEngine(rates_file_path=rates_file)
    return engine.compute_validity(age_hours, category)
