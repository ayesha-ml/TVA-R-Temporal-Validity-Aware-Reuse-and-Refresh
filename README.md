# Temporal Validity-Aware Reuse and Refresh (TVA-R)

TVA-R is an empirically calibrated, data-driven Temporal Validity framework for Large Language Model (LLM) tool-calling architectures. It models contextual time-decay to optimize the trade-off between retrieval latency, token/compute costs, and downstream answer accuracy.

TVA-R replaces heuristic raw time windows (such as TicToc) and uncalibrated token-level confidence gating (such as FLARE) with an analytical survival decay model V(t, c) = exp(-lambda_c * t) calibrated via Maximum Likelihood Estimation (MLE).

---

## Key Empirical Findings

1. Failure of Uncertainty Gating (FLARE): Token log-probabilities from open-weights LLMs (Qwen/Qwen2.5-0.5B-Instruct) exhibit high variance on dynamic contexts. Uncertainty gating collapses into near-continuous execution (99.67% tool call rate, achieving only 0.33% tool savings).
2. 100% Static Knowledge Call Suppression: TVA-R identifies immutable/static domain facts (lambda_static = 0.0) and suppresses 100% of redundant tool calls (0 out of 3,183 queries), whereas heuristic time gating (TicToc) wastes 1,061 tool calls on static data (33.33% waste).
3. Pareto Dominance on Dynamic Facts: On rapidly changing contexts (FAST tier), TVA-R achieves an F1 score of 0.8106 and 78.42% accuracy while reducing tool calls by 33.33%.

---

## Mathematical Core and Framework Architecture

### 1. Survival Decay Function
Context validity V(t, c) in [0, 1] decays exponentially over elapsed time t (hours) according to volatility class c in {FAST, SLOW, STATIC}:

V(t, c) = exp(-lambda_c * t)

### 2. Maximum Likelihood Estimation (MLE) Calibration
Decay rates lambda_c are empirically fitted using benchmark trajectory outcomes:

- lambda_fast  : 0.011166 (Half-life = 62.08 hours)
- lambda_slow  : 0.005228 (Half-life = 132.58 hours)
- lambda_static: 0.000000 (Half-life = infinity)

### 3. Expected-Cost Gating Decision
TVA-R computes a calibrated validity threshold tau:

tau = 1.0 - (C_tool / C_stale)

Given relative tool invocation cost C_tool = 0.03 and stale context error penalty C_stale = 1.0, the optimal refresh threshold is tau = 0.97.

Action = REFRESH if V(t, c) < tau else REUSE

---

## Empirical Benchmarks and Multi-Tier Results

Evaluated across N = 3,630 benchmark instances categorized into FAST (N=366), SLOW (N=81), and STATIC (N=3,183) volatility tiers.

### Overall Benchmark Performance (N = 3,630)

| Strategy | Overall Accuracy (%) | Tool Reduction (%) | Refresh F1 | Tool Calls Executed |
| :--- | :---: | :---: | :---: | :---: |
| Always_Refresh | 42.26% | 0.00% | 0.5941 | 3,630 / 3,630 |
| Always_Reuse | 57.74% | 100.00% | 0.0000 | 0 / 3,630 |
| Uncertainty_Gating (FLARE) | 42.48% | 0.33% | 0.5947 | 3,618 / 3,630 |
| Raw_Time_Gap (TicToc) | 83.53% | 66.67% | 0.7821 | 1,210 / 3,630 |
| TVA_R_Proposed | 60.39% | 91.79% | 0.2151 | 298 / 3,630 |

---

## Downstream Task Accuracy vs. Tool Savings

Evaluated on a 150-sample stratified evaluation set (50 FAST, 50 SLOW, 50 STATIC) measuring downstream LLM answer correctness:

- Always_Refresh        : 94.67% (Tool Savings: 0.0%)
- Uncertainty_Gating    : 96.67% (Tool Savings: 0.3%)
- Raw_Time_Gap (TicToc) : 95.33% (Tool Savings: 66.7%)
- TVA_R_Proposed        : 84.00% (Tool Savings: 91.8%)
- Always_Reuse          : 62.67% (Tool Savings: 100.0%)

---

## Visualizations and Figures

1. figures/volatility_tier_breakdown.png: Side-by-side bar plots showing routing accuracy and tool call savings across volatility tiers.
2. figures/pareto_frontier.png: Overall Accuracy vs. Tool Call Reduction trade-off plot.

---

---

## Repository Structure

```text
.
├── data/
│   ├── hybrid_benchmark.json          # 3,630 benchmark records + empirical LLM log-probs
│   ├── calibrated_rates.json           # Fitted MLE lambda parameters
│   ├── evaluation_results.json         # Aggregated benchmark summary metrics
│   ├── detailed_benchmark_predictions.csv # Granular prediction rows across all 3,630 records
│   └── downstream_eval_sample.csv      # Stratified 150-sample downstream evaluation artifact
├── src/
│   ├── survival.py                     # Exponential survival decay engine V(t)
│   ├── router.py                       # TVARouter decision engine (C_tool=0.03, Tau=0.97)
│   └── baselines.py                    # Interface wrapper for comparative baselines
├── experiments/
│   ├── compute_confidence.py           # GPU log-prob extractor script (Qwen2.5-0.5B)
│   ├── evaluate.py                     # Multi-tier benchmark evaluation engine
│   ├── eval_downstream.py              # Downstream task correctness evaluation
│   └── plot_results.py                 # Publication figure generator
├── figures/
│   ├── volatility_tier_breakdown.png   # Tier-by-tier comparative figure
│   └── pareto_frontier.png             # Accuracy vs. Tool Savings Pareto plot
└── README.md
```

---

## Quickstart and Reproduction

1. Run Benchmark Evaluation:
   PYTHONPATH=. python experiments/evaluate.py

2. Run Downstream LLM Accuracy Evaluation:
   PYTHONPATH=. python experiments/eval_downstream.py

3. Regenerate Visualizations:
   PYTHONPATH=. python experiments/plot_results.py
