from typing import Dict, Any
from src.survival import SurvivalEngine

class TVARouter:
    # initializing survival router with cost ratio thresholds
    def __init__(
        self, 
        rates_file_path: str = "data/calibrated_rates.json",
        c_tool: float = 0.2,
        c_stale: float = 1.0
    ):
        self.survival_engine = SurvivalEngine(rates_file_path=rates_file_path)
        self.c_tool = c_tool
        self.c_stale = c_stale
        # threshold tau derived from expected cost minimization
        self.tau = 1.0 - (self.c_tool / self.c_stale)

    # determining routing action reuse vs refresh based on context age and volatility
    def route(self, age_hours: float, volatility_tier: str) -> Dict[str, Any]:
        validity = self.survival_engine.compute_validity(age_hours, volatility_tier)
        
        # gating decision against validity threshold tau
        action = "REFRESH" if validity < self.tau else "REUSE"
        
        return {
            "action": action,
            "validity_score": round(validity, 6),
            "threshold_tau": round(self.tau, 4),
            "age_hours": age_hours,
            "volatility_tier": volatility_tier
        }

# helper function for single evaluation queries
def evaluate_routing(
    age_hours: float, 
    volatility_tier: str, 
    rates_file_path: str = "data/calibrated_rates.json",
    c_tool: float = 0.2,
    c_stale: float = 1.0
) -> Dict[str, Any]:
    router = TVARouter(rates_file_path=rates_file_path, c_tool=c_tool, c_stale=c_stale)
    return router.route(age_hours, volatility_tier)
