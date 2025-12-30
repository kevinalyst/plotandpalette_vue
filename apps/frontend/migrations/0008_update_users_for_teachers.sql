-- Migration: 0008_update_users_for_teachers
-- Update users table for high school teacher demographic
-- Changes field_of_study to school_name and frequency to years_teaching

-- SQLite doesn't support ALTER COLUMN for rename, so we need to recreate the table
-- Step 1: Create new table with updated column names
CREATE TABLE users_new (
  username TEXT PRIMARY KEY,
  age TEXT,
  gender TEXT,
  school_name TEXT,
  years_teaching TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Step 2: Copy data from old table to new table
INSERT INTO users_new (username, age, gender, school_name, years_teaching, created_at, updated_at)
SELECT username, age, gender, field_of_study, frequency, created_at, updated_at
FROM users;

-- Step 3: Drop old table
DROP TABLE users;

-- Step 4: Rename new table to users
ALTER TABLE users_new RENAME TO users;

-- Step 5: Recreate index
CREATE INDEX idx_users_created_at ON users(created_at);
