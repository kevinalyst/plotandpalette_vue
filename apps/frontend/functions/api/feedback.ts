/**
 * Feedback API
 * POST /api/feedback - Save user feedback
 */

import type { Env } from '../types/env';
import { successResponse, errorResponse } from './_middleware';
import { saveFeedback } from '../lib/db';

// POST /api/feedback
export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { request, env } = context;
  
  try {
    const body = await request.json() as any;
    const sessionId = body.session_id || request.headers.get('X-Session-ID');
    
    if (!sessionId) {
      return errorResponse('Session ID is required', 400);
    }
    
    // Save feedback with all question responses
    await saveFeedback(env.DB, sessionId, {
      q1: body.q1,
      q2: body.q2,
      q3: body.q3,
      q4: body.q4,
      q5: body.q5,
      q6: body.q6,
      q7: body.q7,
      q8: body.q8,
      q9: body.q9,
      q10: body.q10,
      q11: body.q11,
      q12: body.q12,
      q13: body.q13,
      q14: body.q14,
      q15: body.q15,
      prolific_pid: body.prolific_pid,
      prolific_study_id: body.prolific_study_id,
      prolific_session_id: body.prolific_session_id,
    });
    
    return successResponse({
      message: 'Feedback saved successfully',
      session_id: sessionId,
    });
    
  } catch (error: any) {
    console.error('Error saving feedback:', error);
    return errorResponse(error.message || 'Failed to save feedback', 500);
  }
};
