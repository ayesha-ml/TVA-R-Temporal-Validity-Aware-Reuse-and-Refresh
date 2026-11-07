import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from src.baselines import BaselineRouters

def run_evaluation(
    benchmark_path: str = "data/hybrid_benchmark.json",
    rates_path: str = "data/calibrated_rates.json",
    output_summary_path: str = "data/evaluation_results.json",
    output_detailed_csv_path: str = "data/detailed_benchmark_predictions.csv",
    output_detailed_json_path: str = "data/detailed_benchmark_predictions.json"
) -> Dict[str, Any]:
    
    with open(benchmark_path, "r") as f:
        benchmark_data = json.load(f)
        
    routers = BaselineRouters(rates_file_path=rates_path)
    
    results = []
    
    for record in benchmark_data:
        age_hours = float(record["elapsed_age_hours"])
        volatility = str(record["volatility_tier"])
        ground_truth = str(record["ground_truth_action"])
        confidence = float(record.get("confidence_score", 0.85))
        query_id = record.get("trajectory_id", record.get("id", "N/A"))
        
        # evaluate record across all 5 strategies
        decisions = routers.evaluate_record(
            age_hours=age_hours,
            volatility_tier=volatility,
            confidence_score=confidence
        )
        
        entry = {
            "query_id": query_id,
            "volatility_tier": volatility,
            "elapsed_age_hours": age_hours,
            "ground_truth_action": ground_truth,
            "empirical_confidence": confidence
        }
        
        for strategy_name, action in decisions.items():
            entry[f"{strategy_name}_action"] = action
            entry[f"{strategy_name}_correct"] = (action == ground_truth)
            
        results.append(entry)
        
    df_res = pd.DataFrame(results)
    
    # Save granular itemized predictions across all 3,630 records
    df_res.to_csv(output_detailed_csv_path, index=False)
    with open(output_detailed_json_path, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Saved detailed predictions for all {len(df_res)} records to:")
    print(f" - {output_detailed_csv_path}")
    print(f" - {output_detailed_json_path}")
    
    # Summary calculation across overall and volatility tiers
    strategies = ["Always_Refresh", "Always_Reuse", "Uncertainty_Gating", "Raw_Time_Gap", "TVA_R_Proposed"]
    tiers = ["overall", "fast", "slow", "static"]
    summary_metrics = {}
    
    for tier in tiers:
        sub_df = df_res if tier == "overall" else df_res[df_res["volatility_tier"] == tier]
        tier_summary = {"total_samples": len(sub_df)}
        
        for strat in strategies:
            acc = float(sub_df[f"{strat}_correct"].mean()) * 100.0
            tool_calls = int((sub_df[f"{strat}_action"] == "REFRESH").sum())
            tool_reduction = (1.0 - (tool_calls / len(sub_df))) * 100.0 if len(sub_df) > 0 else 0.0
            
            tp = int(((sub_df[f"{strat}_action"] == "REFRESH") & (sub_df["ground_truth_action"] == "REFRESH")).sum())
            fp = int(((sub_df[f"{strat}_action"] == "REFRESH") & (sub_df["ground_truth_action"] == "REUSE")).sum())
            fn = int(((sub_df[f"{strat}_action"] == "REUSE") & (sub_df["ground_truth_action"] == "REFRESH")).sum())
            
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
        
    with open(output_summary_path, "w") as f:
        json.dump(summary_metrics, f, indent=2)
        
    return summary_metrics

if __name__ == "__main__":
    metrics = run_evaluation()
    print("Multi-tier evaluation complete!")
