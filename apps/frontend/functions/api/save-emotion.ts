/**
 * Save Emotion API
 * POST /api/save-emotion - Save user's emotion selection
 * 
 * This endpoint provides backward compatibility with frontend api.js
 * which expects /save-emotion path instead of /emotions
 */

import type { Env } from '../types/env';
import { successResponse, errorResponse } from './_middleware';
import { saveEmotionSelection } from '../lib/db';

// POST /api/save-emotion
export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { request, env } = context;
  
  try {
    const body = await request.json() as any;
    const sessionId = body.sessionId || body.session_id || request.headers.get('X-Session-ID');
    
    if (!sessionId) {
      return errorResponse('Session ID is required', 400);
    }
    
    if (!body.emotion) {
      return errorResponse('Emotion is required', 400);
    }
    
    // Validate intensity if provided
    const intensity = body.intensity;
    if (intensity && !['low', 'medium', 'high'].includes(intensity)) {
      return errorResponse('Intensity must be "low", "medium", or "high"', 400);
    }
    
    await saveEmotionSelection(
      env.DB,
      sessionId,
      body.emotion,
      intensity
    );
    
    return successResponse({
      message: 'Emotion selection saved successfully',
      sessionId: sessionId,
      selectedEmotion: {
        emotion: body.emotion,
        intensity: intensity
      }
    });
    
  } catch (error: any) {
    console.error('Error saving emotion selection:', error);
    return errorResponse(error.message || 'Failed to save emotion selection', 500);
  }
};
