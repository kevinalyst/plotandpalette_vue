/**
 * Sessions API
 * POST /api/sessions - Create new session
 * GET /api/sessions/:id - Get session by ID
 */

import type { Env } from '../../types/env';
import { successResponse, errorResponse } from '../_middleware';
import { createSession, getSession } from '../../lib/db';
import { validateRequiredFields } from '../../lib/utils';

// POST /api/sessions
export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { request, env } = context;
  
  try {
    const body = await request.json() as any;
    
    // Validate required fields
    const validation = validateRequiredFields(body, ['username']);
    if (!validation.valid) {
      return errorResponse(`Missing required fields: ${validation.missing?.join(', ')}`, 400);
    }
    
    const sessionId = await createSession(env.DB, body.username);
    
    return successResponse({
      sessionId,
      username: body.username,
    });
    
  } catch (error: any) {
    console.error('Error creating session:', error);
    return errorResponse(error.message || 'Failed to create session', 500);
  }
};

// GET /api/sessions/:id
export const onRequestGet: PagesFunction<Env> = async (context) => {
  const { params, env } = context;
  
  try {
    const sessionId = params.id as string;
    
    if (!sessionId) {
      return errorResponse('Session ID is required', 400);
    }
    
    const session = await getSession(env.DB, sessionId);
    
    if (!session) {
      return errorResponse('Session not found', 404);
    }
    
    return successResponse(session);
    
  } catch (error: any) {
    console.error('Error getting session:', error);
    return errorResponse(error.message || 'Failed to get session', 500);
  }
};
