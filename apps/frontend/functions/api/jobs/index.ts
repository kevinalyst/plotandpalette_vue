/**
 * Jobs API
 * POST /api/jobs - Create new job
 * GET /api/jobs - Get all jobs (optional: filter by session)
 */

import type { Env } from '../../types/env';
import { successResponse, errorResponse } from '../_middleware';
import { createJob, getJobsBySession } from '../../lib/db';
import { validateRequiredFields } from '../../lib/utils';

// Helper function to convert relative URLs to public URLs
function convertToPublicUrl(url: string, origin: string): string {
  // If already a full URL, return as-is
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }
  
  // Convert relative path to absolute URL
  if (url.startsWith('/')) {
    return `${origin}${url}`;
  } else {
    return `${origin}/${url}`;
  }
}

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
    
    let enrichedInputData = { ...body.input_data };
    
    // Special handling for STORY_GENERATION: enrich from database
    if (body.type === 'STORY_GENERATION') {
      console.log('📚 Processing STORY_GENERATION job for session:', body.session_id);
      
      // 1. Query painting selection from database
      const selection = await env.DB
        .prepare('SELECT selected_paintings, story_character, nickname FROM painting_selections WHERE session_id = ? ORDER BY created_at DESC LIMIT 1')
        .bind(body.session_id)
        .first();
      
      if (!selection) {
        return errorResponse('No painting selection found for this session', 404);
      }
      
      console.log('✅ Found painting selection in database');
      
      // 2. Parse paintings from JSON
      const paintings = JSON.parse(selection.selected_paintings as string);
      
      // 3. Convert painting URLs to public URLs
      const origin = new URL(request.url).origin;
      const paintingsWithPublicUrls = paintings.map((painting: any) => ({
        ...painting,
        url: convertToPublicUrl(painting.url, origin),
        originalUrl: painting.url // Keep original for reference
      }));
      
      console.log('🌐 Converted painting URLs to public URLs:', paintingsWithPublicUrls.map((p: any) => p.url));
      
      // 4. Query emotion data
      const emotion = await env.DB
        .prepare('SELECT selected_emotion, intensity FROM emotion_selections WHERE session_id = ? ORDER BY created_at DESC LIMIT 1')
        .bind(body.session_id)
        .first();
      
      console.log('😊 Emotion data:', emotion);
      
      // 5. Enrich input data with database values
      enrichedInputData = {
        paintings: paintingsWithPublicUrls,
        character: selection.story_character,
        nickname: selection.nickname,
        emotion: emotion?.selected_emotion || 'neutral',
        intensity: emotion?.intensity || 'medium',
        sessionId: body.session_id
      };
      
      console.log('✅ Enriched story generation data:', {
        paintingCount: enrichedInputData.paintings.length,
        character: enrichedInputData.character,
        nickname: enrichedInputData.nickname,
        emotion: enrichedInputData.emotion
      });
    }
    
    // Create job in database
    const job = await createJob(env.DB, {
      type: body.type,
      input_data: enrichedInputData,
      session_id: body.session_id,
      client_request_id: body.client_request_id,
    });
    
    // Trigger n8n workflow if webhook URL is configured
    if (env.N8N_WEBHOOK_URL && env.N8N_SHARED_SECRET) {
      try {
        // Convert screenshot_key to full URL if present (for PALETTE_ANALYSIS jobs)
        const inputDataForN8n = { ...enrichedInputData };
        if (inputDataForN8n.screenshot_key) {
          const origin = new URL(request.url).origin;
          inputDataForN8n.screenshot_url = `${origin}/api/assets/${inputDataForN8n.screenshot_key}`;
          console.log('📸 Screenshot URL for n8n:', inputDataForN8n.screenshot_url);
          // Remove the key, send URL instead
          delete inputDataForN8n.screenshot_key;
        }
        
        // Send to n8n webhook
        const n8nPayload = {
          job_id: job.job_id,
          job_type: body.type,
          session_id: body.session_id,
          input_data: inputDataForN8n,
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
