from typing import Dict, Any, List
from src.router import TVARouter

class BaselineRouters:
    # initializing baseline decision modules for benchmarking
    def __init__(
        self,
        rates_file_path: str = "data/calibrated_rates.json",
        c_tool: float = 0.03,
        c_stale: float = 1.0,
        fixed_time_threshold_hours: float = 72.0,
        uncertainty_threshold: float = 0.70
    ):
        self.tva_router = TVARouter(rates_file_path=rates_file_path, c_tool=c_tool, c_stale=c_stale)
        self.fixed_time_threshold_hours = fixed_time_threshold_hours
        self.uncertainty_threshold = uncertainty_threshold

    # baseline 1: always refresh baseline
    def route_always_refresh(self) -> Dict[str, Any]:
        return {
            "action": "REFRESH",
            "strategy": "Always_Refresh"
        }

    # baseline 2: always reuse baseline
    def route_always_reuse(self) -> Dict[str, Any]:
        return {
            "action": "REUSE",
            "strategy": "Always_Reuse"
        }

    # baseline 3: uncertainty gating
    def route_uncertainty_gating(self, confidence_score: float = 0.85) -> Dict[str, Any]:
        action = "REFRESH" if confidence_score < self.uncertainty_threshold else "REUSE"
        return {
            "action": action,
            "strategy": "Uncertainty_Gating",
            "confidence_score": confidence_score
        }

    # baseline 4: raw time gap gating
    def route_raw_time_gap(self, age_hours: float) -> Dict[str, Any]:
        action = "REFRESH" if age_hours > self.fixed_time_threshold_hours else "REUSE"
        return {
            "action": action,
            "strategy": "Raw_Time_Gap",
            "age_hours": age_hours,
            "threshold_hours": self.fixed_time_threshold_hours
        }

    # proposed method: temporal validity framework (tva-r)
    def route_tva_proposed(self, age_hours: float, volatility_tier: str) -> Dict[str, Any]:
        action = self.tva_router.route(age_hours, volatility_tier)
        return {
            "action": action,
            "strategy": "TVA_R_Proposed"
        }

    # evaluating all 5 routing strategies for single benchmark record
    def evaluate_record(
        self,
        age_hours: float,
        volatility_tier: str,
        confidence_score: float = 0.85
    ) -> Dict[str, str]:
        return {
            "Always_Refresh": self.route_always_refresh()["action"],
            "Always_Reuse": self.route_always_reuse()["action"],
            "Uncertainty_Gating": self.route_uncertainty_gating(confidence_score)["action"],
            "Raw_Time_Gap": self.route_raw_time_gap(age_hours)["action"],
            "TVA_R_Proposed": self.route_tva_proposed(age_hours, volatility_tier)["action"]
        }
