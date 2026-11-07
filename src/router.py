import json
import numpy as np
from src.survival import SurvivalEngine

class TVARouter:
    def __init__(self, c_tool: float = 0.03, c_stale: float = 1.0, rates_file_path: str = "data/calibrated_rates.json"):
        self.c_tool = c_tool
        self.c_stale = c_stale
        self.tau = 1.0 - (self.c_tool / self.c_stale)
        self.engine = SurvivalEngine(rates_file_path=rates_file_path)

    def route(self, age_hours: float, volatility_tier: str) -> str:
        validity = self.engine.compute_validity(age_hours, volatility_tier)
        return "REFRESH" if validity < self.tau else "REUSE"

    def evaluate_record(self, age_hours: float, volatility_tier: str) -> str:
        return self.route(age_hours, volatility_tier)
