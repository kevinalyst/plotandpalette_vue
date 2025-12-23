/**
 * N8N Callback API (Internal)
 * POST /api/internal/jobs/:job_id/callback
 * Receives completion callbacks from n8n workflows
 */

import type { Env, JobStatus } from '../../../../types/env';
import { successResponse, errorResponse } from '../../../_middleware';
import { updateJobStatus, saveJobResult, getJob, savePaletteAnalysis, savePaintingRecommendations } from '../../../../lib/db';
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
    
    // Save result if provided (with merging support for two-stage callbacks)
    if (body.result_data) {
      // Hydrate painting IDs if detailedRecommendations is array of numbers
      if (body.result_data.detailedRecommendations && Array.isArray(body.result_data.detailedRecommendations)) {
        const recommendations = body.result_data.detailedRecommendations;
        
        // Check if it's an array of IDs (numbers) that need hydration
        if (recommendations.length > 0 && typeof recommendations[0] === 'number') {
          console.log('🔄 Hydrating painting IDs from D1:', recommendations);
          
          try {
            // Query D1 for painting details
            const placeholders = recommendations.map(() => '?').join(',');
            const result = await env.DB
              .prepare(`SELECT id, artist, title, year, r2_key FROM art_information WHERE id IN (${placeholders})`)
              .bind(...recommendations)
              .all();
            
            // Map to frontend format, preserving order from AI selection
            const hydratedPaintings = recommendations.map((id: number) => {
              const painting = result.results.find((p: any) => p.id === id);
              if (!painting) return null;
              
              return {
                id: painting.id,
                title: painting.title,
                artist: painting.artist,
                year: painting.year,
                url: `/api/assets/${painting.r2_key}`,
                page: null
              };
            }).filter(Boolean);
            
            // Replace ID array with hydrated objects
            body.result_data.detailedRecommendations = hydratedPaintings;
            console.log('✅ Hydrated', hydratedPaintings.length, 'paintings from D1');
          } catch (hydrationError: any) {
            console.error('❌ Failed to hydrate painting IDs:', hydrationError.message);
            // Continue with IDs if hydration fails
          }
        }
      }
      
      // Get existing job to merge with previous callback data
      const existingJob = await getJob(env.DB, jobId);
      let mergedResultData = body.result_data;
      
      // If job already has result_data, merge instead of replace
      // Note: result_data is added dynamically by getJob(), not in Job type
      if (existingJob && (existingJob as any).result_data) {
        try {
          const existingResult = typeof (existingJob as any).result_data === 'string' 
            ? JSON.parse((existingJob as any).result_data) 
            : (existingJob as any).result_data;
          
          // Merge: new data takes precedence, but preserve existing fields
          mergedResultData = {
            ...existingResult,
            ...body.result_data,
            // Explicitly preserve/combine arrays
            detailedRecommendations: body.result_data.detailedRecommendations || existingResult.detailedRecommendations,
          };
          
          console.log('✅ Merged callback data with existing result');
        } catch (parseError) {
          console.warn('⚠️  Could not parse existing result_data, using new data only');
        }
      }
      
      await saveJobResult(env.DB, jobId, mergedResultData, body.r2_result_key);
      
      // Get job info once for additional saves (reuse existingJob if available)
      const jobForSaves = existingJob || await getJob(env.DB, jobId);
      
      // Save painting recommendations to dedicated table if present
      if (jobForSaves && mergedResultData.detailedRecommendations && Array.isArray(mergedResultData.detailedRecommendations)) {
        try {
          await savePaintingRecommendations(
            env.DB,
            jobForSaves.session_id,
            mergedResultData.detailedRecommendations,
            jobId
          );
          console.log('✅ Saved', mergedResultData.detailedRecommendations.length, 'recommendations to painting_recommendations table');
        } catch (recError: any) {
          console.warn('⚠️  Failed to save to painting_recommendations table:', recError.message);
        }
      }
      
      // For PALETTE_ANALYSIS jobs, also save to palette_analysis table
      // Use try-catch to make this non-blocking - if it fails, job still succeeds
      if (jobForSaves && jobForSaves.type === 'PALETTE_ANALYSIS' && body.success) {
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
