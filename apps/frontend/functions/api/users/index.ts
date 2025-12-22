/**
 * User Registration
 * POST /api/users
 */

import type { Env } from '../../types/env';
import { successResponse, errorResponse } from '../_middleware';
import { createUser, userExists } from '../../lib/db';
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
    
    // Check if user already exists
    const exists = await userExists(env.DB, body.username);
    if (exists) {
      return errorResponse('Username already exists', 409);
    }
    
    // Create user
    await createUser(env.DB, {
      username: body.username,
      age: body.age,
      gender: body.gender,
      field_of_study: body.field_of_study,
      frequency: body.frequency,
    });
    
    return successResponse({
      username: body.username,
      message: 'User created successfully',
    }, 201);
    
  } catch (error: any) {
    console.error('Error creating user:', error);
    return errorResponse(error.message || 'Failed to create user', 500);
  }
};
