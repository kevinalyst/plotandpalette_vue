#!/usr/bin/env python3
"""
Emotion Prediction API
=====================

Multi-label emotion prediction from color features using trained model.
Based on the implementation steps from Training_Results_Summary.html

Usage:
    python emotion_prediction_api.py
"""

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Optional
import uvicorn
from datetime import datetime
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# STEP 1: Load Model Components
# ============================================================================

def load_model_components():
    """Load the trained model and preprocessing components"""
    try:
        # Load the trained model and preprocessing components
        model = joblib.load('final_emotion_model.pkl')
        scaler = joblib.load('final_scaler.pkl')
        feature_info = joblib.load('final_feature_info.pkl')
        
        # Extract feature names
        color_columns = feature_info['color_columns']
        engineered_columns = [col for col in feature_info['final_features'] 
                             if col not in color_columns]
        emotion_columns = feature_info['emotion_columns']
        
        logger.info("✅ Model components loaded successfully")
        logger.info(f"   Color features: {len(color_columns)}")
        logger.info(f"   Engineered features: {len(engineered_columns)}")
        logger.info(f"   Emotion classes: {len(emotion_columns)}")
        
        return model, scaler, feature_info, color_columns, engineered_columns, emotion_columns
        
    except FileNotFoundError as e:
        logger.error(f"❌ Model file not found: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Error loading model: {e}")
        raise

# Load model components at startup
model, scaler, feature_info, color_columns, engineered_columns, emotion_columns = load_model_components()

# ============================================================================
# STEP 2: Create Prediction Function
# ============================================================================

def predict_emotions(color_features, engineered_features=None):
    """
    Predict emotions from color and engineered features
    
    Args:
        color_features (dict): Color proportions (12 colors)
        engineered_features (dict): Engineered features (73 features)
    
    Returns:
        dict: Emotion predictions and metadata
    """
    try:
        # Prepare feature vector
        features = []
        
        # Add color features in correct order
        for color in color_columns:
            features.append(color_features.get(color, 0.0))
        
        # Add engineered features if provided
        if engineered_features:
            for feature in engineered_columns:
                features.append(engineered_features.get(feature, 0.0))
        else:
            # Use default values for engineered features
            features.extend([0.0] * len(engineered_columns))
        
        # Convert to numpy array and reshape
        X = np.array(features).reshape(1, -1)
        
        # Scale features
        X_scaled = scaler.transform(X)
        
        # Make prediction
        predictions_proba = model.predict_proba(X_scaled)
        
        # Convert to dictionary
        emotion_predictions = {}
        for i, emotion in enumerate(emotion_columns):
            # Get prediction array for this emotion
            pred_array = predictions_proba[i]
            
            # Handle 2D array (1, 2) - get probability of positive class
            if pred_array.shape[1] > 1:
                # Binary classification - get positive class probability (index 1)
                emotion_predictions[emotion] = float(pred_array[0, 1])
            else:
                # Single value - get the only probability
                emotion_predictions[emotion] = float(pred_array[0, 0])
        
        # Find dominant emotion
        dominant_emotion = max(emotion_predictions.items(), key=lambda x: x[1])
        
        # Sort emotions by confidence (highest first)
        sorted_emotions = sorted(emotion_predictions.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "predictions": emotion_predictions,
            "sorted_emotions": sorted_emotions,
            "dominant_emotion": dominant_emotion[0],
            "confidence": dominant_emotion[1],
            "total_emotions": len(emotion_predictions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Prediction error: {e}")
        raise

# ============================================================================
# STEP 3: FastAPI Implementation
# ============================================================================

app = FastAPI(
    title="🎨 Emotion Prediction API",
    description="Multi-label emotion prediction from color features using trained model",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

class ColorFeatures(BaseModel):
    """Color features model with validation"""
    black: float = Field(0.0, ge=0.0, le=1.0, description="Black color proportion")
    blue: float = Field(0.0, ge=0.0, le=1.0, description="Blue color proportion")
    brown: float = Field(0.0, ge=0.0, le=1.0, description="Brown color proportion")
    green: float = Field(0.0, ge=0.0, le=1.0, description="Green color proportion")
    grey: float = Field(0.0, ge=0.0, le=1.0, description="Grey color proportion")
    orange: float = Field(0.0, ge=0.0, le=1.0, description="Orange color proportion")
    pink: float = Field(0.0, ge=0.0, le=1.0, description="Pink color proportion")
    purple: float = Field(0.0, ge=0.0, le=1.0, description="Purple color proportion")
    red: float = Field(0.0, ge=0.0, le=1.0, description="Red color proportion")
    turquoise: float = Field(0.0, ge=0.0, le=1.0, description="Turquoise color proportion")
    white: float = Field(0.0, ge=0.0, le=1.0, description="White color proportion")
    yellow: float = Field(0.0, ge=0.0, le=1.0, description="Yellow color proportion")

class PredictionRequest(BaseModel):
    """Request model for emotion prediction"""
    colors: ColorFeatures
    engineered_features: Optional[Dict[str, float]] = Field(
        None, 
        description="Optional engineered features (73 features)"
    )

class PredictionResponse(BaseModel):
    """Response model for emotion prediction"""
    predictions: Dict[str, float] = Field(..., description="All emotion prediction probabilities")
    sorted_emotions: list = Field(..., description="Emotions sorted by confidence (highest first)")
    dominant_emotion: str = Field(..., description="Emotion with highest probability")
    confidence: float = Field(..., description="Confidence score of dominant emotion")
    total_emotions: int = Field(..., description="Total number of emotions predicted")
    timestamp: str = Field(..., description="Prediction timestamp")

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    timestamp: str = Field(..., description="Health check timestamp")
    model_info: Dict[str, str] = Field(..., description="Model information")
    
    model_config = {
        "protected_namespaces": ()
    }

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🎨 Emotion Prediction API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "predict": "/predict",
        "model_auc": str(feature_info.get('final_auc', 'N/A')),
        "features_used": str(len(color_columns) + len(engineered_columns))
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_emotions_endpoint(request: PredictionRequest):
    """Main prediction endpoint"""
    try:
        logger.info(f"📊 Received prediction request")
        
        result = predict_emotions(
            color_features=request.colors.dict(),
            engineered_features=request.engineered_features
        )
        
        logger.info(f"✅ Prediction completed. Dominant emotion: {result['dominant_emotion']} (confidence: {result['confidence']:.3f})")
        return PredictionResponse(**result)
        
    except ValueError as e:
        logger.warning(f"⚠️ Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        model_info = {
            "model_type": "GradientBoostingClassifier with MultiOutputClassifier",
            "final_auc": str(feature_info.get('final_auc', 'N/A')),
            "features_used": str(len(color_columns) + len(engineered_columns)),
            "color_features": str(len(color_columns)),
            "engineered_features": str(len(engineered_columns)),
            "emotions_predicted": str(len(emotion_columns)),
            "training_date": feature_info.get('training_date', 'N/A')
        }
        
        return HealthResponse(
            status="healthy",
            model_loaded=True,
            timestamp=datetime.now().isoformat(),
            model_info=model_info
        )
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            model_loaded=False,
            timestamp=datetime.now().isoformat(),
            model_info={"error": str(e)}
        )

@app.get("/model-info", response_model=Dict)
async def get_model_info():
    """Get detailed model information"""
    try:
        return {
            "model_type": "GradientBoostingClassifier with MultiOutputClassifier",
            "final_auc": feature_info.get('final_auc', 'N/A'),
            "features_used": len(color_columns) + len(engineered_columns),
            "color_features": color_columns,
            "engineered_features": engineered_columns[:10],  # Show first 10 only
            "total_engineered_features": len(engineered_columns),
            "emotion_classes": emotion_columns,
            "training_date": feature_info.get('training_date', 'N/A'),
            "package_versions": feature_info.get('package_versions', {})
        }
    except Exception as e:
        logger.error(f"❌ Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MAIN DEPLOYMENT FUNCTION
# ============================================================================

def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy Emotion Prediction API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes (default: 1)")
    
    args = parser.parse_args()
    
    # Print startup information
    print("=" * 60)
    print("🎨 EMOTION PREDICTION API DEPLOYMENT")
    print("=" * 60)
    print(f"Model AUC: {feature_info.get('final_auc', 'N/A')}")
    print(f"Features: {len(color_columns)} colors + {len(engineered_columns)} engineered")
    print(f"Emotions: {len(emotion_columns)}")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Workers: {args.workers}")
    print("=" * 60)
    print("🚀 Starting API server...")
    print(f"📖 API Documentation: http://{args.host}:{args.port}/docs")
    print(f"🔍 Health Check: http://{args.host}:{args.port}/health")
    print("=" * 60)
    
    try:
        # Start the server
        uvicorn.run(
            "emotion_prediction_api:app",  # ✅ Correct module name
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers if not args.reload else 1,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()
