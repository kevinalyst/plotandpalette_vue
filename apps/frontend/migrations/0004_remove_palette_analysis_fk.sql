-- Migration: 0004_remove_palette_analysis_fk
-- Date: 2025-12-21
-- Description: Remove foreign key constraint from palette_analysis table
--              to avoid SQLITE_CONSTRAINT errors during n8n callbacks
-- 
-- APPLY THIS VIA D1 STUDIO:
-- 1. Go to Cloudflare Dashboard → D1 → plotandplate-db
-- 2. Run this SQL in the Studio console

-- Step 1: Drop the existing table (backs up data first if needed)
DROP TABLE IF EXISTS palette_analysis;

-- Step 2: Recreate table without foreign key constraint
CREATE TABLE palette_analysis (
  job_id TEXT PRIMARY KEY,
  filename TEXT,
  colour_data TEXT,          -- JSON: {purple: 0.1, pink: 0.25, ...}
  raw_colors TEXT,           -- JSON: {"#8b54b5": 0.1027, "#ffc0cb": 0.2515, ...}
  emotion_intensity TEXT,    -- JSON: {happiness: "high", love: "medium", ...}
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Note: This table no longer has FOREIGN KEY constraint
--       This is intentional - palette_analysis is derived data
--       that can be regenerated from job_results if needed
