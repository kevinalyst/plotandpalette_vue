/**
 * Job Detail API
 * GET /api/jobs/:job_id - Get job by ID
 */

import type { Env } from '../../types/env';
import { successResponse, errorResponse } from '../_middleware';
import { getJob } from '../../lib/db';

// GET /api/jobs/:job_id
export const onRequestGet: PagesFunction<Env> = async (context) => {
  const { params, env } = context;
  
  try {
    const jobId = params.job_id as string;
    
    if (!jobId) {
      return errorResponse('Job ID is required', 400);
    }
    
    const job = await getJob(env.DB, jobId);
    
    if (!job) {
      return errorResponse('Job not found', 404);
    }
    
    return successResponse(job);
    
  } catch (error: any) {
    console.error('Error getting job:', error);
    return errorResponse(error.message || 'Failed to get job', 500);
  }
};
