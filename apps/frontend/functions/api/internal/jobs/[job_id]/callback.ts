/**
 * N8N Callback API (Internal)
 * POST /api/internal/jobs/:job_id/callback
 * Receives completion callbacks from n8n workflows
 */

import type { Env, JobStatus } from '../../../../types/env';
import { successResponse, errorResponse } from '../../../_middleware';
import { updateJobStatus, saveJobResult, getJob, savePaletteAnalysis } from '../../../../lib/db';
import { verifyN8nCallback } from '../../../../lib/n8n';

// POST /api/internal/jobs/:job_id/callback
export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { request, params, env } = context;
  
  try {
    const jobId = params.job_id as string;
    
    if (!jobId) {
      return errorResponse('Job ID is required', 400);
    }
    
    const body = await request.json() as any;
    
    // Verify HMAC signature if callback secret is configured
    if (env.N8N_CALLBACK_SECRET) {
      const signature = request.headers.get('X-N8N-Signature');
      
      if (!signature || !verifyN8nCallback(body, signature, env.N8N_CALLBACK_SECRET)) {
        return errorResponse('Invalid signature', 401);
      }
    }
    
    // Update job status
    const status = (body.success ? 'COMPLETED' : 'FAILED') as JobStatus;
    await updateJobStatus(env.DB, jobId, status, {
      completed_at: new Date().toISOString(),
      error_message: body.error_message,
    });
    
    // Save result if provided
    if (body.result_data) {
      await saveJobResult(env.DB, jobId, body.result_data, body.r2_result_key);
      
      // For PALETTE_ANALYSIS jobs, also save to palette_analysis table
      // Use try-catch to make this non-blocking - if it fails, job still succeeds
      const job = await getJob(env.DB, jobId);
      if (job && job.type === 'PALETTE_ANALYSIS' && body.success) {
        try {
          await savePaletteAnalysis(env.DB, jobId, {
            filename: body.result_data.filename,
            colour_data: body.result_data.colourData,
            raw_colors: body.result_data.rawColors,
            emotion_intensity: body.result_data.emotionPrediction?.all_intensities,
            cluster_0: body.result_data.clusters?.cluster_0,
            cluster_1: body.result_data.clusters?.cluster_1,
            cluster_2: body.result_data.clusters?.cluster_2,
            cluster_3: body.result_data.clusters?.cluster_3,
            cluster_4: body.result_data.clusters?.cluster_4,
          });
          console.log('✅ Saved PALETTE_ANALYSIS results to palette_analysis table (including clusters)');
        } catch (paletteError: any) {
          // Log but don't fail - palette_analysis is derived data
          console.warn('⚠️ Failed to save to palette_analysis table:', paletteError.message);
          console.warn('   Job results are still saved in job_results table');
        }
      }
    }
    
    return successResponse({
      message: 'Callback processed successfully',
      job_id: jobId,
      status,
    });
    
  } catch (error: any) {
    console.error('Error processing n8n callback:', error);
    return errorResponse(error.message || 'Failed to process callback', 500);
  }
};
