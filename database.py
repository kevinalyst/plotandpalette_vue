#!/usr/bin/env python3

import mysql.connector
from mysql.connector import Error
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', '34.142.53.204'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'Lihanwen1997'),
    'database': os.environ.get('DB_NAME', 'plotpalette-mydb'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'autocommit': True,
    'raise_on_warnings': True,
    'connection_timeout': 10,
    'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'
}

class DatabaseManager:
    def __init__(self):
        self.config = DB_CONFIG
        self._connection = None

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = None
        try:
            connection = mysql.connector.connect(**self.config)
            yield connection
        except Error as e:
            logger.error(f"Database connection error: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()

    def init_database(self):
        """Initialize database tables"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                
                # Check if tables already exist
                cursor.execute("SHOW TABLES")
                existing_tables = [table[0] for table in cursor.fetchall()]
                
                required_tables = ['users', 'palettes', 'recommendations', 'user_selections', 'stories', 'analytics']
                missing_tables = [table for table in required_tables if table not in existing_tables]
                
                if missing_tables:
                    logger.info(f"Creating missing tables: {missing_tables}")
                # Create tables
                self._create_tables(cursor)
                connection.commit()
                    logger.info("Database tables created successfully")
                else:
                    logger.info("All database tables already exist, skipping creation")
                
                logger.info("Database initialized successfully")
                
        except Error as e:
            logger.error(f"Error initializing database: {e}")
            # Don't raise the exception if tables already exist
            if "already exists" in str(e).lower():
                logger.info("Tables already exist, continuing...")
            else:
            raise

    def _create_tables(self, cursor):
        """Create all required database tables"""
        
        # Users table (for session tracking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(255) UNIQUE NOT NULL,
                user_agent TEXT,
                ip_address VARCHAR(45),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_session_id (session_id),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Palettes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS palettes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) UNIQUE NOT NULL,
                original_name VARCHAR(255),
                colors JSON,
                file_size INT,
                session_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSON,
                INDEX idx_filename (filename),
                INDEX idx_session_id (session_id),
                INDEX idx_created_at (created_at),
                FOREIGN KEY (session_id) REFERENCES users(session_id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Recommendations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                palette_id INT,
                session_id VARCHAR(255),
                emotion_predicted VARCHAR(100),
                emotion_confidence DECIMAL(5,4),
                all_emotions JSON,
                color_features JSON,
                recommended_paintings JSON,
                processing_time_ms INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_palette_id (palette_id),
                INDEX idx_session_id (session_id),
                INDEX idx_emotion (emotion_predicted),
                INDEX idx_created_at (created_at),
                FOREIGN KEY (palette_id) REFERENCES palettes(id) ON DELETE CASCADE,
                FOREIGN KEY (session_id) REFERENCES users(session_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # User selections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_selections (
                id INT AUTO_INCREMENT PRIMARY KEY,
                recommendation_id INT,
                session_id VARCHAR(255),
                selected_paintings JSON,
                selection_data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_recommendation_id (recommendation_id),
                INDEX idx_session_id (session_id),
                INDEX idx_created_at (created_at),
                FOREIGN KEY (recommendation_id) REFERENCES recommendations(id) ON DELETE CASCADE,
                FOREIGN KEY (session_id) REFERENCES users(session_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Stories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                selection_id INT,
                session_id VARCHAR(255),
                narrative_style VARCHAR(50),
                user_name VARCHAR(255),
                emotion VARCHAR(100),
                emotion_probability DECIMAL(5,2),
                paintings_data JSON,
                story_content TEXT,
                word_count INT,
                generation_time_ms INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_selection_id (selection_id),
                INDEX idx_session_id (session_id),
                INDEX idx_narrative_style (narrative_style),
                INDEX idx_created_at (created_at),
                FOREIGN KEY (selection_id) REFERENCES user_selections(id) ON DELETE CASCADE,
                FOREIGN KEY (session_id) REFERENCES users(session_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Analytics table for usage tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(255),
                event_type VARCHAR(100),
                event_data JSON,
                ip_address VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_session_id (session_id),
                INDEX idx_event_type (event_type),
                INDEX idx_created_at (created_at),
                FOREIGN KEY (session_id) REFERENCES users(session_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

    # User management
    def create_or_get_user(self, session_id: str, user_agent: str = None, ip_address: str = None) -> Dict[str, Any]:
        """Create or get existing user by session ID"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                # Try to get existing user
                cursor.execute("SELECT * FROM users WHERE session_id = %s", (session_id,))
                user = cursor.fetchone()
                
                if user:
                    # Update last active
                    cursor.execute(
                        "UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE session_id = %s",
                        (session_id,)
                    )
                    return user
                else:
                    # Create new user
                    cursor.execute(
                        "INSERT INTO users (session_id, user_agent, ip_address) VALUES (%s, %s, %s)",
                        (session_id, user_agent, ip_address)
                    )
                    
                    # Return the new user
                    cursor.execute("SELECT * FROM users WHERE session_id = %s", (session_id,))
                    return cursor.fetchone()
                    
        except Error as e:
            logger.error(f"Error creating/getting user: {e}")
            raise

    # Palette management
    def save_palette(self, filename: str, original_name: str, colors: List[str], 
                    file_size: int, session_id: str, metadata: Dict[str, Any] = None) -> int:
        """Save palette to database"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                
                cursor.execute("""
                    INSERT INTO palettes (filename, original_name, colors, file_size, session_id, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (filename, original_name, json.dumps(colors), file_size, session_id, json.dumps(metadata or {})))
                
                return cursor.lastrowid
                
        except Error as e:
            logger.error(f"Error saving palette: {e}")
            raise

    def get_palette(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get palette by filename"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                cursor.execute("SELECT * FROM palettes WHERE filename = %s", (filename,))
                palette = cursor.fetchone()
                
                if palette and palette['colors']:
                    palette['colors'] = json.loads(palette['colors'])
                if palette and palette['metadata']:
                    palette['metadata'] = json.loads(palette['metadata'])
                    
                return palette
                
        except Error as e:
            logger.error(f"Error getting palette: {e}")
            raise

    def get_recent_palettes(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent palettes"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                cursor.execute("""
                    SELECT * FROM palettes 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (limit,))
                
                palettes = cursor.fetchall()
                
                # Parse JSON fields
                for palette in palettes:
                    if palette['colors']:
                        palette['colors'] = json.loads(palette['colors'])
                    if palette['metadata']:
                        palette['metadata'] = json.loads(palette['metadata'])
                
                return palettes
                
        except Error as e:
            logger.error(f"Error getting recent palettes: {e}")
            raise

    # Recommendation management
    def save_recommendation(self, palette_id: int, session_id: str, emotion_data: Dict[str, Any],
                          color_features: Dict[str, Any], recommended_paintings: List[Dict[str, Any]],
                          processing_time_ms: int) -> int:
        """Save recommendation result to database"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                
                cursor.execute("""
                    INSERT INTO recommendations 
                    (palette_id, session_id, emotion_predicted, emotion_confidence, all_emotions, 
                     color_features, recommended_paintings, processing_time_ms)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    palette_id,
                    session_id,
                    emotion_data.get('emotion'),
                    float(emotion_data.get('confidence_percentage', '0%').rstrip('%')) / 100,
                    json.dumps(emotion_data.get('all_probabilities', {})),
                    json.dumps(color_features),
                    json.dumps(recommended_paintings),
                    processing_time_ms
                ))
                
                return cursor.lastrowid
                
        except Error as e:
            logger.error(f"Error saving recommendation: {e}")
            raise

    # Selection management
    def save_selection(self, recommendation_id: int, session_id: str, 
                      selected_paintings: List[Dict[str, Any]], selection_data: Dict[str, Any]) -> int:
        """Save user selection to database"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                
                cursor.execute("""
                    INSERT INTO user_selections (recommendation_id, session_id, selected_paintings, selection_data)
                    VALUES (%s, %s, %s, %s)
                """, (recommendation_id, session_id, json.dumps(selected_paintings), json.dumps(selection_data)))
                
                return cursor.lastrowid
                
        except Error as e:
            logger.error(f"Error saving selection: {e}")
            raise

    # Story management
    def save_story(self, selection_id: int, session_id: str, narrative_style: str,
                  user_name: str, emotion: str, emotion_probability: float,
                  paintings_data: List[Dict[str, Any]], story_content: str,
                  word_count: int, generation_time_ms: int) -> int:
        """Save generated story to database"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                
                cursor.execute("""
                    INSERT INTO stories 
                    (selection_id, session_id, narrative_style, user_name, emotion, emotion_probability,
                     paintings_data, story_content, word_count, generation_time_ms)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    selection_id, session_id, narrative_style, user_name, emotion, emotion_probability,
                    json.dumps(paintings_data), story_content, word_count, generation_time_ms
                ))
                
                return cursor.lastrowid
                
        except Error as e:
            logger.error(f"Error saving story: {e}")
            raise

    # Analytics
    def log_event(self, session_id: str, event_type: str, event_data: Dict[str, Any],
                 ip_address: str = None, user_agent: str = None):
        """Log analytics event"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                
                cursor.execute("""
                    INSERT INTO analytics (session_id, event_type, event_data, ip_address, user_agent)
                    VALUES (%s, %s, %s, %s, %s)
                """, (session_id, event_type, json.dumps(event_data), ip_address, user_agent))
                
        except Error as e:
            logger.error(f"Error logging event: {e}")

    # Health check
    def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()  # Consume the result to avoid "Unread result found" error
                cursor.close()
                return True
        except Error as e:
            logger.error(f"Database health check failed: {e}")
            return False

# Global database instance
db = DatabaseManager() 