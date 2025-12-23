-- Migration: Create painting_recommendations table
-- Description: Dedicated table for storing painting recommendations by session
-- Date: 2025-12-22

CREATE TABLE IF NOT EXISTS painting_recommendations (
  session_id TEXT PRIMARY KEY,
  recommendations TEXT NOT NULL,  -- JSON array of painting objects
  job_id TEXT,                     -- Reference to source job
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
