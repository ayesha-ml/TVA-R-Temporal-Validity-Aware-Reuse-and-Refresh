# Risk-Controlled Temporal Tool Routing: Experimental Audit

## 1. Dataset
- Total source records: 3630
- Primary records after excluding `any`: 3608
- Ambiguous `any` records: 22
- Candidate scenarios: 1210
- Connected meta-scenarios: 1075

## 2. Split sizes
| split       |   records |   candidate_scenarios |   meta_scenarios |
|:------------|----------:|----------------------:|-----------------:|
| train       |      2149 |                   720 |              645 |
| calibration |       726 |                   244 |              215 |
| test        |       733 |                   246 |              215 |

## 3. CRC definition and assumptions
- Unit of calibration: connected meta-scenario.
- Loss: 1 when the human preference is REFRESH and the policy chooses REUSE; otherwise 0.
- Aggregation: row losses are averaged within candidate scenarios, then candidate losses are averaged within connected meta-scenarios.
- Finite-sample correction: (sum of calibration meta-scenario losses + 1) / (number of calibration meta-scenarios + 1).
- Threshold selection: largest grid threshold whose corrected calibration risk is no greater than alpha.
- The loss is weakly non-decreasing in the threshold; flat intervals are allowed.
- The CRC statement depends on exchangeability of calibration and future meta-scenarios and a model fixed independently of calibration labels.
- Connected-component grouping controls observed duplicate-query and specified template links; it does not prove exchangeability or provide arbitrary OOD guarantees.

## 4. Test results
| model          |   threshold |   records |   candidate_scenarios |   meta_scenarios |   missed_refresh_preference_meta_risk |   row_weighted_refresh_rate |   meta_weighted_refresh_rate |   row_weighted_tool_call_reduction |   preference_accuracy |   refresh_precision |   refresh_recall |   refresh_f1 |   alpha | status    |
|:---------------|------------:|----------:|----------------------:|-----------------:|--------------------------------------:|----------------------------:|-----------------------------:|-----------------------------------:|----------------------:|--------------------:|-----------------:|-------------:|--------:|:----------|
| time_only      |        0.38 |       733 |                   246 |              215 |                           0.000387597 |                    0.664393 |                     0.662791 |                           0.335607 |              0.744884 |            0.61807  |         0.996689 |     0.762991 |    0.1  | evaluated |
| time_only      |        0.9  |       733 |                   246 |              215 |                           0.0996124   |                    0.33015  |                     0.327907 |                           0.66985  |              0.839018 |            0.880165 |         0.705298 |     0.783088 |    0.15 | evaluated |
| time_only      |        0.9  |       733 |                   246 |              215 |                           0.0996124   |                    0.33015  |                     0.327907 |                           0.66985  |              0.839018 |            0.880165 |         0.705298 |     0.783088 |    0.2  | evaluated |
| time_only      |        0.9  |       733 |                   246 |              215 |                           0.0996124   |                    0.33015  |                     0.327907 |                           0.66985  |              0.839018 |            0.880165 |         0.705298 |     0.783088 |    0.25 | evaluated |
| text_only      |        0.23 |       733 |                   246 |              215 |                           0.0872093   |                    0.740791 |                     0.72093  |                           0.259209 |              0.499318 |            0.440147 |         0.791391 |     0.56568  |    0.1  | evaluated |
| text_only      |        0.33 |       733 |                   246 |              215 |                           0.134496    |                    0.607094 |                     0.574419 |                           0.392906 |              0.542974 |            0.462921 |         0.682119 |     0.551539 |    0.15 | evaluated |
| text_only      |        0.4  |       733 |                   246 |              215 |                           0.186047    |                    0.473397 |                     0.440698 |                           0.526603 |              0.570259 |            0.481268 |         0.55298  |     0.514638 |    0.2  | evaluated |
| text_only      |        0.51 |       733 |                   246 |              215 |                           0.244574    |                    0.326057 |                     0.287209 |                           0.673943 |              0.600273 |            0.518828 |         0.410596 |     0.45841  |    0.25 | evaluated |
| text_plus_time |        0.47 |       733 |                   246 |              215 |                           0.0817829   |                    0.402456 |                     0.381008 |                           0.597544 |              0.834925 |            0.80678  |         0.788079 |     0.79732  |    0.1  | evaluated |
| text_plus_time |        0.85 |       733 |                   246 |              215 |                           0.132946    |                    0.31105  |                     0.293023 |                           0.68895  |              0.814461 |            0.864035 |         0.652318 |     0.743396 |    0.15 | evaluated |
| text_plus_time |        0.95 |       733 |                   246 |              215 |                           0.186434    |                    0.248295 |                     0.224031 |                           0.751705 |              0.77899  |            0.884615 |         0.533113 |     0.665289 |    0.2  | evaluated |
| text_plus_time |        0.98 |       733 |                   246 |              215 |                           0.226357    |                    0.197817 |                     0.172868 |                           0.802183 |              0.750341 |            0.910345 |         0.437086 |     0.590604 |    0.25 | evaluated |

## 5. Reference baselines and uncalibrated results
| model                            |   threshold |   records |   candidate_scenarios |   meta_scenarios |   missed_refresh_preference_meta_risk |   row_weighted_refresh_rate |   meta_weighted_refresh_rate |   row_weighted_tool_call_reduction |   preference_accuracy |   refresh_precision |   refresh_recall |   refresh_f1 |
|:---------------------------------|------------:|----------:|----------------------:|-----------------:|--------------------------------------:|----------------------------:|-----------------------------:|-----------------------------------:|----------------------:|--------------------:|-----------------:|-------------:|
| always_refresh                   |       nan   |       733 |                   246 |              215 |                           0           |                    1        |                     1        |                           0        |              0.412005 |            0.412005 |         1        |     0.583575 |
| always_reuse                     |       nan   |       733 |                   246 |              215 |                           0.383721    |                    0        |                     0        |                           1        |              0.587995 |            0        |         0        |     0        |
| fixed_ttl_24h                    |        24   |       733 |                   246 |              215 |                           0.000387597 |                    0.664393 |                     0.662791 |                           0.335607 |              0.744884 |            0.61807  |         0.996689 |     0.762991 |
| fixed_ttl_72h                    |        72   |       733 |                   246 |              215 |                           0.0996124   |                    0.33015  |                     0.327907 |                           0.66985  |              0.839018 |            0.880165 |         0.705298 |     0.783088 |
| fixed_ttl_168h                   |       168   |       733 |                   246 |              215 |                           0.0996124   |                    0.33015  |                     0.327907 |                           0.66985  |              0.839018 |            0.880165 |         0.705298 |     0.783088 |
| time_only_uncalibrated_0.50      |         0.5 |       733 |                   246 |              215 |                           0.0996124   |                    0.33015  |                     0.327907 |                           0.66985  |              0.839018 |            0.880165 |         0.705298 |     0.783088 |
| text_only_uncalibrated_0.50      |         0.5 |       733 |                   246 |              215 |                           0.240698    |                    0.334243 |                     0.293023 |                           0.665757 |              0.603001 |            0.522449 |         0.423841 |     0.468007 |
| text_plus_time_uncalibrated_0.50 |         0.5 |       733 |                   246 |              215 |                           0.0833333   |                    0.396999 |                     0.374806 |                           0.603001 |              0.837653 |            0.814433 |         0.784768 |     0.799325 |

## 6. Meta-scenario bootstrap intervals
|   test_meta_scenarios |   risk_ci_low |   risk_ci_high |   meta_refresh_ci_low |   meta_refresh_ci_high | model          |   alpha |
|----------------------:|--------------:|---------------:|----------------------:|-----------------------:|:---------------|--------:|
|                   215 |     0         |     0.00116279 |               0.65969 |               0.665891 | time_only      |     0.1 |
|                   215 |     0.0651163 |     0.112025   |               0.65814 |               0.775581 | text_only      |     0.1 |
|                   215 |     0.0616182 |     0.10156    |               0.35    |               0.410862 | text_plus_time |     0.1 |

## 7. Sensitivity analysis: `any` assigned to REUSE
| model          |   threshold |   records |   candidate_scenarios |   meta_scenarios |   missed_refresh_preference_meta_risk |   row_weighted_refresh_rate |   meta_weighted_refresh_rate |   row_weighted_tool_call_reduction |   preference_accuracy |   refresh_precision |   refresh_recall |   refresh_f1 |   alpha | status    |
|:---------------|------------:|----------:|----------------------:|-----------------:|--------------------------------------:|----------------------------:|-----------------------------:|-----------------------------------:|----------------------:|--------------------:|-----------------:|-------------:|--------:|:----------|
| time_only      |        0.37 |       738 |                   246 |              215 |                           0.000387597 |                    0.666667 |                     0.666667 |                           0.333333 |              0.739837 |            0.611789 |         0.996689 |     0.758186 |     0.1 | evaluated |
| text_only      |        0.23 |       738 |                   246 |              215 |                           0.0872093   |                    0.739837 |                     0.72093  |                           0.260163 |              0.498645 |            0.437729 |         0.791391 |     0.563679 |     0.1 | evaluated |
| text_plus_time |        0.39 |       738 |                   246 |              215 |                           0.0771318   |                    0.424119 |                     0.401938 |                           0.575881 |              0.830623 |            0.782748 |         0.811258 |     0.796748 |     0.1 | evaluated |

## 8. Interpretation and limitations
- The target represents human tool-use preference, not objective factual staleness.
- The reported risk is human-preference refresh-misalignment risk, not factual error rate.
- The benchmark does not establish that refreshing produces a factually more correct answer.
- Bootstrap intervals describe variability in the held-out test estimate; they are not the CRC guarantee.
- The test risk is an empirical held-out result and is not itself guaranteed to be below the selected alpha.
- Risk and refresh rates are weighted at the connected meta-scenario level where explicitly labeled; row-weighted refresh rate is reported separately.

## 9. Reproducibility artifacts
- `crc_calibration_diagnostics.csv`
- `crc_thresholds.json`
- `crc_test_results.csv`
- `baseline_test_results.csv`
- `meta_scenario_bootstrap_intervals.csv`
- `any_as_reuse_sensitivity.csv`
- `test_risk_refresh_frontier.csv`
- `split_assignments.csv`
- `split_metadata.json`
- `experiment_summary.json`
- Trained model files under `models/risk_routing_final/`
- Figures under `figures/risk_routing_final/`