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

-- Create palettes table
CREATE TABLE IF NOT EXISTS palettes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    colors TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_filename (filename),
    INDEX idx_created_at (created_at)
);

-- Create stories table
CREATE TABLE IF NOT EXISTS stories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    palette_id INT,
    user_name VARCHAR(100),
    emotion VARCHAR(50),
    narrative_style VARCHAR(50),
    story_text TEXT,
    word_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (palette_id) REFERENCES palettes(id) ON DELETE CASCADE,
    INDEX idx_palette_id (palette_id),
    INDEX idx_emotion (emotion),
    INDEX idx_created_at (created_at)
);

-- Create recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    palette_id INT,
    painting_url VARCHAR(500),
    artist VARCHAR(200),
    title VARCHAR(300),
    year VARCHAR(10),
    confidence_score DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (palette_id) REFERENCES palettes(id) ON DELETE CASCADE,
    INDEX idx_palette_id (palette_id),
    INDEX idx_artist (artist),
    INDEX idx_created_at (created_at)
);

-- Create emotion_predictions table
CREATE TABLE IF NOT EXISTS emotion_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    palette_id INT,
    emotion VARCHAR(50),
    confidence DECIMAL(5,4),
    all_probabilities JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (palette_id) REFERENCES palettes(id) ON DELETE CASCADE,
    INDEX idx_palette_id (palette_id),
    INDEX idx_emotion (emotion),
    INDEX idx_created_at (created_at)
);

-- Insert sample data for testing
INSERT IGNORE INTO palettes (filename, colors) VALUES 
('sample-palette.png', '["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]');

SELECT 'Database initialization completed successfully' as status; 