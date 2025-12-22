/**
 * Save Selection API
 * POST /api/save-selection - Save user's painting selection
 * 
 * This endpoint provides backward compatibility with frontend api.js
 * which expects /save-selection path instead of /selections
 */

import type { Env } from '../types/env';
import { successResponse, errorResponse } from './_middleware';
import { savePaintingSelection } from '../lib/db';

// POST /api/save-selection
export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { request, env } = context;
  
  try {
    const body = await request.json() as any;
    const sessionId = body.sessionId || body.session_id || request.headers.get('X-Session-ID');
    
    if (!sessionId) {
      return errorResponse('Session ID is required', 400);
    }
    
    if (!body.selectedPaintings || !Array.isArray(body.selectedPaintings)) {
      return errorResponse('selectedPaintings array is required', 400);
    }
    
    if (body.selectedPaintings.length !== 3) {
      return errorResponse('Exactly 3 paintings must be selected', 400);
    }
    
    await savePaintingSelection(
      env.DB,
      sessionId,
      body.selectedPaintings,
      body.character,
      body.nickname
    );
    
    return successResponse({
      message: 'Selection saved successfully',
      sessionId: sessionId,
      selectedPaintings: body.selectedPaintings,
      character: body.character,
      nickname: body.nickname,
      emotion: body.emotion,
      probability: body.probability
    });
    
  } catch (error: any) {
    console.error('Error saving selection:', error);
    return errorResponse(error.message || 'Failed to save selection', 500);
  }
};
