-- Plot & Palette D1 Database Schema
-- Migration: 0001_initial_schema
-- Created: 2024-01-01

-- Users table (demographics)
CREATE TABLE users (
  username TEXT PRIMARY KEY,
  age TEXT,
  gender TEXT,
  field_of_study TEXT,
  frequency TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_users_created_at ON users(created_at);

-- Sessions table (user sessions)
CREATE TABLE sessions (
  session_id TEXT PRIMARY KEY,
  username TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);

CREATE INDEX idx_sessions_username ON sessions(username);
CREATE INDEX idx_sessions_created_at ON sessions(created_at);

-- Assets table (uploaded images, stored in R2)
CREATE TABLE assets (
  asset_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  filename TEXT NOT NULL,
  original_name TEXT,
  content_type TEXT,
  size_bytes INTEGER,
  r2_key TEXT NOT NULL UNIQUE,
  metadata TEXT, -- JSON
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX idx_assets_session_id ON assets(session_id);
CREATE INDEX idx_assets_r2_key ON assets(r2_key);

-- Jobs table (async processing)
CREATE TABLE jobs (
  job_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  type TEXT NOT NULL, -- PALETTE_ANALYSIS, PAINTING_RECOMMENDATION, STORY_GENERATION
  status TEXT NOT NULL DEFAULT 'QUEUED', -- QUEUED, RUNNING, SUCCEEDED, FAILED
  client_request_id TEXT,
  input_data TEXT, -- JSON
  error_message TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  started_at TEXT,
  completed_at TEXT,
  FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX idx_jobs_session_id ON jobs(session_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_type ON jobs(type);
CREATE INDEX idx_jobs_client_request_id ON jobs(client_request_id);
CREATE UNIQUE INDEX idx_jobs_idempotency ON jobs(client_request_id, session_id, type) WHERE client_request_id IS NOT NULL;

-- Job Results table (separate for large results)
CREATE TABLE job_results (
  job_id TEXT PRIMARY KEY,
  result_data TEXT, -- JSON (small results inline)
  r2_result_key TEXT, -- R2 key for large results
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
);

-- Palette Analysis Results
CREATE TABLE palette_analysis (
  session_id TEXT PRIMARY KEY,
  gif_name TEXT,
  colour_data TEXT, -- JSON: {black: 0.5, blue: 0.2, ...}
  raw_colors TEXT, -- JSON: [{hex, percentage}, ...]
  emotion_scores TEXT, -- JSON: {anger: 0.1, happiness: 0.8, ...}
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

-- Painting Recommendations
CREATE TABLE painting_recommendations (
  session_id TEXT PRIMARY KEY,
  recommendations TEXT NOT NULL, -- JSON array of {url, title, artist, year, page}
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

-- Emotion Selections
CREATE TABLE emotion_selections (
  session_id TEXT PRIMARY KEY,
  selected_emotion TEXT NOT NULL,
  probability REAL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

-- Painting Selections
CREATE TABLE painting_selections (
  session_id TEXT PRIMARY KEY,
  selected_paintings TEXT NOT NULL, -- JSON array of {url, title, artist}
  story_character TEXT,
  nickname TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

-- Stories
CREATE TABLE stories (
  session_id TEXT PRIMARY KEY,
  story_title TEXT,
  story_part_1 TEXT,
  story_part_2 TEXT,
  story_part_3 TEXT,
  word_count INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

-- Feedback
CREATE TABLE feedback (
  session_id TEXT PRIMARY KEY,
  q1 INTEGER,
  q2 INTEGER,
  q3 INTEGER,
  q4 INTEGER,
  q5 INTEGER,
  q6 INTEGER,
  q7 INTEGER,
  q8 INTEGER,
  q9 INTEGER,
  q10 INTEGER,
  q11 INTEGER,
  q12 INTEGER,
  q13 INTEGER,
  q14 TEXT,
  q15 TEXT,
  prolific_pid TEXT,
  prolific_study_id TEXT,
  prolific_session_id TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX idx_feedback_prolific ON feedback(prolific_pid);
