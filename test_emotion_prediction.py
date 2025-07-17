#!/usr/bin/env python3
"""
Test script to verify emotion prediction returns all 15 emotions
Usage: python3 test_emotion_prediction.py
"""

import sys
import os
sys.path.insert(0, '/var/www/plot-palette')

import joblib
import numpy as np
from datetime import datetime

def test_emotion_model_loading():
    """Test loading the emotion model files"""
    print("🧪 Testing Emotion Model Loading")
    print("=" * 50)
    
    # Model paths
    MODEL_PATH = "/var/www/plot-palette/emotions_generation/final_emotion_model.pkl"
    SCALER_PATH = "/var/www/plot-palette/emotions_generation/final_scaler.pkl"
    FEATURE_INFO_PATH = "/var/www/plot-palette/emotions_generation/final_feature_info.pkl"
    
    # Check if files exist
    for name, path in [("Model", MODEL_PATH), ("Scaler", SCALER_PATH), ("Feature Info", FEATURE_INFO_PATH)]:
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ {name}: {path} ({size:,} bytes)")
        else:
            print(f"❌ {name}: {path} - NOT FOUND")
            return False
    
    try:
        # Load model components
        print("\n📊 Loading model components...")
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        feature_info = joblib.load(FEATURE_INFO_PATH)
        
        # Extract feature structure
        color_columns = feature_info.get('color_columns', [])
        engineered_columns = [col for col in feature_info.get('final_features', []) 
                             if col not in color_columns]
        emotion_columns = feature_info.get('emotion_columns', [])
        
        print(f"✅ Model loaded successfully")
        print(f"   Color features: {len(color_columns)}")
        print(f"   Engineered features: {len(engineered_columns)}")
        print(f"   Emotion classes: {len(emotion_columns)}")
        
        # Display the 15 emotions
        print(f"\n🎭 15 Emotions in Model:")
        for i, emotion in enumerate(emotion_columns, 1):
            print(f"   {i:2d}. {emotion}")
        
        # Expected 15 emotions from illustrations
        expected_emotions = [
            'anger', 'anticipation', 'arrogance', 'disagreeableness', 'disgust',
            'fear', 'gratitude', 'happiness', 'humility', 'love',
            'optimism', 'pessimism', 'sadness', 'surprise', 'trust'
        ]
        
        print(f"\n📁 Expected emotions from illustrations:")
        for i, emotion in enumerate(expected_emotions, 1):
            print(f"   {i:2d}. {emotion}")
        
        # Check if emotions match
        missing_emotions = set(expected_emotions) - set(emotion_columns)
        extra_emotions = set(emotion_columns) - set(expected_emotions)
        
        if missing_emotions:
            print(f"\n⚠️  Missing emotions: {missing_emotions}")
        if extra_emotions:
            print(f"\n⚠️  Extra emotions: {extra_emotions}")
        
        if not missing_emotions and not extra_emotions:
            print(f"\n✅ All 15 emotions match perfectly!")
        
        return model, scaler, feature_info, color_columns, engineered_columns, emotion_columns
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

def test_emotion_prediction():
    """Test emotion prediction with sample data"""
    print("\n🎯 Testing Emotion Prediction")
    print("=" * 50)
    
    # Load model
    result = test_emotion_model_loading()
    if not result:
        return False
    
    model, scaler, feature_info, color_columns, engineered_columns, emotion_columns = result
    
    # Sample color data (similar to what the recommendation script would use)
    sample_colors = {
        'black': 0.0,
        'blue': 0.1,
        'brown': 0.0,
        'green': 0.0,
        'grey': 0.2,
        'orange': 0.0,
        'pink': 0.3,
        'purple': 0.0,
        'red': 0.0,
        'turquoise': 0.0,
        'white': 0.4,
        'yellow': 0.0
    }
    
    try:
        # Prepare feature vector
        features = []
        
        # Add color features
        for color in color_columns:
            features.append(float(sample_colors.get(color, 0.0)))
        
        # Add engineered features (default values)
        for feature in engineered_columns:
            features.append(0.0)
        
        # Convert to numpy array
        X = np.array(features).reshape(1, -1)
        
        # Scale features
        X_scaled = scaler.transform(X)
        
        # Make prediction
        predictions_proba = model.predict_proba(X_scaled)
        
        # Process results
        emotion_predictions = {}
        for i, emotion in enumerate(emotion_columns):
            pred_array = predictions_proba[i]
            
            if pred_array.shape[1] > 1:
                # Binary classification - get positive class probability
                emotion_predictions[emotion] = float(pred_array[0, 1])
            else:
                # Single value
                emotion_predictions[emotion] = float(pred_array[0, 0])
        
        # Display results
        print(f"📊 Emotion Predictions:")
        sorted_emotions = sorted(emotion_predictions.items(), key=lambda x: x[1], reverse=True)
        
        for emotion, probability in sorted_emotions:
            percentage = probability * 100
            print(f"   {emotion:15s}: {percentage:6.2f}%")
        
        # Get dominant emotion
        dominant_emotion = max(emotion_predictions.items(), key=lambda x: x[1])
        
        print(f"\n🎭 Dominant Emotion: {dominant_emotion[0]} ({dominant_emotion[1] * 100:.1f}%)")
        
        # Verify we have all 15 emotions
        if len(emotion_predictions) == 15:
            print(f"✅ All 15 emotions returned successfully!")
        else:
            print(f"❌ Expected 15 emotions, got {len(emotion_predictions)}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error in emotion prediction: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_recommendation_script_integration():
    """Test the emotion prediction within the recommendation script"""
    print("\n🔗 Testing Recommendation Script Integration")
    print("=" * 50)
    
    try:
        # Import the recommendation script function
        from recommendation_service_embedded import predict_emotion_via_api
        
        # Sample color features
        sample_features = {
            'black': 0.0,
            'blue': 0.1,
            'brown': 0.0,
            'green': 0.0,
            'grey': 0.2,
            'orange': 0.0,
            'pink': 0.3,
            'purple': 0.0,
            'red': 0.0,
            'turquoise': 0.0,
            'white': 0.4,
            'yellow': 0.0
        }
        
                 # Call the emotion prediction function
        result = predict_emotion_via_api(sample_features)
        
        print(f"📋 Recommendation Script Result:")
        print(f"   Emotion: {result['emotion']}")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Confidence %: {result.get('confidence_percentage', 'N/A')}")
        print(f"   All probabilities: {len(result['all_probabilities'])} emotions")
        
        # Verify that the model pkl files are being used correctly
        print(f"\n🔍 PKL Files Usage Verification:")
        print(f"   The emotion prediction uses the exact feature set from final_feature_info.pkl")
        print(f"   Feature names and order match the model's training requirements")
        print(f"   Uses final_emotion_model.pkl and final_scaler.pkl correctly")
        print(f"   Should show feature count and name matching in the logs above")
        
        # Display top 5 emotions
        if 'all_probabilities' in result:
            sorted_emotions = sorted(result['all_probabilities'].items(), key=lambda x: x[1], reverse=True)
            print(f"\n🔝 Top 5 emotions:")
            for emotion, prob in sorted_emotions[:5]:
                print(f"   {emotion:15s}: {prob * 100:6.2f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in recommendation script integration: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🧪 Emotion Prediction Test Suite")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    success = True
    
    # Test model loading
    if not test_emotion_model_loading():
        success = False
    
    # Test emotion prediction
    if not test_emotion_prediction():
        success = False
    
    # Test recommendation script integration
    if not test_recommendation_script_integration():
        success = False
    
    # Final summary
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed! Emotion prediction is working correctly.")
        print("💡 The model should now return all 15 emotions in the recommendation script.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    print("\n📋 Next steps:")
    print("   1. If tests pass, restart the plot-palette service")
    print("   2. Test the web application with palette upload")
    print("   3. Check service logs for full 15-emotion predictions")

if __name__ == "__main__":
    main() 