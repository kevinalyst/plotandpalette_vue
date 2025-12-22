-- Migration: 0005_add_cluster_columns
-- Date: 2025-12-22
-- Description: Add cluster columns to palette_analysis table
--              Stores color cluster data from Google Vision API
-- 
-- APPLY THIS VIA D1 STUDIO:
-- Go to Cloudflare Dashboard → D1 → plotandplate-db → Studio
-- Run these ALTER TABLE commands:

ALTER TABLE palette_analysis ADD COLUMN cluster_0 TEXT;
ALTER TABLE palette_analysis ADD COLUMN cluster_1 TEXT;
ALTER TABLE palette_analysis ADD COLUMN cluster_2 TEXT;
ALTER TABLE palette_analysis ADD COLUMN cluster_3 TEXT;
ALTER TABLE palette_analysis ADD COLUMN cluster_4 TEXT;

-- Each cluster column stores JSON with format:
-- {"hex":"#a388f5","rgb":{"r":163,"g":136,"b":245},"pixelFraction":0.14833333}

-- Updated schema (for reference):
-- CREATE TABLE palette_analysis (
--   job_id TEXT PRIMARY KEY,
--   filename TEXT,
--   colour_data TEXT,        -- JSON: {purple: 0.1, pink: 0.25, ...}
--   raw_colors TEXT,         -- JSON: {"#8b54b5": 0.1027, "#ffc0cb": 0.2515, ...}
--   emotion_intensity TEXT,  -- JSON: {happiness: "high", love: "medium", ...}
--   cluster_0 TEXT,          -- JSON: {"hex":"#xxx","rgb":{...},"pixelFraction":0.xx}
--   cluster_1 TEXT,          -- JSON: {"hex":"#xxx","rgb":{...},"pixelFraction":0.xx}
--   cluster_2 TEXT,          -- JSON: {"hex":"#xxx","rgb":{...},"pixelFraction":0.xx}
--   cluster_3 TEXT,          -- JSON: {"hex":"#xxx","rgb":{...},"pixelFraction":0.xx}
--   cluster_4 TEXT,          -- JSON: {"hex":"#xxx","rgb":{...},"pixelFraction":0.xx}
--   created_at TEXT NOT NULL DEFAULT (datetime('now')),
--   updated_at TEXT NOT NULL DEFAULT (datetime('now'))
-- );
