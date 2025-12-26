/**
 * Screenshot Upload API
 * POST /api/uploads/screenshot - Upload screenshot to R2
 * Note: GET requests are handled by /api/uploads/[[path]].ts
 */

import type { Env } from '../../types/env';
import { successResponse, errorResponse } from '../_middleware';

// POST /api/uploads/screenshot
export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { request, env } = context;
  
  try {
    const body = await request.json() as any;
    
    if (!body.screenshot) {
      return errorResponse('Missing screenshot data', 400);
    }
    
    if (!body.session_id) {
      return errorResponse('Missing session_id', 400);
    }
    
    // Extract base64 data from data URL (remove "data:image/png;base64," prefix)
    const base64Data = body.screenshot.replace(/^data:image\/\w+;base64,/, '');
    
    // Convert base64 to binary
    const binaryString = atob(base64Data);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    
    // Generate unique filename with timestamp
    const timestamp = Date.now();
    const filename = `screenshots/${body.session_id}/capture-${timestamp}.png`;
    
    // Upload to R2
    await env.ASSET_BUCKET.put(filename, bytes, {
      httpMetadata: {
        contentType: 'image/png',
      },
      customMetadata: {
        session_id: body.session_id,
        palette_no: body.palette_no?.toString() || '',
        uploaded_at: new Date().toISOString(),
      },
    });
    
    console.log('✅ Screenshot uploaded to R2:', filename);
    
    return successResponse({
      key: filename,
      url: `/api/assets/${filename}`,
      size: bytes.length,
    }, 201);
    
  } catch (error: any) {
    console.error('Error uploading screenshot:', error);
    return errorResponse(error.message || 'Failed to upload screenshot', 500);
  }
};
