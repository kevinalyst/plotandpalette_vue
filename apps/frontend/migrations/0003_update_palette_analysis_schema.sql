-- Migration: 0003_update_palette_analysis_schema
-- Date: 2025-12-21
-- Description: Update palette_analysis table to use job_id instead of session_id
--              and rename columns to match n8n response format
-- 
-- THIS MIGRATION WAS APPLIED MANUALLY VIA D1 STUDIO ON 2025-12-21
-- This file documents the changes for future reference

-- Changes made:
-- 1. Changed PRIMARY KEY from session_id to job_id
-- 2. Renamed gif_name → filename
-- 3. Renamed emotion_scores → emotion_intensity
-- 4. Columns now match n8n PALETTE_ANALYSIS response format

-- New schema (for reference):
-- CREATE TABLE palette_analysis (
--   job_id TEXT PRIMARY KEY,
--   filename TEXT,
--   colour_data TEXT,          -- JSON: {purple: 0.1, pink: 0.25, ...}
--   raw_colors TEXT,           -- JSON: {"#8b54b5": 0.1027, "#ffc0cb": 0.2515, ...}
--   emotion_intensity TEXT,    -- JSON: {happiness: "high", love: "medium", ...}
--   created_at TEXT NOT NULL DEFAULT (datetime('now')),
--   updated_at TEXT NOT NULL DEFAULT (datetime('now')),
--   FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
-- );

-- Note: The actual table modification was done manually via D1 Studio
--       This file serves as documentation only
