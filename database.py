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
    'host': os.environ.get('DB_HOST', 'db'),
    'user': os.environ.get('DB_USER', 'plotapp'),
    'password': os.environ.get('DB_PASSWORD', 'plotapp123'),
    'database': os.environ.get('DB_NAME', 'plotpalette-mydb'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'autocommit': True,
    'raise_on_warnings': True,
    'connection_timeout': 10,
    'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'
}

# Optional Cloud SQL Unix socket support
DB_UNIX_SOCKET = os.environ.get('DB_UNIX_SOCKET')  # e.g., /cloudsql/project:region:instance

class DatabaseManager:
    def __init__(self):
        self.config = DB_CONFIG
        self._connection = None

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = None
        try:
            connect_args = dict(self.config)
            # Use Unix socket if provided (Cloud SQL Connector on Cloud Run)
            if DB_UNIX_SOCKET:
                connect_args['unix_socket'] = DB_UNIX_SOCKET
                # When using socket, host may be omitted; keep user/password/db/port
            connection = mysql.connector.connect(**connect_args)
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
                
                required_tables = ['user_info', 'user_session', 'palette_analyse', 'painting_recommendations', 
                                 'emotion_selection', 'paintings_style', 'feedback_form']
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
        """Create the seven required database tables without id columns"""
        
        # Table 1: user_info (User Demographics) - username as PRIMARY KEY
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_info (
                username VARCHAR(255) PRIMARY KEY,
                age VARCHAR(255),
                gender VARCHAR(255),
                fieldOfStudy VARCHAR(255),
                frequency VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Table 2: user_session (Session Management) - session_id as PRIMARY KEY
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_session (
                session_id VARCHAR(255) PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_username (username),
                INDEX idx_created_at (created_at),
                FOREIGN KEY (username) REFERENCES user_info(username) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Table 3: palette_analyse (Emotion Analysis Results) - session_id as PRIMARY KEY
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS palette_analyse (
                session_id VARCHAR(255) PRIMARY KEY,
                gifname VARCHAR(255),
                anger DECIMAL(5,4),
                anticipation DECIMAL(5,4),
                arrogance DECIMAL(5,4),
                disagreeableness DECIMAL(5,4),
                disgust DECIMAL(5,4),
                fear DECIMAL(5,4),
                gratitude DECIMAL(5,4),
                happiness DECIMAL(5,4),
                humility DECIMAL(5,4),
                love DECIMAL(5,4),
                optimism DECIMAL(5,4),
                pessimism DECIMAL(5,4),
                sadness DECIMAL(5,4),
                surprise DECIMAL(5,4),
                trust DECIMAL(5,4),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_created_at (created_at),
                FOREIGN KEY (session_id) REFERENCES user_session(session_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Table 4: painting_recommendations (Recommended Painting URLs) - session_id as PRIMARY KEY
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS painting_recommendations (
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Table 5: emotion_selection (User's Selected Emotion) - session_id as PRIMARY KEY
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emotion_selection (
                session_id VARCHAR(255) PRIMARY KEY,
                selected_emotion VARCHAR(100),
                probability DECIMAL(5,4),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_created_at (created_at),
                FOREIGN KEY (session_id) REFERENCES user_session(session_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Table 6: paintings_style (User's Selected Paintings and Character) - session_id as PRIMARY KEY
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paintings_style (
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Table 7: feedback_form (User Feedback) - session_id as PRIMARY KEY
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback_form (
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

    # Table 1: user_info management
    def save_user_info(self, username: str, age: str = None, gender: str = None, 
                      fieldOfStudy: str = None, frequency: str = None) -> bool:
        """Save or update user info in the database"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                
                # Check if user exists
                cursor.execute("SELECT username FROM user_info WHERE username = %s", (username,))
                existing_user = cursor.fetchone()
                
                if existing_user:
                    # Update existing user
                    cursor.execute("""
                        UPDATE user_info SET 
                        age = COALESCE(%s, age),
                        gender = COALESCE(%s, gender),
                        fieldOfStudy = COALESCE(%s, fieldOfStudy),
                        frequency = COALESCE(%s, frequency),
                        updated_at = CURRENT_TIMESTAMP
                        WHERE username = %s
                    """, (age, gender, fieldOfStudy, frequency, username))
                    return True
                else:
                    # Insert new user
                    cursor.execute("""
                        INSERT INTO user_info (username, age, gender, fieldOfStudy, frequency)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (username, age, gender, fieldOfStudy, frequency))
                    return True
                    
        except Error as e:
            logger.error(f"Error saving user info: {e}")
            raise

    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user info by username"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM user_info WHERE username = %s", (username,))
                return cursor.fetchone()
        except Error as e:
            logger.error(f"Error getting user info: {e}")
            raise

    def check_username_exists(self, username: str) -> bool:
        """Check if a username exists in the database"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM user_info WHERE username = %s", (username,))
                count = cursor.fetchone()[0]
                return count > 0
        except Error as e:
            logger.error(f"Error checking username existence: {e}")
            raise

    # Table 2: user_session management
    def create_session(self, username: str, session_id: str) -> bool:
        """Create a new session for a user"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                
                cursor.execute("""
                    INSERT INTO user_session (session_id, username)
                    VALUES (%s, %s)
                """, (session_id, username))
                return True
                    
        except Error as e:
            logger.error(f"Error creating session: {e}")
            raise

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by session_id"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM user_session WHERE session_id = %s", (session_id,))
                return cursor.fetchone()
        except Error as e:
            logger.error(f"Error getting session: {e}")
            raise

    # Table 3: palette_analyse management
    def save_palette_analyse(self, session_id: str, gifname: str = None, emotion_scores: Dict[str, float] = None) -> bool:
        """Save palette analysis results to the database"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                
                # Debug logging
                logger.info(f"💾 Saving palette analysis for session: {session_id}")
                logger.info(f"💾 GIF name: {gifname}")
                logger.info(f"💾 Raw emotion scores: {emotion_scores}")
                
                # Prepare emotion scores with default values and validation
                emotions = {}
                for emotion_name in ['anger', 'anticipation', 'arrogance', 'disagreeableness', 
                                   'disgust', 'fear', 'gratitude', 'happiness', 'humility', 
                                   'love', 'optimism', 'pessimism', 'sadness', 'surprise', 'trust']:
                    
                    raw_value = emotion_scores.get(emotion_name) if emotion_scores else None
                    
                    if raw_value is not None:
                        # Ensure value is a float and within valid DECIMAL(10,8) range
                        try:
                            float_value = float(raw_value)
                            # DECIMAL(10,8) can handle values from -99.99999999 to 99.99999999
                            # For probabilities, ensure they're between 0 and 1
                            validated_value = max(0.0, min(1.0, float_value))
                            
                            # Round to 8 decimal places to fit DECIMAL(10,8)
                            emotions[emotion_name] = round(validated_value, 8)
                            
                            if abs(float_value - validated_value) > 0.00000001:
                                logger.warning(f"⚠️ Emotion {emotion_name} value clamped: {float_value} -> {validated_value}")
                                
                        except (ValueError, TypeError) as e:
                            logger.error(f"❌ Invalid emotion value for {emotion_name}: {raw_value}, error: {e}")
                            emotions[emotion_name] = None
                    else:
                        emotions[emotion_name] = None
                
                logger.info(f"💾 Processed emotion scores: {emotions}")
                
                # Check if analysis exists for this session
                cursor.execute("SELECT session_id FROM palette_analyse WHERE session_id = %s", (session_id,))
                existing_analysis = cursor.fetchone()
                
                if existing_analysis:
                    # Update existing analysis
                    cursor.execute("""
                        UPDATE palette_analyse SET 
                        gifname = COALESCE(%s, gifname),
                        anger = COALESCE(%s, anger),
                        anticipation = COALESCE(%s, anticipation),
                        arrogance = COALESCE(%s, arrogance),
                        disagreeableness = COALESCE(%s, disagreeableness),
                        disgust = COALESCE(%s, disgust),
                        fear = COALESCE(%s, fear),
                        gratitude = COALESCE(%s, gratitude),
                        happiness = COALESCE(%s, happiness),
                        humility = COALESCE(%s, humility),
                        love = COALESCE(%s, love),
                        optimism = COALESCE(%s, optimism),
                        pessimism = COALESCE(%s, pessimism),
                        sadness = COALESCE(%s, sadness),
                        surprise = COALESCE(%s, surprise),
                        trust = COALESCE(%s, trust),
                        updated_at = CURRENT_TIMESTAMP
                        WHERE session_id = %s
                    """, (gifname, emotions['anger'], emotions['anticipation'], emotions['arrogance'],
                         emotions['disagreeableness'], emotions['disgust'], emotions['fear'], emotions['gratitude'],
                         emotions['happiness'], emotions['humility'], emotions['love'], emotions['optimism'],
                         emotions['pessimism'], emotions['sadness'], emotions['surprise'], emotions['trust'], session_id))
                    return True
                else:
                    # Insert new analysis
                    cursor.execute("""
                        INSERT INTO palette_analyse 
                        (session_id, gifname, anger, anticipation, arrogance, disagreeableness, disgust, fear,
                         gratitude, happiness, humility, love, optimism, pessimism, sadness, surprise, trust)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (session_id, gifname, emotions['anger'], emotions['anticipation'], emotions['arrogance'],
                         emotions['disagreeableness'], emotions['disgust'], emotions['fear'], emotions['gratitude'],
                         emotions['happiness'], emotions['humility'], emotions['love'], emotions['optimism'],
                         emotions['pessimism'], emotions['sadness'], emotions['surprise'], emotions['trust']))
                    return True
                    
        except Error as e:
            logger.error(f"Error saving palette analysis: {e}")
            raise

    def get_palette_analyse(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get palette analysis by session ID"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM palette_analyse WHERE session_id = %s", (session_id,))
                return cursor.fetchone()
        except Error as e:
            logger.error(f"Error getting palette analysis: {e}")
            raise

    # Table 4: painting_recommendations management
    def save_painting_recommendations(self, session_id: str, urls: List[str] = None) -> bool:
        """Save painting recommendations to the database"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                
                # Debug logging
                logger.info(f"🎨 Saving painting recommendations for session: {session_id}")
                logger.info(f"🎨 Number of URLs received: {len(urls) if urls else 0}")
                logger.info(f"🎨 URLs: {urls[:5] if urls else None}...")  # Show first 5 URLs
                
                # Pad or truncate list to exactly 10 URLs
                url_list = []
                if urls:
                    url_list = urls[:10]  # Take first 10 URLs
                
                # Pad with None to ensure exactly 10 elements
                while len(url_list) < 10:
                    url_list.append(None)
                
                logger.info(f"🎨 Processed URL list length: {len(url_list)}")
                
                # Check if recommendations exist for this session
                cursor.execute("SELECT session_id FROM painting_recommendations WHERE session_id = %s", (session_id,))
                existing_recs = cursor.fetchone()
                
                if existing_recs:
                    # Update existing recommendations
                    logger.info(f"🎨 Updating existing recommendations for session: {session_id}")
                    cursor.execute("""
                        UPDATE painting_recommendations SET 
                        url_0 = %s, url_1 = %s, url_2 = %s, url_3 = %s, url_4 = %s,
                        url_5 = %s, url_6 = %s, url_7 = %s, url_8 = %s, url_9 = %s,
                        updated_at = CURRENT_TIMESTAMP
                        WHERE session_id = %s
                    """, url_list + [session_id])
                    logger.info(f"✅ Updated painting recommendations for session: {session_id}")
                    return True
                else:
                    # Insert new recommendations
                    logger.info(f"🎨 Inserting new recommendations for session: {session_id}")
                    cursor.execute("""
                        INSERT INTO painting_recommendations 
                        (session_id, url_0, url_1, url_2, url_3, url_4, url_5, url_6, url_7, url_8, url_9)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [session_id] + url_list)
                    logger.info(f"✅ Inserted painting recommendations for session: {session_id}")
                    return True
                    
        except Error as e:
            logger.error(f"Error saving painting recommendations: {e}")
            raise

    def get_painting_recommendations(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get painting recommendations by session ID"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM painting_recommendations WHERE session_id = %s", (session_id,))
                return cursor.fetchone()
        except Error as e:
            logger.error(f"Error getting painting recommendations: {e}")
            raise

    # Table 5: emotion_selection management
    def save_emotion_selection(self, session_id: str, selected_emotion: str, probability: float = None) -> bool:
        """Save emotion selection to the database"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                
                # Debug logging
                logger.info(f"💾 Saving emotion selection for session: {session_id}")
                logger.info(f"💾 Selected emotion: {selected_emotion}")
                logger.info(f"💾 Raw probability value: {probability} (type: {type(probability)})")
                
                # Validate and process probability
                processed_probability = None
                if probability is not None:
                    try:
                        # Convert to float and validate range for DECIMAL(10,8)
                        float_prob = float(probability)
                        # Ensure it's within valid range (0.0 to 1.0 for probabilities)
                        if 0.0 <= float_prob <= 1.0:
                            processed_probability = round(float_prob, 8)
                        else:
                            logger.warning(f"⚠️ Probability value out of range [0,1]: {float_prob}")
                            processed_probability = max(0.0, min(1.0, float_prob))
                            processed_probability = round(processed_probability, 8)
                        
                        logger.info(f"💾 Processed probability: {processed_probability}")
                        
                    except (ValueError, TypeError) as e:
                        logger.error(f"❌ Invalid probability value: {probability}, error: {e}")
                        processed_probability = None
                
                # Check if emotion selection exists for this session
                cursor.execute("SELECT session_id FROM emotion_selection WHERE session_id = %s", (session_id,))
                existing_selection = cursor.fetchone()
                
                if existing_selection:
                    # Update existing selection
                    logger.info(f"💾 Updating existing emotion selection for session: {session_id}")
                    cursor.execute("""
                        UPDATE emotion_selection SET 
                        selected_emotion = %s,
                        probability = %s,
                        updated_at = CURRENT_TIMESTAMP
                        WHERE session_id = %s
                    """, (selected_emotion, processed_probability, session_id))
                    connection.commit()
                    logger.info(f"✅ Updated emotion selection for session: {session_id}")
                    return True
                else:
                    # Insert new selection
                    logger.info(f"💾 Inserting new emotion selection for session: {session_id}")
                    cursor.execute("""
                        INSERT INTO emotion_selection (session_id, selected_emotion, probability)
                        VALUES (%s, %s, %s)
                    """, (session_id, selected_emotion, processed_probability))
                    connection.commit()
                    logger.info(f"✅ Inserted emotion selection for session: {session_id}")
                    return True
                    
        except Error as e:
            logger.error(f"Error saving emotion selection: {e}")
            raise

    def get_emotion_selection(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get emotion selection by session ID"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM emotion_selection WHERE session_id = %s", (session_id,))
                return cursor.fetchone()
        except Error as e:
            logger.error(f"Error getting emotion selection: {e}")
            raise

    # Table 6: paintings_style management
    def save_paintings_style(self, session_id: str, painting_urls: List[str] = None, 
                            story_character: str = None, nickname: str = None) -> bool:
        """Save paintings style and character selection to the database"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                
                # Pad or truncate list to 3 URLs
                url_list = (painting_urls or [])[:3] + [None] * (3 - len(painting_urls or []))
                
                # Check if paintings style exists for this session
                cursor.execute("SELECT session_id FROM paintings_style WHERE session_id = %s", (session_id,))
                existing_style = cursor.fetchone()
                
                if existing_style:
                    # Update existing style
                    cursor.execute("""
                        UPDATE paintings_style SET 
                        url_0 = COALESCE(%s, url_0),
                        url_1 = COALESCE(%s, url_1),
                        url_2 = COALESCE(%s, url_2),
                        story_character = COALESCE(%s, story_character),
                        nickname = COALESCE(%s, nickname),
                        updated_at = CURRENT_TIMESTAMP
                        WHERE session_id = %s
                    """, (url_list[0], url_list[1], url_list[2], story_character, nickname, session_id))
                    return True
                else:
                    # Insert new style
                    cursor.execute("""
                        INSERT INTO paintings_style 
                        (session_id, url_0, url_1, url_2, story_character, nickname)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (session_id, url_list[0], url_list[1], url_list[2], story_character, nickname))
                    return True
                    
        except Error as e:
            logger.error(f"Error saving paintings style: {e}")
            raise

    def get_paintings_style(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get paintings style by session ID"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM paintings_style WHERE session_id = %s", (session_id,))
                return cursor.fetchone()
        except Error as e:
            logger.error(f"Error getting paintings style: {e}")
            raise

    # Table 7: feedback_form management
    def save_feedback_form(self, session_id: str, feedback_data: Dict[str, Any]) -> bool:
        """Save feedback form to the database"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                
                # Extract feedback values
                q_values = [
                    feedback_data.get('q1'),
                    feedback_data.get('q2'),
                    feedback_data.get('q3'),
                    feedback_data.get('q4'),
                    feedback_data.get('q5'),
                    feedback_data.get('q6'),
                    feedback_data.get('q7'),
                    feedback_data.get('q8'),
                    feedback_data.get('q9'),
                    feedback_data.get('q10'),
                    feedback_data.get('q11'),
                    feedback_data.get('q12'),
                    feedback_data.get('q13'),
                    feedback_data.get('q14'),
                    feedback_data.get('q15')
                ]
                
                # Check if feedback exists for this session
                cursor.execute("SELECT session_id FROM feedback_form WHERE session_id = %s", (session_id,))
                existing_feedback = cursor.fetchone()
                
                if existing_feedback:
                    # Update existing feedback
                    cursor.execute("""
                        UPDATE feedback_form SET 
                        q1 = COALESCE(%s, q1), q2 = COALESCE(%s, q2), q3 = COALESCE(%s, q3),
                        q4 = COALESCE(%s, q4), q5 = COALESCE(%s, q5), q6 = COALESCE(%s, q6),
                        q7 = COALESCE(%s, q7), q8 = COALESCE(%s, q8), q9 = COALESCE(%s, q9),
                        q10 = COALESCE(%s, q10), q11 = COALESCE(%s, q11), q12 = COALESCE(%s, q12),
                        q13 = COALESCE(%s, q13), q14 = COALESCE(%s, q14), q15 = COALESCE(%s, q15),
                        updated_at = CURRENT_TIMESTAMP
                        WHERE session_id = %s
                    """, q_values + [session_id])
                    return True
                else:
                    # Insert new feedback
                    cursor.execute("""
                        INSERT INTO feedback_form 
                        (session_id, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [session_id] + q_values)
                    return True
                    
        except Error as e:
            logger.error(f"Error saving feedback form: {e}")
            raise

    def get_feedback_form(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get feedback form by session ID"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM feedback_form WHERE session_id = %s", (session_id,))
                return cursor.fetchone()
        except Error as e:
            logger.error(f"Error getting feedback form: {e}")
            raise

    # Analytics and reporting
    def get_complete_user_data(self, session_id: str) -> Dict[str, Any]:
        """Get complete user data from all tables joined together"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                cursor.execute("""
                    SELECT 
                        ui.username, ui.age, ui.gender, ui.fieldOfStudy, ui.frequency,
                        us.session_id,
                        pa.gifname, pa.anger, pa.anticipation, pa.arrogance, pa.disagreeableness, pa.disgust,
                        pa.fear, pa.gratitude, pa.happiness, pa.humility, pa.love, pa.optimism,
                        pa.pessimism, pa.sadness, pa.surprise, pa.trust,
                        pr.url_0 as rec_url_0, pr.url_1 as rec_url_1, pr.url_2 as rec_url_2, pr.url_3 as rec_url_3,
                        pr.url_4 as rec_url_4, pr.url_5 as rec_url_5, pr.url_6 as rec_url_6, pr.url_7 as rec_url_7,
                        pr.url_8 as rec_url_8, pr.url_9 as rec_url_9,
                        es.selected_emotion, es.probability,
                        ps.url_0 as style_url_0, ps.url_1 as style_url_1, ps.url_2 as style_url_2,
                        ps.story_character, ps.nickname,
                        ff.q1, ff.q2, ff.q3, ff.q4, ff.q5, ff.q6, ff.q7, ff.q8, ff.q9, ff.q10,
                        ff.q11, ff.q12, ff.q13, ff.q14, ff.q15
                    FROM user_session us
                    LEFT JOIN user_info ui ON us.username = ui.username
                    LEFT JOIN palette_analyse pa ON us.session_id = pa.session_id
                    LEFT JOIN painting_recommendations pr ON us.session_id = pr.session_id
                    LEFT JOIN emotion_selection es ON us.session_id = es.session_id
                    LEFT JOIN paintings_style ps ON us.session_id = ps.session_id
                    LEFT JOIN feedback_form ff ON us.session_id = ff.session_id
                    WHERE us.session_id = %s
                """, (session_id,))
                
                return cursor.fetchone()
                
        except Error as e:
            logger.error(f"Error getting complete user data: {e}")
            raise

    def export_to_csv_format(self, session_id: str = None) -> List[Dict[str, Any]]:
        """Export data in CSV format"""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                
                if session_id:
                    where_clause = "WHERE us.session_id = %s"
                    params = (session_id,)
                else:
                    where_clause = ""
                    params = ()
                
                cursor.execute(f"""
                    SELECT 
                        us.session_id, ui.username, ui.age, ui.gender, ui.fieldOfStudy, ui.frequency,
                        pa.gifname, es.selected_emotion, ps.story_character, ps.nickname,
                        ff.q1, ff.q2, ff.q3, ff.q4, ff.q5, ff.q6, ff.q7, ff.q8, ff.q9, ff.q10,
                        ff.q11, ff.q12, ff.q13, ff.q14, ff.q15,
                        us.created_at
                    FROM user_session us
                    LEFT JOIN user_info ui ON us.username = ui.username
                    LEFT JOIN palette_analyse pa ON us.session_id = pa.session_id
                    LEFT JOIN emotion_selection es ON us.session_id = es.session_id
                    LEFT JOIN paintings_style ps ON us.session_id = ps.session_id
                    LEFT JOIN feedback_form ff ON us.session_id = ff.session_id
                    {where_clause}
                    ORDER BY us.created_at DESC
                """, params)
                
                return cursor.fetchall()
                
        except Error as e:
            logger.error(f"Error exporting CSV data: {e}")
            raise

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

# Wrapper functions for backward compatibility
def health_check() -> bool:
    """Database health check - wrapper function"""
    return db.health_check()

def init_database():
    """Initialize database - wrapper function"""
    return db.init_database()

def get_db_connection():
    """Get database connection - wrapper for compatibility"""
    return mysql.connector.connect(**DB_CONFIG) 