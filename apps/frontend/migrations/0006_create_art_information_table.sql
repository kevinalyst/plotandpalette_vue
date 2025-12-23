-- Migration: Create art_information table for Chinese Contemporary Art collection
-- Description: Stores 153 artworks with metadata and color features for recommendation system
-- Date: 2025-12-22

CREATE TABLE IF NOT EXISTS art_information (
  -- Primary identification (matches image filename)
  id INTEGER PRIMARY KEY,
  
  -- Basic metadata
  artist TEXT NOT NULL,
  title TEXT NOT NULL,
  year TEXT NOT NULL,
  
  -- R2 image reference
  r2_key TEXT NOT NULL,
  
  -- Color feature vectors (5 dominant colors for cosine similarity recommendations)
  -- Format: RGB (0-255) + percentage (0.0-1.0)
  color_r_1 REAL DEFAULT 0,
  color_g_1 REAL DEFAULT 0,
  color_b_1 REAL DEFAULT 0,
  color_pct_1 REAL DEFAULT 0,
  
  color_r_2 REAL DEFAULT 0,
  color_g_2 REAL DEFAULT 0,
  color_b_2 REAL DEFAULT 0,
  color_pct_2 REAL DEFAULT 0,
  
  color_r_3 REAL DEFAULT 0,
  color_g_3 REAL DEFAULT 0,
  color_b_3 REAL DEFAULT 0,
  color_pct_3 REAL DEFAULT 0,
  
  color_r_4 REAL DEFAULT 0,
  color_g_4 REAL DEFAULT 0,
  color_b_4 REAL DEFAULT 0,
  color_pct_4 REAL DEFAULT 0,
  
  color_r_5 REAL DEFAULT 0,
  color_g_5 REAL DEFAULT 0,
  color_b_5 REAL DEFAULT 0,
  color_pct_5 REAL DEFAULT 0,
  
  -- Clustering metadata (for future use)
  cluster_id INTEGER DEFAULT 0,
  
  -- Timestamps
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster artist filtering
CREATE INDEX IF NOT EXISTS idx_art_artist ON art_information(artist);

-- Index for cluster-based queries
CREATE INDEX IF NOT EXISTS idx_art_cluster ON art_information(cluster_id);

-- Index for R2 key lookups
CREATE INDEX IF NOT EXISTS idx_art_r2_key ON art_information(r2_key);
