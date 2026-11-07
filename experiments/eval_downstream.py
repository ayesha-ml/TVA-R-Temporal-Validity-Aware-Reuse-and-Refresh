import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List

def run_downstream_eval(
    benchmark_path: str = "data/hybrid_benchmark.json",
    sample_size_per_tier: int = 50,
    seed: int = 42
):
    np.random.seed(seed)
    
    with open(benchmark_path, "r") as f:
        data = json.load(f)
        
    df = pd.DataFrame(data)
    
    # Stratified sampling: 50 fast, 50 slow, 50 static (N=150 total)
    sampled_dfs = []
    for tier in ["fast", "slow", "static"]:
        tier_df = df[df["volatility_tier"] == tier]
        n_sample = min(len(tier_df), sample_size_per_tier)
        sampled_dfs.append(tier_df.sample(n=n_sample, random_state=seed))
        
    eval_sample = pd.concat(sampled_dfs).reset_index(drop=True)
    print(f"--- DOWNSTREAM EVALUATION SETUP ---")
    print(f"Stratified evaluation sample created: {len(eval_sample)} records (50 per tier).\n")
    
    results = []
    strategies = ["Always_Refresh", "Always_Reuse", "Uncertainty_Gating", "Raw_Time_Gap", "TVA_R_Proposed"]
    
    for idx, row in eval_sample.iterrows():
        gt = row["ground_truth_action"]
        tier = row["volatility_tier"]
        age = float(row["elapsed_age_hours"])
        conf = float(row.get("confidence_score", 0.85))
        
        for strat in strategies:
            # Routing decision rule per strategy
            if strat == "Always_Refresh":
                action = "REFRESH"
            elif strat == "Always_Reuse":
                action = "REUSE"
            elif strat == "Uncertainty_Gating":
                action = "REFRESH" if conf < 0.70 else "REUSE"
            elif strat == "Raw_Time_Gap":
                action = "REFRESH" if age > 24.0 else "REUSE"
            elif strat == "TVA_R_Proposed":
                if tier == "fast":
                    v_t = np.exp(-0.011166 * age)
                elif tier == "slow":
                    v_t = np.exp(-0.005228 * age)
                else:
                    v_t = 1.0
                action = "REFRESH" if v_t < 0.97 else "REUSE"
                
            # Downstream Task Outcome Simulation:
            # 1. REFRESH: Tool fetches live context -> ~95% answer accuracy
            # 2. REUSE on Valid Context: Cached data is fresh -> ~95% answer accuracy
            # 3. REUSE on Stale Context: Cached data expired -> ~15% answer accuracy (hallucination)
            if action == "REFRESH":
                ans_correct = True if np.random.rand() < 0.95 else False
            else:
                if gt == "REUSE":
                    ans_correct = True if np.random.rand() < 0.95 else False
                else:
                    ans_correct = True if np.random.rand() < 0.15 else False
                    
            results.append({
                "id": row.get("trajectory_id", str(idx)),
                "tier": tier,
                "strategy": strat,
                "action": action,
                "downstream_correct": ans_correct
            })
            
    df_res = pd.DataFrame(results)
    
    summary = df_res.groupby("strategy")["downstream_correct"].mean() * 100.0
    print("--- DOWNSTREAM ACCURACY SUMMARY (N=150 Stratified Sample) ---")
    for strat, acc in summary.items():
        print(f"{strat:22s}: {acc:.2f}%")
        
    # Save downstream results artifact
    df_res.to_csv("data/downstream_eval_sample.csv", index=False)
    print("\nSaved detailed downstream sample predictions to data/downstream_eval_sample.csv")

if __name__ == "__main__":
    run_downstream_eval()
