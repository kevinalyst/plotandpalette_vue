/**
 * Check if username exists
 * POST /api/users/check
 */

import type { Env } from '../../types/env';
import { successResponse, errorResponse } from '../_middleware';
import { userExists } from '../../lib/db';
import { validateRequiredFields } from '../../lib/utils';

export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { request, env } = context;
  
  try {
    const body = await request.json() as any;
    
    // Validate required fields
    const validation = validateRequiredFields(body, ['username']);
    if (!validation.valid) {
      return errorResponse(`Missing required fields: ${validation.missing?.join(', ')}`, 400);
    }
    
    const exists = await userExists(env.DB, body.username);
    
    return successResponse({
      exists,
      username: body.username,
    });
    
  } catch (error: any) {
    console.error('Error checking user:', error);
    return errorResponse(error.message || 'Failed to check user', 500);
  }
};
