/**
 * Store Username (Backward compatibility endpoint)
 * POST /api/store-username
 * Creates user and session
 */

import type { Env } from '../types/env';
import { successResponse, errorResponse } from './_middleware';
import { createUser, createSession, userExists } from '../lib/db';
import { validateRequiredFields } from '../lib/utils';

export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { request, env } = context;
  
  try {
    const body = await request.json() as any;
    
    // Accept both 'username' and 'name' for backward compatibility
    const username = body.username || body.name;
    
    if (!username) {
      return errorResponse('Missing required fields: username', 400);
    }
    
    // Check if user already exists
    const exists = await userExists(env.DB, username);
    
    if (!exists) {
      // Create new user
      await createUser(env.DB, {
        username: username,
        age: body.age,
        gender: body.gender,
        field_of_study: body.fieldOfStudy || body.field_of_study,
        frequency: body.frequency,
      });
    }
    
    // Create new session for this user
    const sessionId = await createSession(env.DB, username);
    
    return successResponse({
      success: true,
      sessionId: sessionId,
      username: username,
      message: exists ? 'User found, new session created' : 'User created with new session',
    });
    
  } catch (error: any) {
    console.error('Error in store-username:', error);
    return errorResponse(error.message || 'Failed to store username', 500);
  }
};
