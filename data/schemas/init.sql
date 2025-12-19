-- Database Initialization Script for Plot & Palette
-- ===============================================

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS `plotpalette-mydb` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the database
USE `plotpalette-mydb`;

-- Create application user with proper permissions
CREATE USER IF NOT EXISTS 'plotapp'@'%' IDENTIFIED BY 'plotapp123';
GRANT ALL PRIVILEGES ON `plotpalette-mydb`.* TO 'plotapp'@'%';
FLUSH PRIVILEGES;

-- Drop existing tables if they exist (clean up)
DROP TABLE IF EXISTS feedback_form;
DROP TABLE IF EXISTS paintings_style;
DROP TABLE IF EXISTS emotion_selection;
DROP TABLE IF EXISTS painting_recommendations;
DROP TABLE IF EXISTS palette_analyse;
DROP TABLE IF EXISTS user_session;
DROP TABLE IF EXISTS user_info;

-- Table 1: user_info (User Demographics) - username as PRIMARY KEY
CREATE TABLE user_info (
    username VARCHAR(255) PRIMARY KEY,
    age VARCHAR(255),
    gender VARCHAR(255),
    fieldOfStudy VARCHAR(255),
    frequency VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 2: user_session (Session Management) - session_id as PRIMARY KEY
CREATE TABLE user_session (
    session_id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (username) REFERENCES user_info(username) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 3: palette_analyse (Emotion Analysis Results) - session_id as PRIMARY KEY
CREATE TABLE palette_analyse (
    session_id VARCHAR(255) PRIMARY KEY,
    gifname VARCHAR(255),
    anger DECIMAL(10,8),
    anticipation DECIMAL(10,8),
    arrogance DECIMAL(10,8),
    disagreeableness DECIMAL(10,8),
    disgust DECIMAL(10,8),
    fear DECIMAL(10,8),
    gratitude DECIMAL(10,8),
    happiness DECIMAL(10,8),
    humility DECIMAL(10,8),
    love DECIMAL(10,8),
    optimism DECIMAL(10,8),
    pessimism DECIMAL(10,8),
    sadness DECIMAL(10,8),
    surprise DECIMAL(10,8),
    trust DECIMAL(10,8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    FOREIGN KEY (session_id) REFERENCES user_session(session_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 4: painting_recommendations (Recommended Painting URLs) - session_id as PRIMARY KEY
CREATE TABLE painting_recommendations (
    session_id VARCHAR(255) PRIMARY KEY,
    url_0 TEXT,
    url_1 TEXT,
    url_2 TEXT,
    url_3 TEXT,
    url_4 TEXT,
    url_5 TEXT,
    url_6 TEXT,
    url_7 TEXT,
    url_8 TEXT,
    url_9 TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    FOREIGN KEY (session_id) REFERENCES user_session(session_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 5: emotion_selection (User's Selected Emotion) - session_id as PRIMARY KEY
CREATE TABLE emotion_selection (
    session_id VARCHAR(255) PRIMARY KEY,
    selected_emotion VARCHAR(100),
    probability DECIMAL(10,8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    FOREIGN KEY (session_id) REFERENCES user_session(session_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 6: paintings_style (User's Selected Paintings and Character) - session_id as PRIMARY KEY
CREATE TABLE paintings_style (
    session_id VARCHAR(255) PRIMARY KEY,
    url_0 TEXT,
    url_1 TEXT,
    url_2 TEXT,
    story_character VARCHAR(100),
    nickname VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    FOREIGN KEY (session_id) REFERENCES user_session(session_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 7: feedback_form (User Feedback) - session_id as PRIMARY KEY
CREATE TABLE feedback_form (
    session_id VARCHAR(255) PRIMARY KEY,
    q1 INT,
    q2 INT,
    q3 INT,
    q4 INT,
    q5 INT,
    q6 INT,
    q7 INT,
    q8 INT,
    q9 INT,
    q10 INT,
    q11 INT,
    q12 INT,
    q13 INT,
    q14 TEXT,
    q15 TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    FOREIGN KEY (session_id) REFERENCES user_session(session_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SELECT 'Database initialization completed successfully with no-ID 7-table structure' as status; 