-- Migration: Add intensity column to emotion_selections table
-- Created: 2025-12-20
-- Purpose: Replace probability with intensity levels (low, medium, high)

-- Add intensity column to emotion_selections table
ALTER TABLE emotion_selections ADD COLUMN intensity TEXT;

-- Note: We're keeping the probability column for backward compatibility
-- In production, you may want to drop it after migration is complete:
-- ALTER TABLE emotion_selections DROP COLUMN probability;
