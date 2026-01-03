CREATE TABLE IF NOT EXISTS working_blocks (
    id TEXT PRIMARY KEY,

    project_id TEXT NOT NULL,

    method_name TEXT NOT NULL,
    status TEXT NOT NULL,

    polling_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,

    priority INTEGER,
    prev_ids TEXT,

    output_path TEXT,
    accumulated_duration_sec REAL DEFAULT 0.0,

    block_id TEXT,
    action_index INTEGER,

    config_json TEXT,
    result_json TEXT,

    create_time REAL,
    last_scheduled_at REAL
);

CREATE INDEX IF NOT EXISTS idx_wb_project
    ON working_blocks (project_id);

CREATE INDEX IF NOT EXISTS idx_wb_status
    ON working_blocks (status);

CREATE INDEX IF NOT EXISTS idx_wb_project_status_priority
    ON working_blocks (project_id, status, priority);

CREATE INDEX IF NOT EXISTS idx_wb_dedup
    ON working_blocks (project_id, block_id, action_index, method_name);
