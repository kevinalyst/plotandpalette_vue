/**
 * Jobs API
 * POST /api/jobs - Create new job
 * GET /api/jobs - Get all jobs (optional: filter by session)
 */

import type { Env } from '../../types/env';
import { successResponse, errorResponse } from '../_middleware';
import { createJob, getJobsBySession } from '../../lib/db';
import { validateRequiredFields } from '../../lib/utils';

// POST /api/jobs
export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { request, env } = context;
  
  try {
    const body = await request.json() as any;
    
    // Validate required fields
    const validation = validateRequiredFields(body, ['type', 'input_data', 'session_id']);
    if (!validation.valid) {
      return errorResponse(`Missing required fields: ${validation.missing?.join(', ')}`, 400);
    }
    
    // Create job in database
    const job = await createJob(env.DB, {
      type: body.type,
      input_data: body.input_data,
      session_id: body.session_id,
      client_request_id: body.client_request_id,
    });
    
    // Trigger n8n workflow if webhook URL is configured
    if (env.N8N_WEBHOOK_URL && env.N8N_SHARED_SECRET) {
      try {
        // Convert screenshot_key to full URL if present
        const inputData = { ...body.input_data };
        if (inputData.screenshot_key) {
          const origin = new URL(request.url).origin;
          inputData.screenshot_url = `${origin}/api/assets/${inputData.screenshot_key}`;
          console.log('📸 Screenshot URL for n8n:', inputData.screenshot_url);
          // Remove the key, send URL instead
          delete inputData.screenshot_key;
        }
        
        // Send to n8n webhook
        const n8nPayload = {
          job_id: job.job_id,
          job_type: body.type,
          session_id: body.session_id,
          input_data: inputData,
          callback_url: `${new URL(request.url).origin}/api/internal/jobs/${job.job_id}/callback`,
        };
        
        console.log('📡 Sending to n8n webhook:', env.N8N_WEBHOOK_URL);
        
        const n8nResponse = await fetch(env.N8N_WEBHOOK_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Shared-Secret': env.N8N_SHARED_SECRET,
          },
          body: JSON.stringify(n8nPayload),
        });
        
        if (!n8nResponse.ok) {
          const errorText = await n8nResponse.text();
          throw new Error(`n8n webhook failed: ${n8nResponse.status} - ${errorText}`);
        }
        
        console.log('✅ n8n workflow triggered successfully');
      } catch (n8nError) {
        console.error('Failed to trigger n8n workflow:', n8nError);
        // Don't fail the request, job is created
      }
    }
    
    return successResponse({
      job_id: job.job_id,
      status: job.status,
    }, 201);
    
  } catch (error: any) {
    console.error('Error creating job:', error);
    return errorResponse(error.message || 'Failed to create job', 500);
  }
};

// GET /api/jobs?session_id=xxx
export const onRequestGet: PagesFunction<Env> = async (context) => {
  const { request, env } = context;
  
  try {
    const url = new URL(request.url);
    const sessionId = url.searchParams.get('session_id');
    
    if (!sessionId) {
      return errorResponse('session_id query parameter is required', 400);
    }
    
    const jobs = await getJobsBySession(env.DB, sessionId);
    
    return successResponse({ jobs });
    
  } catch (error: any) {
    console.error('Error getting jobs:', error);
    return errorResponse(error.message || 'Failed to get jobs', 500);
  }
};
