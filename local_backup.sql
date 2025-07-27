-- MySQL dump 10.13  Distrib 8.0.42, for Linux (aarch64)
--
-- Host: localhost    Database: plotpalette-mydb
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `emotion_selection`
--

DROP TABLE IF EXISTS `emotion_selection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `emotion_selection` (
  `session_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `selected_emotion` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `probability` decimal(5,4) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`session_id`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `emotion_selection_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `user_session` (`session_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `emotion_selection`
--

LOCK TABLES `emotion_selection` WRITE;
/*!40000 ALTER TABLE `emotion_selection` DISABLE KEYS */;
/*!40000 ALTER TABLE `emotion_selection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feedback_form`
--

DROP TABLE IF EXISTS `feedback_form`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedback_form` (
  `session_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `q1` int DEFAULT NULL,
  `q2` int DEFAULT NULL,
  `q3` int DEFAULT NULL,
  `q4` int DEFAULT NULL,
  `q5` int DEFAULT NULL,
  `q6` int DEFAULT NULL,
  `q7` int DEFAULT NULL,
  `q8` int DEFAULT NULL,
  `q9` int DEFAULT NULL,
  `q10` int DEFAULT NULL,
  `q11` int DEFAULT NULL,
  `q12` int DEFAULT NULL,
  `q13` int DEFAULT NULL,
  `q14` text COLLATE utf8mb4_unicode_ci,
  `q15` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`session_id`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `feedback_form_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `user_session` (`session_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feedback_form`
--

LOCK TABLES `feedback_form` WRITE;
/*!40000 ALTER TABLE `feedback_form` DISABLE KEYS */;
/*!40000 ALTER TABLE `feedback_form` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `painting_recommendations`
--

DROP TABLE IF EXISTS `painting_recommendations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `painting_recommendations` (
  `session_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `url_0` text COLLATE utf8mb4_unicode_ci,
  `url_1` text COLLATE utf8mb4_unicode_ci,
  `url_2` text COLLATE utf8mb4_unicode_ci,
  `url_3` text COLLATE utf8mb4_unicode_ci,
  `url_4` text COLLATE utf8mb4_unicode_ci,
  `url_5` text COLLATE utf8mb4_unicode_ci,
  `url_6` text COLLATE utf8mb4_unicode_ci,
  `url_7` text COLLATE utf8mb4_unicode_ci,
  `url_8` text COLLATE utf8mb4_unicode_ci,
  `url_9` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`session_id`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `painting_recommendations_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `user_session` (`session_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `painting_recommendations`
--

LOCK TABLES `painting_recommendations` WRITE;
/*!40000 ALTER TABLE `painting_recommendations` DISABLE KEYS */;
/*!40000 ALTER TABLE `painting_recommendations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `paintings_style`
--

DROP TABLE IF EXISTS `paintings_style`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `paintings_style` (
  `session_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `url_0` text COLLATE utf8mb4_unicode_ci,
  `url_1` text COLLATE utf8mb4_unicode_ci,
  `url_2` text COLLATE utf8mb4_unicode_ci,
  `story_character` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nickname` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`session_id`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `paintings_style_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `user_session` (`session_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `paintings_style`
--

LOCK TABLES `paintings_style` WRITE;
/*!40000 ALTER TABLE `paintings_style` DISABLE KEYS */;
/*!40000 ALTER TABLE `paintings_style` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `palette_analyse`
--

DROP TABLE IF EXISTS `palette_analyse`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `palette_analyse` (
  `session_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `gifname` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `anger` decimal(5,4) DEFAULT NULL,
  `anticipation` decimal(5,4) DEFAULT NULL,
  `arrogance` decimal(5,4) DEFAULT NULL,
  `disagreeableness` decimal(5,4) DEFAULT NULL,
  `disgust` decimal(5,4) DEFAULT NULL,
  `fear` decimal(5,4) DEFAULT NULL,
  `gratitude` decimal(5,4) DEFAULT NULL,
  `happiness` decimal(5,4) DEFAULT NULL,
  `humility` decimal(5,4) DEFAULT NULL,
  `love` decimal(5,4) DEFAULT NULL,
  `optimism` decimal(5,4) DEFAULT NULL,
  `pessimism` decimal(5,4) DEFAULT NULL,
  `sadness` decimal(5,4) DEFAULT NULL,
  `surprise` decimal(5,4) DEFAULT NULL,
  `trust` decimal(5,4) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`session_id`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `palette_analyse_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `user_session` (`session_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `palette_analyse`
--

LOCK TABLES `palette_analyse` WRITE;
/*!40000 ALTER TABLE `palette_analyse` DISABLE KEYS */;
INSERT INTO `palette_analyse` VALUES ('94342b90-d084-4ed4-a749-529841dd5343','16.e98b0b1e.gif',0.6733,0.8180,0.4714,0.6231,0.5937,0.3959,0.3882,0.7042,0.8170,0.2982,0.7934,0.3969,0.5800,0.7363,0.7929,'2025-07-26 20:42:17','2025-07-26 20:42:17');
/*!40000 ALTER TABLE `palette_analyse` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_info`
--

DROP TABLE IF EXISTS `user_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_info` (
  `username` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `age` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `gender` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fieldOfStudy` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `frequency` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`username`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_info`
--

LOCK TABLES `user_info` WRITE;
/*!40000 ALTER TABLE `user_info` DISABLE KEYS */;
INSERT INTO `user_info` VALUES ('kevin123','18-24','man','computer-science','few-times-year','2025-07-26 20:41:22','2025-07-26 20:41:22'),('test_user','25','other','Computer Science','weekly','2025-07-26 16:14:45','2025-07-26 16:14:45');
/*!40000 ALTER TABLE `user_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_session`
--

DROP TABLE IF EXISTS `user_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_session` (
  `session_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `username` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`session_id`),
  KEY `idx_username` (`username`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `user_session_ibfk_1` FOREIGN KEY (`username`) REFERENCES `user_info` (`username`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_session`
--

LOCK TABLES `user_session` WRITE;
/*!40000 ALTER TABLE `user_session` DISABLE KEYS */;
INSERT INTO `user_session` VALUES ('00efa149-d3d6-47e6-82e3-0645e5ee71c5','test_user','2025-07-26 16:14:50','2025-07-26 16:14:50'),('94342b90-d084-4ed4-a749-529841dd5343','kevin123','2025-07-26 20:42:07','2025-07-26 20:42:07');
/*!40000 ALTER TABLE `user_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'plotpalette-mydb'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-26 21:27:56
