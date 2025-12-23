/**
 * Get Painting Recommendations by Session ID
 * GET /api/recommendations/:session_id
 */

import type { Env } from '../../types/env';
import { successResponse, errorResponse } from '../_middleware';
import { getPaintingRecommendations } from '../../lib/db';

export const onRequestGet: PagesFunction<Env> = async (context) => {
  const { params, env } = context;
  
  try {
    const sessionId = params.session_id as string;
    
    if (!sessionId) {
      return errorResponse('Session ID is required', 400);
    }
    
    // Get recommendations from D1
    const recommendations = await getPaintingRecommendations(env.DB, sessionId);
    
    if (!recommendations) {
      return errorResponse('No recommendations found for this session', 404);
    }
    
    return successResponse({
      recommendations,
      total: recommendations.length
    });
    
  } catch (error: any) {
    console.error('Error fetching recommendations:', error);
    return errorResponse(error.message || 'Failed to fetch recommendations', 500);
  }
};
