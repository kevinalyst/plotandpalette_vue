/**
 * Selections API
 * POST /api/selections - Save painting selection
 */

import type { Env } from '../types/env';
import { successResponse, errorResponse } from './_middleware';
import { savePaintingSelection } from '../lib/db';

// POST /api/selections
export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { request, env } = context;
  
  try {
    const body = await request.json() as any;
    const sessionId = body.session_id || request.headers.get('X-Session-ID');
    
    if (!sessionId) {
      return errorResponse('Session ID is required', 400);
    }
    
    if (!body.selected_paintings || !Array.isArray(body.selected_paintings)) {
      return errorResponse('selected_paintings array is required', 400);
    }
    
    await savePaintingSelection(
      env.DB,
      sessionId,
      body.selected_paintings,
      body.story_character,
      body.nickname
    );
    
    return successResponse({
      message: 'Selection saved successfully',
      session_id: sessionId,
    });
    
  } catch (error: any) {
    console.error('Error saving selection:', error);
    return errorResponse(error.message || 'Failed to save selection', 500);
  }
};
