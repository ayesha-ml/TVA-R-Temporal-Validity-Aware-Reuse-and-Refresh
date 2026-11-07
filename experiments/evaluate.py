import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from src.baselines import BaselineRouters

def run_evaluation(
    benchmark_path: str = "data/hybrid_benchmark.json",
    rates_path: str = "data/calibrated_rates.json",
    output_path: str = "data/evaluation_results.json"
) -> Dict[str, Any]:
    
    with open(benchmark_path, "r") as f:
        benchmark_data = json.load(f)
        
    routers = BaselineRouters(rates_file_path=rates_path)
    
    results = []
    
    for record in benchmark_data:
        age_hours = float(record["elapsed_age_hours"])
        volatility = str(record["volatility_tier"])
        ground_truth = str(record["ground_truth_action"])
        
        # STRICT empirical token log-prob confidence score
        confidence = float(record["confidence_score"])
        
        decisions = routers.evaluate_record(
            age_hours=age_hours,
            volatility_tier=volatility,
            confidence_score=confidence
        )
        
        entry = {
            "query_id": record.get("trajectory_id", record.get("id", "N/A")),
            "volatility_tier": volatility,
            "elapsed_age_hours": age_hours,
            "ground_truth": ground_truth,
            "empirical_confidence": confidence
        }
        
        for strategy_name, action in decisions.items():
            entry[f"{strategy_name}_action"] = action
            entry[f"{strategy_name}_correct"] = (action == ground_truth)
            
        results.append(entry)
        
    df_res = pd.DataFrame(results)
    
    strategies = ["Always_Refresh", "Always_Reuse", "Uncertainty_Gating", "Raw_Time_Gap", "TVA_R_Proposed"]
    tiers = ["overall", "fast", "slow", "static"]
    
    summary_metrics = {}
    
    for tier in tiers:
        if tier == "overall":
            sub_df = df_res
        else:
            sub_df = df_res[df_res["volatility_tier"] == tier]
            
        tier_summary = {"total_samples": len(sub_df)}
        
        for strat in strategies:
            acc = float(sub_df[f"{strat}_correct"].mean()) * 100.0
            tool_calls = int((sub_df[f"{strat}_action"] == "REFRESH").sum())
            tool_reduction = (1.0 - (tool_calls / len(sub_df))) * 100.0 if len(sub_df) > 0 else 0.0
            
            tp = int(((sub_df[f"{strat}_action"] == "REFRESH") & (sub_df["ground_truth"] == "REFRESH")).sum())
            fp = int(((sub_df[f"{strat}_action"] == "REFRESH") & (sub_df["ground_truth"] == "REUSE")).sum())
            fn = int(((sub_df[f"{strat}_action"] == "REUSE") & (sub_df["ground_truth"] == "REFRESH")).sum())
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            tier_summary[strat] = {
                "accuracy": round(acc, 2),
                "tool_reduction_pct": round(tool_reduction, 2),
                "refresh_f1": round(f1, 4),
                "refresh_calls": tool_calls
            }
            
        summary_metrics[tier] = tier_summary
        
    with open(output_path, "w") as f:
        json.dump(summary_metrics, f, indent=2)
        
    return summary_metrics

if __name__ == "__main__":
    metrics = run_evaluation()
    print("empirical evaluation complete!")
