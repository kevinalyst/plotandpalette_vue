#!/usr/bin/env python3
"""
Recommendation Service
Handles cluster-based painting recommendations using raw color data from emotion prediction service.
"""
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import math
import os
import json
import sys
import random
from collections import Counter, defaultdict
from datetime import datetime, timedelta

# Configuration
CLUSTER_PALETTES_PATH = os.path.join(os.path.dirname(__file__), "cluster_color_palettes.csv")
COLOUR_DATA_PATH = os.path.join(os.path.dirname(__file__), "colour_data_with_clusters_3.0.csv")
NUM_RECOMMENDATIONS = 10

# Diversity and Exploration Parameters
DIVERSITY_CONFIG = {
    'N_CAND': 600,           # Candidate pool size
    'N_SAMPLE': 60,          # Softmax sampling size
    'K_FINAL': 12,           # Final recommendations (will be trimmed to NUM_RECOMMENDATIONS)
    'LAMBDA_MMR': 0.8,       # MMR balance (relevance vs diversity)
    'TEMP_SOFTMAX': 0.08,    # Softmax temperature for sampling
    'ALPHA_USER': 0.03,      # Per-user exposure penalty weight
    'BETA_STABILITY': 0.05,  # Stability penalty weight
    'GAMMA_POP': 0.02,       # Global popularity penalty weight
    'QUOTA_MAX': 0.4,        # Max 40% from any cluster
    'COOLDOWN_DAYS': 14,     # Recently seen cooldown period
    'ARTIST_PENALTY': 0.05,  # Same artist penalty
    'ASPECT_PENALTY': 0.03   # Aspect ratio diversity penalty
}

def calculate_color_statistics(raw_colors):
    """
    Calculate BGR, HSV, and LAB statistics from raw color data.
    
    Args:
        raw_colors: List of color dictionaries with 'bgr', 'hsv', 'lab', and 'percentage' keys
    
    Returns:
        Dictionary with mean and std statistics for each color space
    """
    print("\n=== Calculating Color Statistics ===")
    
    # Extract color values weighted by percentage
    bgr_values = []
    hsv_values = []
    lab_values = []
    weights = []
    
    for color in raw_colors:
        bgr_values.append(color['bgr'])
        hsv_values.append(color['hsv'])
        lab_values.append(color['lab'])
        weights.append(color['percentage'])
    
    # Convert to numpy arrays
    bgr_array = np.array(bgr_values)
    hsv_array = np.array(hsv_values)
    lab_array = np.array(lab_values)
    weights_array = np.array(weights)
    
    # Calculate weighted means
    bgr_mean = np.average(bgr_array, axis=0, weights=weights_array)
    hsv_mean = np.average(hsv_array, axis=0, weights=weights_array)
    lab_mean = np.average(lab_array, axis=0, weights=weights_array)
    
    # Calculate weighted standard deviations
    bgr_std = np.sqrt(np.average((bgr_array - bgr_mean)**2, axis=0, weights=weights_array))
    hsv_std = np.sqrt(np.average((hsv_array - hsv_mean)**2, axis=0, weights=weights_array))
    lab_std = np.sqrt(np.average((lab_array - lab_mean)**2, axis=0, weights=weights_array))
    
    statistics = {
        'bgr_mean': bgr_mean.tolist(),
        'hsv_mean': hsv_mean.tolist(),
        'lab_mean': lab_mean.tolist(),
        'bgr_std': bgr_std.tolist(),
        'hsv_std': hsv_std.tolist(),
        'lab_std': lab_std.tolist()
    }
    
    print(f"BGR mean: {bgr_mean}")
    print(f"HSV mean: {hsv_mean}")
    print(f"LAB mean: {lab_mean}")
    print(f"BGR std: {bgr_std}")
    print(f"HSV std: {hsv_std}")
    print(f"LAB std: {lab_std}")
    
    return statistics

def categorize_colors_to_clusters(raw_colors, cluster_df):
    """
    Categorize the five raw colors into their nearest cluster_id using k-means.
    
    Args:
        raw_colors: List of raw color dictionaries
        cluster_df: DataFrame with cluster information
    
    Returns:
        Dictionary with cluster_id percentages
    """
    print("\n=== Categorizing Colors to Clusters ===")
    
    # Prepare cluster centers using bgr_mean, hsv_mean, lab_mean (9 dimensions)
    cluster_features = []
    cluster_ids = []
    
    for _, row in cluster_df.iterrows():
        features = [
            row['b_bgr_mean'], row['g_bgr_mean'], row['r_bgr_mean'],  # BGR
            row['h_hsv_mean'], row['s_hsv_mean'], row['v_hsv_mean'],  # HSV
            row['l_lab_mean'], row['a_lab_mean'], row['b_lab_mean']   # LAB
        ]
        cluster_features.append(features)
        cluster_ids.append(row['cluster_id'])
    
    cluster_centers = np.array(cluster_features)
    
    # Prepare raw color features (9 dimensions per color)
    color_features = []
    color_percentages = []
    
    for color in raw_colors:
        features = (
            color['bgr'] +  # 3 dimensions
            color['hsv'] +  # 3 dimensions
            color['lab']    # 3 dimensions
        )
        color_features.append(features)
        color_percentages.append(color['percentage'])
    
    color_features = np.array(color_features)
    
    print(f"Cluster centers shape: {cluster_centers.shape}")
    print(f"Color features shape: {color_features.shape}")
    
    # Calculate distances from each color to each cluster center
    cluster_assignments = {}
    
    for i, color_feature in enumerate(color_features):
        # Calculate Euclidean distances to all cluster centers
        distances = np.linalg.norm(cluster_centers - color_feature, axis=1)
        
        # Find the nearest cluster
        nearest_cluster_idx = np.argmin(distances)
        nearest_cluster_id = cluster_ids[nearest_cluster_idx]
        
        print(f"Color {i+1} (BGR: {raw_colors[i]['bgr']}) -> Cluster {nearest_cluster_id} (distance: {distances[nearest_cluster_idx]:.2f})")
        
        # Add percentage to cluster
        if nearest_cluster_id in cluster_assignments:
            cluster_assignments[nearest_cluster_id] += color_percentages[i]
        else:
            cluster_assignments[nearest_cluster_id] = color_percentages[i]
    
    # Sort by percentage (descending)
    sorted_clusters = dict(sorted(cluster_assignments.items(), key=lambda x: x[1], reverse=True))
    
    print("\nCluster assignments:")
    for cluster_id, percentage in sorted_clusters.items():
        print(f"  Cluster {cluster_id}: {percentage:.1%}")
    
    return sorted_clusters

def calculate_headcount(cluster_percentages, total_recommendations=10):
    """
    Calculate how many recommendations should come from each cluster.
    
    Args:
        cluster_percentages: Dictionary with cluster_id -> percentage
        total_recommendations: Total number of recommendations needed
    
    Returns:
        Dictionary with cluster_id -> headcount
    """
    print(f"\n=== Calculating Headcount for {total_recommendations} recommendations ===")
    
    headcount = {}
    remaining = total_recommendations
    
    # Sort clusters by percentage (descending)
    sorted_clusters = sorted(cluster_percentages.items(), key=lambda x: x[1], reverse=True)
    
    # Calculate initial headcount based on percentages
    for cluster_id, percentage in sorted_clusters[:-1]:  # All except the last
        count = max(1, round(percentage * total_recommendations))  # At least 1
        headcount[cluster_id] = count
        remaining -= count
    
    # Give remaining recommendations to the last cluster
    if sorted_clusters:
        last_cluster_id = sorted_clusters[-1][0]
        headcount[last_cluster_id] = max(1, remaining)  # At least 1
    
    # Verify total
    total_assigned = sum(headcount.values())
    if total_assigned != total_recommendations:
        # Adjust the largest cluster to match exactly
        largest_cluster = max(headcount.items(), key=lambda x: x[1])
        adjustment = total_recommendations - total_assigned
        headcount[largest_cluster[0]] += adjustment
    
    print("Headcount distribution:")
    for cluster_id, count in headcount.items():
        percentage = cluster_percentages[cluster_id]
        print(f"  Cluster {cluster_id}: {count} paintings ({percentage:.1%})")
    
    return headcount

def get_recommendations_from_clusters(cluster_headcount, colour_data_df, user_color_stats):
    """
    Get painting recommendations from each cluster using cosine similarity.
    
    Args:
        cluster_headcount: Dictionary with cluster_id -> count
        colour_data_df: DataFrame with painting data and clusters
        user_color_stats: Dictionary with user's input image color statistics
    
    Returns:
        List of recommendation dictionaries
    """
    print("\n=== Getting Recommendations from Clusters ===")
    
    all_recommendations = []
    
    # Feature columns for similarity calculation (18 features: 9 means + 9 stds)
    feature_columns = [
        'b_bgr_mean', 'g_bgr_mean', 'r_bgr_mean',
        'h_hsv_mean', 's_hsv_mean', 'v_hsv_mean', 
        'l_lab_mean', 'a_lab_mean', 'b_lab_mean',
        'b_bgr_std', 'g_bgr_std', 'r_bgr_std',
        'h_hsv_std', 's_hsv_std', 'v_hsv_std',
        'l_lab_std', 'a_lab_std', 'b_lab_std'
    ]
    
    for cluster_id, count in cluster_headcount.items():
        print(f"\nProcessing Cluster {cluster_id} - need {count} recommendations")
        
        # Filter paintings in this cluster
        cluster_paintings = colour_data_df[colour_data_df['cluster_id'] == cluster_id].copy()
        
        if len(cluster_paintings) == 0:
            print(f"  Warning: No paintings found in cluster {cluster_id}")
            continue
        
        if len(cluster_paintings) <= count:
            # Take all paintings if we have fewer than needed
            selected_paintings = cluster_paintings
            print(f"  Taking all {len(selected_paintings)} available paintings")
        else:
            # Use cosine similarity to find paintings most similar to user's input image
            cluster_features = cluster_paintings[feature_columns].values
            
            # Create user color feature vector from input image statistics
            user_features = np.array([
                user_color_stats['bgr_mean'][0], user_color_stats['bgr_mean'][1], user_color_stats['bgr_mean'][2],  # BGR means
                user_color_stats['hsv_mean'][0], user_color_stats['hsv_mean'][1], user_color_stats['hsv_mean'][2],  # HSV means  
                user_color_stats['lab_mean'][0], user_color_stats['lab_mean'][1], user_color_stats['lab_mean'][2],  # LAB means
                user_color_stats['bgr_std'][0], user_color_stats['bgr_std'][1], user_color_stats['bgr_std'][2],    # BGR stds
                user_color_stats['hsv_std'][0], user_color_stats['hsv_std'][1], user_color_stats['hsv_std'][2],    # HSV stds
                user_color_stats['lab_std'][0], user_color_stats['lab_std'][1], user_color_stats['lab_std'][2]     # LAB stds
            ]).reshape(1, -1)
            
            # Calculate cosine similarity between each painting and the user's input image
            similarities = cosine_similarity(cluster_features, user_features).flatten()
            
            # Get indices of paintings with highest similarity to user's input image
            top_indices = np.argsort(similarities)[::-1][:count]
            selected_paintings = cluster_paintings.iloc[top_indices]
            
            print(f"  Selected {len(selected_paintings)} paintings most similar to user's input image")
            for i, (idx, similarity) in enumerate(zip(top_indices, similarities[top_indices])):
                painting = cluster_paintings.iloc[idx]
                print(f"    {i+1}. Similarity: {similarity:.4f} - {painting.get('filename', 'Unknown')}")
        
        # Extract painting information
        for _, painting in selected_paintings.iterrows():
            # Extract artist and title from page URL if available
            page_url = painting.get('page', '')
            image_url = painting.get('image', '')
            
            # Try to extract artist and title from the page URL
            artist, title = extract_artist_title_from_url(page_url)
            
            recommendation = {
                'url': image_url,
                'page': page_url,
                'artist': artist,
                'title': title,
                'cluster_id': cluster_id
            }
            all_recommendations.append(recommendation)
    
    print(f"\nTotal recommendations collected: {len(all_recommendations)}")
    return all_recommendations

def extract_artist_title_from_url(page_url):
    """
    Extract artist and title from Google Arts & Culture page URL.
    
    Example URL: https://artsandculture.google.com/asset/the-lovers-marc-chagall/jQEveVgIzd6-Og
    
    Args:
        page_url: The page URL string
    
    Returns:
        Tuple of (artist, title)
    """
    try:
        if not page_url or 'artsandculture.google.com' not in page_url:
            return "Unknown Artist", "Unknown Title"
        
        # Extract the path part after '/asset/'
        if '/asset/' in page_url:
            path_part = page_url.split('/asset/')[-1]
            # Remove the ID part (everything after the last '/')
            if '/' in path_part:
                title_artist_part = path_part.split('/')[0]
            else:
                title_artist_part = path_part
            
            # Split by hyphens and try to identify title and artist
            parts = title_artist_part.split('-')
            
            if len(parts) >= 2:
                # Common patterns:
                # "the-lovers-marc-chagall" -> title: "The Lovers", artist: "Marc Chagall"
                # Look for capitalized words that might be names
                
                # Simple heuristic: assume last 2-3 parts might be artist name
                if len(parts) >= 4:
                    # Likely format: title-words-artist-surname
                    title_parts = parts[:-2]
                    artist_parts = parts[-2:]
                elif len(parts) == 3:
                    # Could be: title-artist-surname or title-word-artist
                    title_parts = parts[:-2]
                    artist_parts = parts[-2:]
                else:
                    # title-artist or just title
                    title_parts = parts[:-1]
                    artist_parts = parts[-1:]
                
                title = ' '.join(word.capitalize() for word in title_parts)
                artist = ' '.join(word.capitalize() for word in artist_parts)
                
                # Clean up
                if not title:
                    title = "Unknown Title"
                if not artist:
                    artist = "Unknown Artist"
                
                return artist, title
            else:
                # Single part, treat as title
                title = ' '.join(word.capitalize() for word in parts)
                return "Unknown Artist", title if title else "Unknown Title"
        
        return "Unknown Artist", "Unknown Title"
        
    except Exception as e:
        print(f"Error extracting artist/title from URL {page_url}: {e}")
        return "Unknown Artist", "Unknown Title"

def calculate_stability_scores(colour_data_df, feature_columns):
    """
    Calculate stability scores for all paintings (precomputed measure of how "universally appealing" they are).
    Higher stability = lower variance across different user queries.
    """
    print("\n=== Calculating Stability Scores ===")
    
    # For demo purposes, we'll use a simple heuristic based on feature variance
    # In production, this could be precomputed from historical user interactions
    stability_scores = {}
    
    for _, painting in colour_data_df.iterrows():
        filename = painting['filename']
        
        # Simple stability heuristic: inverse of feature variance
        # Paintings with more "average" features tend to be more universally appealing
        features = np.array([painting[col] for col in feature_columns])
        
        # Normalize features to [0,1] range for fair comparison
        feature_ranges = {
            'bgr': [0, 255], 'hsv': [0, 360], 'lab': [-100, 100], 'std': [0, 100]
        }
        
        normalized_features = []
        for i, col in enumerate(feature_columns):
            if 'bgr' in col:
                normalized_features.append(features[i] / 255.0)
            elif 'hsv' in col:
                normalized_features.append(features[i] / 360.0)
            elif 'lab' in col:
                normalized_features.append((features[i] + 100) / 200.0)
            else:  # std features
                normalized_features.append(features[i] / 100.0)
        
        # Stability = 1 / (1 + variance from center)
        center = np.array([0.5] * len(normalized_features))
        variance_from_center = np.var(normalized_features - center)
        stability = 1.0 / (1.0 + variance_from_center * 10)  # Scale factor for reasonable range
        
        stability_scores[filename] = stability
    
    print(f"Calculated stability scores for {len(stability_scores)} paintings")
    return stability_scores

def get_diverse_recommendations(user_color_stats, colour_data_df, cluster_percentages, 
                               user_exposure=None, pop_exposure=None, recently_seen=None):
    """
    Advanced recommendation system with diversity, exploration, and fatigue prevention.
    
    Args:
        user_color_stats: User's input image color statistics
        colour_data_df: DataFrame with painting data
        cluster_percentages: Dictionary with cluster_id -> percentage  
        user_exposure: Dictionary with filename -> exposure count for this user
        pop_exposure: Dictionary with filename -> global exposure count
        recently_seen: Set of filenames seen recently
    
    Returns:
        List of recommendation dictionaries with diversity and exploration
    """
    print("\n=== Advanced Diverse Recommendation System ===")
    
    # Initialize exposure tracking if not provided
    if user_exposure is None:
        user_exposure = defaultdict(int)
    if pop_exposure is None:
        pop_exposure = defaultdict(int)  
    if recently_seen is None:
        recently_seen = set()
    
    # Feature columns for similarity calculation
    feature_columns = [
        'b_bgr_mean', 'g_bgr_mean', 'r_bgr_mean',
        'h_hsv_mean', 's_hsv_mean', 'v_hsv_mean', 
        'l_lab_mean', 'a_lab_mean', 'b_lab_mean',
        'b_bgr_std', 'g_bgr_std', 'r_bgr_std',
        'h_hsv_std', 's_hsv_std', 'v_hsv_std',
        'l_lab_std', 'a_lab_std', 'b_lab_std'
    ]
    
    # Create user color feature vector
    user_features = np.array([
        user_color_stats['bgr_mean'][0], user_color_stats['bgr_mean'][1], user_color_stats['bgr_mean'][2],
        user_color_stats['hsv_mean'][0], user_color_stats['hsv_mean'][1], user_color_stats['hsv_mean'][2],
        user_color_stats['lab_mean'][0], user_color_stats['lab_mean'][1], user_color_stats['lab_mean'][2],
        user_color_stats['bgr_std'][0], user_color_stats['bgr_std'][1], user_color_stats['bgr_std'][2],
        user_color_stats['hsv_std'][0], user_color_stats['hsv_std'][1], user_color_stats['hsv_std'][2],
        user_color_stats['lab_std'][0], user_color_stats['lab_std'][1], user_color_stats['lab_std'][2]
    ]).reshape(1, -1)
    
    # Calculate stability scores
    stability_scores = calculate_stability_scores(colour_data_df, feature_columns)
    
    print(f"Step 1: Candidate Generation (top-{DIVERSITY_CONFIG['N_CAND']} by cosine similarity)")
    
    # Step 1: Candidate generation - Calculate cosine similarity for all paintings
    all_features = colour_data_df[feature_columns].values
    similarities = cosine_similarity(all_features, user_features).flatten()
    
    # Get top N candidates
    top_indices = np.argsort(similarities)[::-1][:DIVERSITY_CONFIG['N_CAND']]
    candidates = colour_data_df.iloc[top_indices].copy()
    candidate_similarities = similarities[top_indices]
    
    print(f"Selected {len(candidates)} candidates with similarity range: {candidate_similarities.min():.4f} - {candidate_similarities.max():.4f}")
    
    # Step 2: Score shift (exposure & stability penalties)
    print("Step 2: Applying exposure and stability penalties")
    
    score_shifted = {}
    for idx, (_, painting) in enumerate(candidates.iterrows()):
        filename = painting['filename']
        base_similarity = candidate_similarities[idx]
        
        # Calculate penalties
        p_user = np.log1p(user_exposure[filename])  # Per-user fatigue
        p_stab = 1.0 / (1.0 + stability_scores[filename])  # Stability penalty
        p_pop = np.log1p(pop_exposure[filename])  # Global popularity fatigue
        
        penalty = (DIVERSITY_CONFIG['ALPHA_USER'] * p_user + 
                  DIVERSITY_CONFIG['BETA_STABILITY'] * p_stab + 
                  DIVERSITY_CONFIG['GAMMA_POP'] * p_pop)
        
        shifted_score = base_similarity - penalty
        score_shifted[filename] = max(0.0, min(1.0, shifted_score))  # Clamp to [0,1]
    
    # Step 3: Filter (cooldown / hard constraints)
    print("Step 3: Applying cooldown filters")
    
    filtered_candidates = []
    for _, painting in candidates.iterrows():
        filename = painting['filename']
        if filename not in recently_seen:
            filtered_candidates.append(painting)
    
    # Backfill if needed
    if len(filtered_candidates) < DIVERSITY_CONFIG['N_SAMPLE']:
        print(f"Backfilling candidates: {len(filtered_candidates)} -> {DIVERSITY_CONFIG['N_SAMPLE']}")
        needed = DIVERSITY_CONFIG['N_SAMPLE'] - len(filtered_candidates)
        
        # Get next best candidates not in recently_seen
        remaining_indices = np.argsort(similarities)[::-1][DIVERSITY_CONFIG['N_CAND']:]
        for idx in remaining_indices[:needed*2]:  # Check 2x needed in case of overlaps
            painting = colour_data_df.iloc[idx]
            if painting['filename'] not in recently_seen:
                filtered_candidates.append(painting)
                score_shifted[painting['filename']] = similarities[idx] * 0.8  # Slight penalty for backfill
                if len(filtered_candidates) >= DIVERSITY_CONFIG['N_SAMPLE']:
                    break
    
    candidates_df = pd.DataFrame(filtered_candidates)
    print(f"After filtering: {len(candidates_df)} candidates")
    
    # Step 4: Softmax sampling (controlled randomness)
    print("Step 4: Softmax sampling for exploration")
    
    # Convert to probabilities with temperature
    candidate_filenames = [row['filename'] for _, row in candidates_df.iterrows()]
    scores = np.array([score_shifted[f] for f in candidate_filenames])
    
    # Apply softmax with temperature
    exp_scores = np.exp(scores / DIVERSITY_CONFIG['TEMP_SOFTMAX'])
    probabilities = exp_scores / np.sum(exp_scores)
    
    # Sample without replacement
    sample_size = min(DIVERSITY_CONFIG['N_SAMPLE'], len(candidates_df))
    sample_indices = np.random.choice(len(candidates_df), size=sample_size, replace=False, p=probabilities)
    sampled_candidates = candidates_df.iloc[sample_indices]
    
    print(f"Sampled {len(sampled_candidates)} candidates for diversity re-ranking")
    
    return sampled_candidates, score_shifted, feature_columns

def mmr_diversity_rerank(sampled_candidates, score_shifted, feature_columns, user_color_stats):
    """
    Step 5: MMR diversity re-ranking with metadata awareness
    """
    print("Step 5: MMR diversity re-ranking")
    
    final_slate = []
    pool = sampled_candidates.copy()
    k_final = min(DIVERSITY_CONFIG['K_FINAL'], len(pool))
    
    while len(final_slate) < k_final and len(pool) > 0:
        best_item = None
        best_score = float('-inf')
        
        for idx, painting in pool.iterrows():
            filename = painting['filename']
            base_score = score_shifted[filename]
            
            # Calculate diversity penalty (color similarity to already selected items)
            if len(final_slate) == 0:
                color_overlap = 0
            else:
                # Get features for current painting
                current_features = np.array([painting[col] for col in feature_columns]).reshape(1, -1)
                
                # Calculate max similarity to items already in slate
                max_similarity = 0
                for selected_painting in final_slate:
                    selected_features = np.array([selected_painting[col] for col in feature_columns]).reshape(1, -1)
                    similarity = cosine_similarity(current_features, selected_features)[0][0]
                    max_similarity = max(max_similarity, similarity)
                color_overlap = max_similarity
            
            # Artist penalty (avoid same artist)
            artist_penalty = 0
            for selected_painting in final_slate:
                if painting.get('page', '') and selected_painting.get('page', ''):
                    # Simple artist check - could be improved with better metadata
                    if painting['page'].split('/')[-2:] == selected_painting['page'].split('/')[-2:]:
                        artist_penalty = DIVERSITY_CONFIG['ARTIST_PENALTY']
                        break
            
            # MMR score
            mmr_score = (DIVERSITY_CONFIG['LAMBDA_MMR'] * base_score - 
                        (1 - DIVERSITY_CONFIG['LAMBDA_MMR']) * color_overlap - 
                        artist_penalty)
            
            if mmr_score > best_score:
                best_score = mmr_score
                best_item = painting
        
        if best_item is not None:
            final_slate.append(best_item)
            pool = pool.drop(best_item.name)
    
    print(f"MMR selected {len(final_slate)} diverse items")
    return final_slate

def apply_cluster_quotas(final_slate, cluster_percentages):
    """
    Step 6: Cluster quota & coverage adjustment
    """
    print("Step 6: Applying cluster quotas")
    
    if len(final_slate) == 0:
        return final_slate
    
    # Count cluster usage
    cluster_counts = Counter()
    for painting in final_slate:
        cluster_id = painting['cluster_id']
        cluster_counts[cluster_id] += 1
    
    quota_limit = int(DIVERSITY_CONFIG['QUOTA_MAX'] * len(final_slate))
    print(f"Cluster quota limit: {quota_limit} per cluster")
    
    # Check for quota violations
    adjusted_slate = []
    cluster_usage = Counter()
    
    for painting in final_slate:
        cluster_id = painting['cluster_id']
        if cluster_usage[cluster_id] < quota_limit:
            adjusted_slate.append(painting)
            cluster_usage[cluster_id] += 1
        else:
            print(f"Skipping painting from over-quota cluster {cluster_id}")
    
    print(f"After quota adjustment: {len(adjusted_slate)} items")
    return adjusted_slate

def main():
    """Main function to run the recommendation service"""
    try:
        # Get raw colors JSON from command line argument
        if len(sys.argv) < 2:
            print("Usage: python3 recommendation_service.py <raw_colors_json>")
            sys.exit(1)
        
        raw_colors_json = sys.argv[1]
        print(f"Processing raw colors: {raw_colors_json}")
        
        # Parse raw colors
        try:
            raw_colors = json.loads(raw_colors_json)
        except json.JSONDecodeError as e:
            print(f"Error parsing raw colors JSON: {e}")
            sys.exit(1)
        
        # Validate raw colors format
        if not isinstance(raw_colors, list) or len(raw_colors) != 5:
            print("Error: Expected 5 raw colors")
            sys.exit(1)
        
        # Check if data files exist
        if not os.path.exists(CLUSTER_PALETTES_PATH):
            print(f"Error: Cluster palettes file not found at {CLUSTER_PALETTES_PATH}")
            sys.exit(1)
        
        if not os.path.exists(COLOUR_DATA_PATH):
            print(f"Error: Colour data file not found at {COLOUR_DATA_PATH}")
            sys.exit(1)
        
        # Load data files
        print("Loading cluster palettes...")
        cluster_df = pd.read_csv(CLUSTER_PALETTES_PATH)
        
        print("Loading colour data with clusters...")
        colour_data_df = pd.read_csv(COLOUR_DATA_PATH)
        
        print(f"Loaded {len(cluster_df)} cluster centers")
        print(f"Loaded {len(colour_data_df)} paintings with cluster assignments")
        
        # Calculate color statistics
        color_stats = calculate_color_statistics(raw_colors)
        
        # Categorize colors to clusters
        cluster_percentages = categorize_colors_to_clusters(raw_colors, cluster_df)
        
        # Use new diverse recommendation system
        print(f"\n=== Using Advanced Diverse Recommendation System ===")
        
        # For demo purposes, simulate some user exposure and recently seen data
        # In production, these would come from user history/session data
        user_exposure = defaultdict(int)
        pop_exposure = defaultdict(int)
        recently_seen = set()
        
        # Add some fake exposure data to demonstrate the system
        # Simulate that some "universally appealing" paintings have been seen before
        fake_high_exposure = ['2333.jpg', '2390.jpg', '2452.jpg']  # The paintings we identified as "safe hits"
        for filename in fake_high_exposure:
            user_exposure[filename] = 2  # User has seen these 2 times
            pop_exposure[filename] = 100  # These are popular globally
        
        # Step 1-4: Get diverse candidates with sampling
        sampled_candidates, score_shifted, feature_columns = get_diverse_recommendations(
            color_stats, colour_data_df, cluster_percentages, 
            user_exposure, pop_exposure, recently_seen
        )
        
        # Step 5: MMR diversity re-ranking
        final_slate = mmr_diversity_rerank(sampled_candidates, score_shifted, feature_columns, color_stats)
        
        # Step 6: Apply cluster quotas
        quota_adjusted_slate = apply_cluster_quotas(final_slate, cluster_percentages)
        
        # Convert to recommendation format and limit to requested number
        recommendations = []
        for painting in quota_adjusted_slate[:NUM_RECOMMENDATIONS]:
            # Extract artist and title from page URL
            page_url = painting.get('page', '')
            image_url = painting.get('image', '')
            
            artist, title = extract_artist_title_from_url(page_url)
            
            recommendation = {
                'url': image_url,
                'page': page_url,
                'artist': artist,
                'title': title,
                'cluster_id': painting['cluster_id'],
                'filename': painting['filename'],
                'similarity_score': score_shifted.get(painting['filename'], 0.0)
            }
            recommendations.append(recommendation)
        
        final_recommendations = recommendations
        
        # Output results
        print(f"\n=== RECOMMENDATION RESULTS ===")
        print(f"Found {len(final_recommendations)} recommendations")
        
        print("\n--- Top 10 Recommended Painting URLs ---")
        for i, painting in enumerate(final_recommendations):
            print(f"{i+1}. {painting['url']}")
        
        print("\n--- DETAILED_RECOMMENDATIONS_JSON ---")
        print(json.dumps(final_recommendations, indent=2))
        print("--- END_DETAILED_RECOMMENDATIONS_JSON ---")
        
        print("\n--- CLUSTER_ANALYSIS_JSON ---")
        cluster_analysis = {
            "cluster_percentages": {str(k): v for k, v in cluster_percentages.items()},
            "diversity_system_used": True,
            "diversity_config": DIVERSITY_CONFIG,
            "color_statistics": color_stats,
            "recommendation_stats": {
                "total_candidates_generated": DIVERSITY_CONFIG['N_CAND'],
                "sampled_for_diversity": DIVERSITY_CONFIG['N_SAMPLE'],
                "final_slate_size": len(final_recommendations),
                "cluster_distribution": dict(Counter([r['cluster_id'] for r in final_recommendations]))
            }
        }
        print(json.dumps(cluster_analysis, indent=2))
        print("--- END_CLUSTER_ANALYSIS_JSON ---")
        
    except Exception as e:
        print(f"Error in main function: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()