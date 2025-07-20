#!/usr/bin/env python3
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
from PIL import Image
import colorsys
import math
import os
import glob
import warnings
import joblib
import requests
import json
import re
import sys

# Suppress pandas warnings for cleaner output
warnings.filterwarnings('ignore', category=pd.errors.DtypeWarning)

# Configuration
ORIGINAL_DATA_PATH = "/app/emotions_generation/interpretable_color_features_cleaned.csv"
RESAMPLED_DATA_PATH = "/app/emotions_generation/resampled_emotions_data.csv"
NUM_RECOMMENDATIONS = 10
NUM_FEATURES = 85

# Path to the image file to analyze
IMAGE_PATH = "/app/uploads/1.png"  # This will be replaced by the server

# Emotion model paths
MODEL_PATH = "/app/emotions_generation/final_emotion_model.pkl"
SCALER_PATH = "/app/emotions_generation/final_scaler.pkl"
FEATURE_INFO_PATH = "/app/emotions_generation/final_feature_info.pkl"

# Predefined basic colours with their RGB values
BASIC_COLOURS = {
    'black': (0, 0, 0),
    'blue': (0, 0, 255),
    'brown': (139, 69, 19),
    'green': (0, 128, 0),
    'grey': (128, 128, 128),
    'orange': (255, 165, 0),
    'pink': (255, 192, 203),
    'purple': (128, 0, 128),
    'red': (255, 0, 0),
    'turquoise': (64, 224, 208),
    'white': (255, 255, 255),
    'yellow': (255, 255, 0)
}

# Color feature names (85 features)
COLOR_FEATURES = [
    'black', 'blue', 'brown', 'green', 'grey', 'orange', 'pink', 'purple', 'red', 'turquoise', 'white', 'yellow',
    'red_blue_ratio', 'red_blue_dominance', 'red_green_ratio', 'red_green_dominance', 'red_yellow_ratio', 'red_yellow_dominance',
    'red_purple_ratio', 'red_purple_dominance', 'blue_yellow_ratio', 'blue_yellow_dominance', 'blue_orange_ratio', 'blue_orange_dominance',
    'blue_green_ratio', 'blue_green_dominance', 'blue_purple_ratio', 'blue_purple_dominance', 'yellow_purple_ratio', 'yellow_purple_dominance',
    'yellow_green_ratio', 'yellow_green_dominance', 'yellow_orange_ratio', 'yellow_orange_dominance', 'green_purple_ratio', 'green_purple_dominance',
    'green_orange_ratio', 'green_orange_dominance', 'purple_orange_ratio', 'purple_orange_dominance', 'black_white_ratio', 'black_white_dominance',
    'black_grey_ratio', 'black_grey_dominance', 'black_brown_ratio', 'black_brown_dominance', 'white_grey_ratio', 'white_grey_dominance',
    'white_brown_ratio', 'white_brown_dominance', 'grey_brown_ratio', 'grey_brown_dominance', 'red_orange_ratio', 'red_orange_dominance',
    'orange_yellow_ratio', 'orange_yellow_dominance', 'blue_turquoise_ratio', 'blue_turquoise_dominance', 'green_turquoise_ratio', 'green_turquoise_dominance',
    'purple_pink_ratio', 'purple_pink_dominance', 'red_pink_ratio', 'red_pink_dominance', 'red_green_complementary', 'blue_orange_complementary',
    'yellow_purple_complementary', 'analogous_group_1', 'analogous_group_2', 'analogous_group_3', 'analogous_group_4', 'analogous_group_5',
    'warm_colors_total', 'cool_colors_total', 'neutral_colors_total', 'warm_cool_balance', 'warm_cool_ratio', 'num_dominant_colors',
    'palette_variance', 'primary_dominance', 'color_diversity', 'dominant_is_warm', 'dominant_is_cool', 'dominant_is_neutral', 'color_balance'
]

# --- Emotion Prediction Functions ---

def predict_emotion_via_api(color_features):
    """Predict emotion using local ML model files"""
    try:
        # Convert color features to the format expected by the model
        if hasattr(color_features, "to_dict"):
            features_dict = color_features.to_dict()
        elif hasattr(color_features, "iloc"):
            features_dict = color_features.iloc[0].to_dict()
        else:
            features_dict = color_features
        
        # Handle the case where features_dict might contain nested dictionaries
        if isinstance(features_dict, dict):
            # If it's a dictionary of dictionaries (from pandas DataFrame.to_dict())
            if any(isinstance(v, dict) for v in features_dict.values()):
                # Extract the first row if it's a dict of dicts
                first_key = list(features_dict.keys())[0]
                if isinstance(features_dict[first_key], dict):
                    row_key = list(features_dict[first_key].keys())[0]
                    features_dict = {k: v[row_key] for k, v in features_dict.items()}
        
        # Check if model files exist
        if not all(os.path.exists(path) for path in [MODEL_PATH, SCALER_PATH, FEATURE_INFO_PATH]):
            print("Model files not found, using simple prediction")
            return simple_emotion_prediction(features_dict)
        
        # Load the emotion model files
        print("Loading emotion model files...")
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        feature_info = joblib.load(FEATURE_INFO_PATH)
        
        # Get feature structure from the model info (exact same as emotion_prediction_api.py)
        color_columns = feature_info['color_columns']
        engineered_columns = [col for col in feature_info['final_features'] 
                             if col not in color_columns]
        emotion_columns = feature_info['emotion_columns']
        
        print(f"Model loaded: {len(color_columns)} colors, {len(engineered_columns)} engineered features, {len(emotion_columns)} emotions")
        print(f"Final features from model: {len(feature_info['final_features'])} total")
        
        # Generate full color features from the basic color selection
        full_color_features = create_color_features_from_selection(features_dict)
        
        # Prepare feature vector in the exact order the model expects
        features = []
        
        # Add color features in correct order (as per model training)
        for color in color_columns:
            features.append(float(full_color_features.get(color, 0.0)))
        
        # Add engineered features in correct order (as per model training)
        for feature in engineered_columns:
            # Use calculated engineered features if available, otherwise default to 0.0
            features.append(float(full_color_features.get(feature, 0.0)))
        
        # Verify we have the correct number of features
        expected_features = len(feature_info['final_features'])
        if len(features) != expected_features:
            print(f"Warning: Feature count mismatch! Expected {expected_features}, got {len(features)}")
        else:
            print(f"✅ Feature vector prepared: {len(features)} features (matches model expectation)")
        
        # Debug: Check for missing features
        model_features = set(feature_info['final_features'])
        generated_features = set(full_color_features.keys())
        missing_features = model_features - generated_features
        extra_features = generated_features - model_features
        
        if missing_features:
            print(f"⚠️  Missing features: {missing_features}")
        if extra_features:
            print(f"⚠️  Extra features: {extra_features}")
        
        if not missing_features and not extra_features:
            print(f"✅ All feature names match the model requirements")
        
        # Convert to numpy array and reshape for prediction
        X = np.array(features).reshape(1, -1)
        
        # Scale features
        X_scaled = scaler.transform(X)
        
        # Make prediction (multi-output classifier)
        predictions_proba = model.predict_proba(X_scaled)
        
        # Convert to dictionary with all 15 emotions
        emotion_predictions = {}
        for i, emotion in enumerate(emotion_columns):
            # Get prediction array for this emotion
            pred_array = predictions_proba[i]
            
            # Handle binary classification output - get probability of positive class
            if pred_array.shape[1] > 1:
                # Binary classification - get positive class probability (index 1)
                emotion_predictions[emotion] = float(pred_array[0, 1])
            else:
                # Single value - get the only probability
                emotion_predictions[emotion] = float(pred_array[0, 0])
            
        # Find dominant emotion
        if emotion_predictions:
            dominant_emotion = max(emotion_predictions.items(), key=lambda x: x[1])
            
            # Convert confidence to percentage for display
            confidence_percentage = f"{dominant_emotion[1] * 100:.1f}%"
            
            return {
                "emotion": dominant_emotion[0],
                "confidence": dominant_emotion[1],
                "confidence_percentage": confidence_percentage,
                "all_probabilities": emotion_predictions
            }
        else:
            return simple_emotion_prediction(features_dict)
            
    except Exception as e:
        print("Error in local emotion prediction:", e)
        return simple_emotion_prediction(features_dict)

def simple_emotion_prediction(color_features):
    """Simple emotion prediction based on color features when model fails"""
    try:
        # Convert pandas Series to dictionary if needed
        if hasattr(color_features, 'to_dict'):
            color_features = color_features.to_dict()
        elif hasattr(color_features, 'iloc'):
            # It's a pandas DataFrame, get the first row
            color_features = color_features.iloc[0].to_dict()
        
        # Extract key features for simple prediction
        warm_cool_ratio = float(color_features.get('warm_cool_ratio', 1.0))
        color_balance = float(color_features.get('color_balance', 0.5))
        num_dominant_colors = float(color_features.get('num_dominant_colors', 3))
        
        # Simple rules based on color psychology
        if warm_cool_ratio > 1.5:  # More warm colors
            if color_balance > 0.7:  # Balanced palette
                emotion = 'happiness'
                confidence = 0.75
            else:
                emotion = 'excitement'
                confidence = 0.65
        elif warm_cool_ratio < 0.7:  # More cool colors
            if color_balance > 0.7:
                emotion = 'calmness'
                confidence = 0.70
            else:
                emotion = 'melancholy'
                confidence = 0.60
        else:  # Balanced warm/cool
            if num_dominant_colors > 4:
                emotion = 'curiosity'
                confidence = 0.65
            else:
                emotion = 'contentment'
                confidence = 0.70
        
        return {
            'emotion': emotion,
            'confidence': confidence,
            'all_probabilities': {emotion: confidence}
        }
    except Exception as e:
        print(f"Error in simple emotion prediction: {e}")
        return {
            'emotion': 'neutral',
            'confidence': 0.5,
            'all_probabilities': {'neutral': 0.5}
        }

# --- Colour Extraction Functions ---

def rgb_to_xyz(rgb):
    """Convert RGB to XYZ color space"""
    r, g, b = [x/255.0 for x in rgb]
    
    # Gamma correction
    def gamma_correction(c):
        if c > 0.04045:
            return pow((c + 0.055) / 1.055, 2.4)
        else:
            return c / 12.92
    
    r = gamma_correction(r)
    g = gamma_correction(g)
    b = gamma_correction(b)
    
    # Convert to XYZ (Observer = 2°, Illuminant = D65)
    x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
    
    return (x, y, z)

def xyz_to_lab(xyz):
    """Convert XYZ to LAB color space"""
    x, y, z = xyz
    
    # Normalize for D65 illuminant
    x = x / 0.95047
    y = y / 1.00000
    z = z / 1.08883
    
    def f(t):
        if t > 0.008856:
            return pow(t, 1/3)
        else:
            return (7.787 * t) + (16/116)
    
    fx = f(x)
    fy = f(y)
    fz = f(z)
    
    l = (116 * fy) - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)
    
    return (l, a, b)

def rgb_to_lab(rgb):
    """Convert RGB directly to LAB"""
    xyz = rgb_to_xyz(rgb)
    return xyz_to_lab(xyz)

def ciede2000_distance(rgb1, rgb2):
    """
    Calculate CIEDE2000 color difference between two RGB colors
    """
    # Convert to LAB
    lab1 = rgb_to_lab(rgb1)
    lab2 = rgb_to_lab(rgb2)
    
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    
    # Calculate C and h
    C1 = math.sqrt(a1*a1 + b1*b1)
    C2 = math.sqrt(a2*a2 + b2*b2)
    
    # Calculate mean C
    C_mean = (C1 + C2) / 2
    
    # Calculate G
    G = 0.5 * (1 - math.sqrt(pow(C_mean, 7) / (pow(C_mean, 7) + pow(25, 7))))
    
    # Calculate a'
    a1_prime = a1 * (1 + G)
    a2_prime = a2 * (1 + G)
    
    # Calculate C'
    C1_prime = math.sqrt(a1_prime*a1_prime + b1*b1)
    C2_prime = math.sqrt(a2_prime*a2_prime + b2*b2)
    
    # Calculate h'
    def calc_h_prime(a_prime, b):
        if a_prime == 0 and b == 0:
            return 0
        h = math.atan2(b, a_prime) * 180 / math.pi
        return h if h >= 0 else h + 360
    
    h1_prime = calc_h_prime(a1_prime, b1)
    h2_prime = calc_h_prime(a2_prime, b2)
    
    # Calculate delta values
    delta_L = L2 - L1
    delta_C = C2_prime - C1_prime
    
    # Calculate delta_h
    if C1_prime * C2_prime == 0:
        delta_h_prime = 0
    elif abs(h2_prime - h1_prime) <= 180:
        delta_h_prime = h2_prime - h1_prime
    elif h2_prime - h1_prime > 180:
        delta_h_prime = h2_prime - h1_prime - 360
    else:
        delta_h_prime = h2_prime - h1_prime + 360
    
    delta_H = 2 * math.sqrt(C1_prime * C2_prime) * math.sin(math.radians(delta_h_prime / 2))
    
    # Calculate mean values
    L_mean = (L1 + L2) / 2
    C_mean_prime = (C1_prime + C2_prime) / 2
    
    if C1_prime * C2_prime == 0:
        h_mean_prime = h1_prime + h2_prime
    elif abs(h1_prime - h2_prime) <= 180:
        h_mean_prime = (h1_prime + h2_prime) / 2
    elif abs(h1_prime - h2_prime) > 180 and (h1_prime + h2_prime) < 360:
        h_mean_prime = (h1_prime + h2_prime + 360) / 2
    else:
        h_mean_prime = (h1_prime + h2_prime - 360) / 2
    
    # Calculate T
    T = (1 - 0.17 * math.cos(math.radians(h_mean_prime - 30)) + 
         0.24 * math.cos(math.radians(2 * h_mean_prime)) + 
         0.32 * math.cos(math.radians(3 * h_mean_prime + 6)) - 
         0.20 * math.cos(math.radians(4 * h_mean_prime - 63)))
    
    # Calculate weighting functions
    SL = 1 + ((0.015 * pow(L_mean - 50, 2)) / math.sqrt(20 + pow(L_mean - 50, 2)))
    SC = 1 + 0.045 * C_mean_prime
    SH = 1 + 0.015 * C_mean_prime * T
    
    # Calculate rotation term
    delta_theta = 30 * math.exp(-pow((h_mean_prime - 275) / 25, 2))
    RC = 2 * math.sqrt(pow(C_mean_prime, 7) / (pow(C_mean_prime, 7) + pow(25, 7)))
    RT = -RC * math.sin(2 * math.radians(delta_theta))
    
    # Calculate final CIEDE2000 difference
    kL = kC = kH = 1  # Reference conditions
    
    delta_E = math.sqrt(
        pow(delta_L / (kL * SL), 2) + 
        pow(delta_C / (kC * SC), 2) + 
        pow(delta_H / (kH * SH), 2) + 
        RT * (delta_C / (kC * SC)) * (delta_H / (kH * SH))
    )
    
    return delta_E

def extract_colours_from_image(image_path, n_colours=5):
    """
    Extract dominant colours from an image using k-means clustering
    """
    print(f"Loading image from '{image_path}'...")
    
    try:
        # Load image
        image = Image.open(image_path)
        image = image.convert('RGB')
    except (FileNotFoundError, IOError) as e:
        print(f"Error loading image: {e}")
        print("Please check that the image file exists and is a valid image format.")
        return None, None
    
    # Convert image to numpy array
    image_array = np.array(image)
    
    # Reshape to get all pixels
    pixels = image_array.reshape(-1, 3)
    
    # Remove duplicate pixels to speed up clustering
    unique_pixels = np.unique(pixels, axis=0)
    
    print(f"Image loaded with {len(pixels)} total pixels, {len(unique_pixels)} unique colours")
    
    # Apply k-means clustering
    print(f"Clustering colours into {n_colours} groups...")
    kmeans = KMeans(n_clusters=n_colours, random_state=42, n_init=10)
    kmeans.fit(unique_pixels)
    
    # Get cluster centers (dominant colours)
    dominant_colours = kmeans.cluster_centers_.astype(int)
    
    # Get labels for all pixels to calculate percentages
    all_labels = kmeans.predict(pixels)
    unique_labels, counts = np.unique(all_labels, return_counts=True)
    percentages = counts / len(pixels)
    
    return dominant_colours, percentages

def colour_distance(colour1, colour2):
    """
    Calculate CIEDE2000 distance between two RGB colours
    """
    return ciede2000_distance(colour1, colour2)

def map_to_basic_colours(dominant_colours, percentages):
    """
    Map extracted colours to predefined basic colours using CIEDE2000 distance
    """
    print("Mapping extracted colours to basic colours using CIEDE2000...")
    
    colour_mapping = {}
    
    for i, colour in enumerate(dominant_colours):
        print(f"\nAnalyzing extracted color: RGB{tuple(colour)}")
        
        # Find the closest basic colour using CIEDE2000
        min_distance = float('inf')
        closest_basic_colour = None
        
        # Calculate distances to all basic colors
        distances = []
        for basic_colour_name, basic_colour_rgb in BASIC_COLOURS.items():
            distance = colour_distance(colour, basic_colour_rgb)
            distances.append((basic_colour_name, distance))
        
        # Sort by distance and show top 3 matches
        distances.sort(key=lambda x: x[1])
        print(f"  Top 3 CIEDE2000 matches:")
        for j, (name, dist) in enumerate(distances[:3]):
            print(f"    {j+1}. {name}: {dist:.2f}")
        
        closest_basic_colour = distances[0][0]
        min_distance = distances[0][1]
        
        # Add to mapping (combine percentages if same basic colour is mapped multiple times)
        if closest_basic_colour in colour_mapping:
            colour_mapping[closest_basic_colour] += percentages[i]
        else:
            colour_mapping[closest_basic_colour] = percentages[i]
        
        print(f"  → Mapped to: {closest_basic_colour} (CIEDE2000 distance: {min_distance:.2f}, percentage: {percentages[i]:.4f})")
    
    # Sort by percentage (descending)
    sorted_colours = dict(sorted(colour_mapping.items(), key=lambda x: x[1], reverse=True))
    
    return sorted_colours

def generate_user_colour_selection(image_path):
    """
    Generate user colour selection dictionary from image
    """
    print(f"\n=== Extracting colours from {image_path} ===")
    
    try:
        # Extract dominant colours
        dominant_colours, percentages = extract_colours_from_image(image_path, n_colours=5)
        
        # Check if image loading failed
        if dominant_colours is None or percentages is None:
            print("Failed to extract colours from image. Using fallback colour selection...")
            return {
                'turquoise': 0.2784,
                'pink': 0.2507,
                'blue': 0.2044,
                'yellow': 0.1461,
                'grey': 0.1204
            }
        
        # Display raw extracted colors first
        print(f"\nRaw colors extracted from image:")
        for i, (colour, percentage) in enumerate(zip(dominant_colours, percentages)):
            print(f"  Raw Color {i+1}: RGB({colour[0]}, {colour[1]}, {colour[2]}) - {percentage*100:.2f}%")
        
        # Map to basic colours
        colour_selection = map_to_basic_colours(dominant_colours, percentages)
        
        print(f"\nFinal colour selection:")
        for colour, percentage in colour_selection.items():
            print(f"  {colour}: {percentage:.4f}")
        
        return colour_selection
        
    except Exception as e:
        print(f"Error processing image: {e}")
        print("Using fallback colour selection...")
        return {
            'turquoise': 0.2784,
            'pink': 0.2507,
            'blue': 0.2044,
            'yellow': 0.1461,
            'grey': 0.1204
        }

def create_color_features_from_selection(user_colour_selection):
    """
    Create 85 color features from user color selection
    """
    print("\n=== Creating 85 Color Features from User Selection ===")
    
    # Initialize all features to 0
    features = {feature: 0.0 for feature in COLOR_FEATURES}
    
    # Extract individual color percentages
    black_pct = user_colour_selection.get('black', 0.0)
    blue_pct = user_colour_selection.get('blue', 0.0)
    brown_pct = user_colour_selection.get('brown', 0.0)
    green_pct = user_colour_selection.get('green', 0.0)
    grey_pct = user_colour_selection.get('grey', 0.0)
    orange_pct = user_colour_selection.get('orange', 0.0)
    pink_pct = user_colour_selection.get('pink', 0.0)
    purple_pct = user_colour_selection.get('purple', 0.0)
    red_pct = user_colour_selection.get('red', 0.0)
    turquoise_pct = user_colour_selection.get('turquoise', 0.0)
    white_pct = user_colour_selection.get('white', 0.0)
    yellow_pct = user_colour_selection.get('yellow', 0.0)
    
    # Basic color percentages (12 features)
    features['black'] = black_pct
    features['blue'] = blue_pct
    features['brown'] = brown_pct
    features['green'] = green_pct
    features['grey'] = grey_pct
    features['orange'] = orange_pct
    features['pink'] = pink_pct
    features['purple'] = purple_pct
    features['red'] = red_pct
    features['turquoise'] = turquoise_pct
    features['white'] = white_pct
    features['yellow'] = yellow_pct
    
    # Color ratios (26 features)
    features['red_blue_ratio'] = red_pct / (blue_pct + 0.001)
    features['red_green_ratio'] = red_pct / (green_pct + 0.001)
    features['red_yellow_ratio'] = red_pct / (yellow_pct + 0.001)
    features['red_purple_ratio'] = red_pct / (purple_pct + 0.001)
    features['blue_yellow_ratio'] = blue_pct / (yellow_pct + 0.001)
    features['blue_orange_ratio'] = blue_pct / (orange_pct + 0.001)
    features['blue_green_ratio'] = blue_pct / (green_pct + 0.001)
    features['blue_purple_ratio'] = blue_pct / (purple_pct + 0.001)
    features['yellow_purple_ratio'] = yellow_pct / (purple_pct + 0.001)
    features['yellow_green_ratio'] = yellow_pct / (green_pct + 0.001)
    features['yellow_orange_ratio'] = yellow_pct / (orange_pct + 0.001)
    features['green_purple_ratio'] = green_pct / (purple_pct + 0.001)
    features['green_orange_ratio'] = green_pct / (orange_pct + 0.001)
    features['purple_orange_ratio'] = purple_pct / (orange_pct + 0.001)
    features['black_white_ratio'] = black_pct / (white_pct + 0.001)
    features['black_grey_ratio'] = black_pct / (grey_pct + 0.001)
    features['black_brown_ratio'] = black_pct / (brown_pct + 0.001)
    features['white_grey_ratio'] = white_pct / (grey_pct + 0.001)
    features['white_brown_ratio'] = white_pct / (brown_pct + 0.001)
    features['grey_brown_ratio'] = grey_pct / (brown_pct + 0.001)
    features['red_orange_ratio'] = red_pct / (orange_pct + 0.001)
    features['orange_yellow_ratio'] = orange_pct / (yellow_pct + 0.001)
    features['blue_turquoise_ratio'] = blue_pct / (turquoise_pct + 0.001)
    features['green_turquoise_ratio'] = green_pct / (turquoise_pct + 0.001)
    features['purple_pink_ratio'] = purple_pct / (pink_pct + 0.001)
    features['red_pink_ratio'] = red_pct / (pink_pct + 0.001)
    
    # Color dominance features (26 features)
    features['red_blue_dominance'] = 1.0 if red_pct > blue_pct else 0.0
    features['red_green_dominance'] = 1.0 if red_pct > green_pct else 0.0
    features['red_yellow_dominance'] = 1.0 if red_pct > yellow_pct else 0.0
    features['red_purple_dominance'] = 1.0 if red_pct > purple_pct else 0.0
    features['blue_yellow_dominance'] = 1.0 if blue_pct > yellow_pct else 0.0
    features['blue_orange_dominance'] = 1.0 if blue_pct > orange_pct else 0.0
    features['blue_green_dominance'] = 1.0 if blue_pct > green_pct else 0.0
    features['blue_purple_dominance'] = 1.0 if blue_pct > purple_pct else 0.0
    features['yellow_purple_dominance'] = 1.0 if yellow_pct > purple_pct else 0.0
    features['yellow_green_dominance'] = 1.0 if yellow_pct > green_pct else 0.0
    features['yellow_orange_dominance'] = 1.0 if yellow_pct > orange_pct else 0.0
    features['green_purple_dominance'] = 1.0 if green_pct > purple_pct else 0.0
    features['green_orange_dominance'] = 1.0 if green_pct > orange_pct else 0.0
    features['purple_orange_dominance'] = 1.0 if purple_pct > orange_pct else 0.0
    features['black_white_dominance'] = 1.0 if black_pct > white_pct else 0.0
    features['black_grey_dominance'] = 1.0 if black_pct > grey_pct else 0.0
    features['black_brown_dominance'] = 1.0 if black_pct > brown_pct else 0.0
    features['white_grey_dominance'] = 1.0 if white_pct > grey_pct else 0.0
    features['white_brown_dominance'] = 1.0 if white_pct > brown_pct else 0.0
    features['grey_brown_dominance'] = 1.0 if grey_pct > brown_pct else 0.0
    features['red_orange_dominance'] = 1.0 if red_pct > orange_pct else 0.0
    features['orange_yellow_dominance'] = 1.0 if orange_pct > yellow_pct else 0.0
    features['blue_turquoise_dominance'] = 1.0 if blue_pct > turquoise_pct else 0.0
    features['green_turquoise_dominance'] = 1.0 if green_pct > turquoise_pct else 0.0
    features['purple_pink_dominance'] = 1.0 if purple_pct > pink_pct else 0.0
    features['red_pink_dominance'] = 1.0 if red_pct > pink_pct else 0.0
    
    # Complementary color features (3 features)
    features['red_green_complementary'] = 1.0 if (red_pct > 0.1 and green_pct > 0.1) else 0.0
    features['blue_orange_complementary'] = 1.0 if (blue_pct > 0.1 and orange_pct > 0.1) else 0.0
    features['yellow_purple_complementary'] = 1.0 if (yellow_pct > 0.1 and purple_pct > 0.1) else 0.0
    
    # Analogous color groups (5 features)
    # Group 1: Red, Orange, Yellow
    features['analogous_group_1'] = 1.0 if (red_pct > 0.05 and orange_pct > 0.05 and yellow_pct > 0.05) else 0.0
    # Group 2: Yellow, Green, Blue
    features['analogous_group_2'] = 1.0 if (yellow_pct > 0.05 and green_pct > 0.05 and blue_pct > 0.05) else 0.0
    # Group 3: Blue, Purple, Red
    features['analogous_group_3'] = 1.0 if (blue_pct > 0.05 and purple_pct > 0.05 and red_pct > 0.05) else 0.0
    # Group 4: Green, Blue, Turquoise
    features['analogous_group_4'] = 1.0 if (green_pct > 0.05 and blue_pct > 0.05 and turquoise_pct > 0.05) else 0.0
    # Group 5: Purple, Pink, Red
    features['analogous_group_5'] = 1.0 if (purple_pct > 0.05 and pink_pct > 0.05 and red_pct > 0.05) else 0.0
    
    # Color temperature and balance features (12 features)
    warm_colors = red_pct + orange_pct + yellow_pct + brown_pct
    cool_colors = blue_pct + green_pct + purple_pct + turquoise_pct
    neutral_colors = black_pct + white_pct + grey_pct
    
    features['warm_colors_total'] = warm_colors
    features['cool_colors_total'] = cool_colors
    features['neutral_colors_total'] = neutral_colors
    features['warm_cool_balance'] = abs(warm_colors - cool_colors)
    features['warm_cool_ratio'] = warm_colors / (cool_colors + 0.001)
    
    # Number of dominant colors (colors with >10% presence)
    dominant_count = sum(1 for pct in user_colour_selection.values() if pct > 0.1)
    features['num_dominant_colors'] = dominant_count
    
    # Palette variance (standard deviation of color percentages)
    color_values = list(user_colour_selection.values())
    if len(color_values) > 1:
        features['palette_variance'] = np.std(color_values)
    else:
        features['palette_variance'] = 0.0
    
    # Primary dominance (check if primary colors dominate)
    primary_colors = red_pct + blue_pct + yellow_pct
    features['primary_dominance'] = primary_colors
    
    # Color diversity (number of colors with >5% presence)
    diverse_count = sum(1 for pct in user_colour_selection.values() if pct > 0.05)
    features['color_diversity'] = diverse_count
    
    # Dominant color type features (3 features)
    max_color = max(user_colour_selection.items(), key=lambda x: x[1])[0]
    features['dominant_is_warm'] = 1.0 if max_color in ['red', 'orange', 'yellow', 'brown'] else 0.0
    features['dominant_is_cool'] = 1.0 if max_color in ['blue', 'green', 'purple', 'turquoise'] else 0.0
    features['dominant_is_neutral'] = 1.0 if max_color in ['black', 'white', 'grey'] else 0.0
    
    # Color balance (inverse of palette variance for better interpretation)
    features['color_balance'] = 1.0 - features['palette_variance']
    
    print("Generated color features:")
    for feature, value in features.items():
        print(f"  {feature}: {value:.4f}")
    
    return features

def recommend_paintings(user_selection, original_df, resampled_df, num_recs=10):
    """
    Recommends paintings based on color feature similarity using the 85 color features
    """
    print("\nStarting recommendation process based on color feature similarity...")
    
    # Get user's color features
    user_color_features = create_color_features_from_selection(user_selection)
    
    # Convert user features to DataFrame for comparison
    user_features_df = pd.DataFrame([user_color_features])
    
    # Get the 85 color features from the resampled data
    feature_cols = COLOR_FEATURES
    
    # Check if all required features exist in the data
    missing_features = [col for col in feature_cols if col not in resampled_df.columns]
    if missing_features:
        print(f"Warning: Missing features in data: {missing_features}")
        # Use only available features
        feature_cols = [col for col in feature_cols if col in resampled_df.columns]
    
    if not feature_cols:
        print("Error: No matching color features found in data")
        return []
    
    print(f"Using {len(feature_cols)} color features for similarity matching")
    
    # Get feature vectors from resampled data
    resampled_features = resampled_df[feature_cols].values
    user_features = user_features_df[feature_cols].values
    
    # Calculate cosine similarity between user features and all paintings
    from sklearn.metrics.pairwise import cosine_similarity
    
    similarities = cosine_similarity(user_features, resampled_features)[0]
    
    # Get indices of top similar paintings
    top_indices = np.argsort(similarities)[::-1][:num_recs]
    
    # Get URLs of top similar paintings
    recommendations = []
    for idx in top_indices:
        url = resampled_df.iloc[idx]['url']
        similarity_score = similarities[idx]
        recommendations.append(url)
        print(f"Similarity {similarity_score:.4f}: {url}")
    
    print(f"Found {len(recommendations)} recommendations based on color feature similarity")
    
    return recommendations

def get_detailed_recommendations(user_selection, original_df, resampled_df, num_recs=10):
    """
    Get recommendations with detailed painting information
    """
    # Get basic recommendations
    recommendations = recommend_paintings(user_selection, original_df, resampled_df, num_recs)
    
    # Extract detailed information for each recommendation
    detailed_recommendations = []
    for url in recommendations:
        info = extract_painting_info(url)
        detailed_recommendations.append({
            'url': url,
            'artist': info['artist'],
            'title': info['title'],
            'year': info['year']
        })
    
    return detailed_recommendations

def extract_painting_info(url):
    """
    Extract artist, title, and year from WikiArt URL
    
    Example URL: https://uploads0.wikiart.org/00120/images/agostino-tassi/naufragio-della-flotta-di-enea-1627.jpg
    Returns: {'artist': 'Agostino Tassi', 'title': 'Naufragio Della Flotta Di Enea', 'year': '1627'}
    """
    import re
    
    try:
        # Extract the filename from URL (everything after the last '/')
        filename = url.split('/')[-1]
        
        # Remove file extension
        filename_no_ext = filename.rsplit('.', 1)[0]
        
        # Extract artist from URL path (second to last segment)
        url_parts = url.split('/')
        artist_slug = None
        for i, part in enumerate(url_parts):
            if part == 'images' and i + 1 < len(url_parts):
                artist_slug = url_parts[i + 1]
                break
        
        # Convert artist slug to proper name (replace hyphens with spaces, title case)
        if artist_slug:
            artist = ' '.join(word.capitalize() for word in artist_slug.split('-'))
        else:
            artist = "Unknown Artist"
        
        # Extract year from filename (look for 4-digit number at the end)
        year_match = re.search(r'-(\d{4})$', filename_no_ext)
        year = year_match.group(1) if year_match else "Unknown Year"
        
        # Extract title (everything before the year, after removing artist info if present)
        if year_match:
            title_part = filename_no_ext[:year_match.start()]
        else:
            title_part = filename_no_ext
        
        # Remove artist name from title if it appears at the beginning
        if artist_slug and title_part.startswith(artist_slug):
            title_part = title_part[len(artist_slug):].lstrip('-')
        
        # Convert title to proper format (replace hyphens/underscores with spaces, title case)
        title = ' '.join(word.capitalize() for word in re.split(r'[-_]', title_part))
        
        # Clean up title (remove extra spaces, handle special cases)
        title = re.sub(r'\s+', ' ', title).strip()
        if not title:
            title = "Untitled"
        
        return {
            'artist': artist,
            'title': title,
            'year': year
        }
        
    except Exception as e:
        print(f"Error extracting info from URL {url}: {e}")
        return {
            'artist': "Unknown Artist",
            'title': "Unknown Title", 
            'year': "Unknown Year"
        }

def main():
    """Main function to run the recommendation system"""
    try:
        # Get image path from command line argument
        if len(sys.argv) < 2:
            print("Usage: python3 recommendation_service_embedded.py <image_path>")
            sys.exit(1)
        
        image_path = sys.argv[1]
        print(f"Processing image: {image_path}")
        
        # Check if data files exist
        if not os.path.exists(ORIGINAL_DATA_PATH):
            print(f"Error: Original data file not found at {ORIGINAL_DATA_PATH}")
            sys.exit(1)
        
        if not os.path.exists(RESAMPLED_DATA_PATH):
            print(f"Error: Resampled data file not found at {RESAMPLED_DATA_PATH}")
            sys.exit(1)
        
        # Load data
        print("Loading original data...")
        original_data = pd.read_csv(ORIGINAL_DATA_PATH)
        
        print("Loading resampled data...")
        resampled_data = pd.read_csv(RESAMPLED_DATA_PATH)
        
        # Generate user input
        user_colour_selection = generate_user_colour_selection(image_path)
        
        # Predict emotion
        user_color_features = create_color_features_from_selection(user_colour_selection)
        emotion_prediction = predict_emotion_via_api(user_color_features)
        
        print("\n=== Emotion Prediction ===")
        print(f"Predicted emotion: {emotion_prediction['emotion']}")
        print(f"Confidence: {emotion_prediction['confidence']:.1%}")
        
        # Get recommendations
        detailed_recommendations = get_detailed_recommendations(
            user_selection=user_colour_selection,
            original_df=original_data,
            resampled_df=resampled_data,
            num_recs=NUM_RECOMMENDATIONS
        )
        
        # Output results in expected format
        if detailed_recommendations:
            print("\n--- Top 10 Recommended Painting URLs ---")
            for i, painting in enumerate(detailed_recommendations):
                print(f"{i+1}. {painting['url']}")
            
            print("\n--- DETAILED_RECOMMENDATIONS_JSON ---")
            print(json.dumps(detailed_recommendations, indent=2))
            print("--- END_DETAILED_RECOMMENDATIONS_JSON ---")
            
            print("\n--- EMOTION_PREDICTION_JSON ---")
            emotion_output = {
                "emotion": emotion_prediction["emotion"],
                "confidence_percentage": f"{emotion_prediction['confidence']:.1%}",
                "all_probabilities": emotion_prediction["all_probabilities"]
            }
            print(json.dumps(emotion_output, indent=2))
            print("--- END_EMOTION_PREDICTION_JSON ---")
        else:
            print("\nCould not generate recommendations with the given data.")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error in main function: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 