/**
 * Health Check Endpoint
 * GET /api/health
 */

import type { Env } from '../types/env';
import { successResponse } from './_middleware';

export const onRequestGet: PagesFunction<Env> = async (context) => {
  const { env } = context;
  
  return successResponse({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    environment: env.ENVIRONMENT || 'unknown',
    version: '1.0.0',
  });
};
