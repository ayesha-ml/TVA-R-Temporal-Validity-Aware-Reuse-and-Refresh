PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS scenarios (
    scenario_id TEXT PRIMARY KEY,
    source_name TEXT,
    source_scenario_id TEXT,
    metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS source_records (
    record_id TEXT PRIMARY KEY,
    scenario_id TEXT NOT NULL,
    source_record_id TEXT,
    query_text TEXT,
    cached_context TEXT,
    elapsed_hours REAL,
    raw_record_json TEXT NOT NULL,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id)
);

CREATE TABLE IF NOT EXISTS preference_labels (
    label_id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id TEXT NOT NULL,
    raw_preference TEXT NOT NULL,
    binary_refresh_preference INTEGER,
    annotation_source TEXT,
    FOREIGN KEY (record_id) REFERENCES source_records(record_id)
);

CREATE TABLE IF NOT EXISTS model_predictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id TEXT NOT NULL,
    experiment_name TEXT NOT NULL,
    refresh_score REAL,
    routing_threshold REAL,
    predicted_action TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (record_id) REFERENCES source_records(record_id)
);

CREATE TABLE IF NOT EXISTS experiment_runs (
    experiment_id TEXT PRIMARY KEY,
    model_name TEXT NOT NULL,
    encoder_name TEXT,
    configuration_json TEXT NOT NULL,
    metrics_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_source_records_scenario
ON source_records(scenario_id);

CREATE INDEX IF NOT EXISTS idx_predictions_experiment
ON model_predictions(experiment_name);
