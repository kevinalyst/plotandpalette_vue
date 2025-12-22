/**
 * Emotions API
 * POST /api/emotions - Save emotion data
 */

import type { Env } from '../types/env';
import { successResponse, errorResponse } from './_middleware';
import { saveEmotionSelection, savePaletteAnalysis } from '../lib/db';

// POST /api/emotions
export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { request, env } = context;
  
  try {
    const body = await request.json() as any;
    const sessionId = body.session_id || request.headers.get('X-Session-ID');
    
    if (!sessionId) {
      return errorResponse('Session ID is required', 400);
    }
    
    // Save emotion selection if provided
    if (body.selected_emotion) {
      // Validate intensity if provided
      const intensity = body.intensity;
      if (intensity && !['low', 'medium', 'high'].includes(intensity)) {
        return errorResponse('Intensity must be "low", "medium", or "high"', 400);
      }
      
      await saveEmotionSelection(
        env.DB,
        sessionId,
        body.selected_emotion,
        intensity
      );
    }
    
    // Save palette analysis if provided
    if (body.palette_data) {
      await savePaletteAnalysis(env.DB, sessionId, {
        gif_name: body.gif_name,
        colour_data: body.colour_data,
        raw_colors: body.raw_colors,
        emotion_scores: body.emotion_scores,
      });
    }
    
    return successResponse({
      message: 'Emotion data saved successfully',
      session_id: sessionId,
    });
    
  } catch (error: any) {
    console.error('Error saving emotion data:', error);
    return errorResponse(error.message || 'Failed to save emotion data', 500);
  }
};
