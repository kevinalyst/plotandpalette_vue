/**
 * Palette Upload API
 * POST /api/uploads/palette - Upload user's custom palette image to R2
 * 
 * Allows users to upload their own palette images for analysis
 */

import type { Env } from '../../types/env';
import { successResponse, errorResponse } from '../_middleware';
import { generateId } from '../../lib/utils';

// POST /api/uploads/palette
export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { request, env } = context;
  
  try {
    // Parse multipart form data
    const formData = await request.formData();
    const imageFile = formData.get('image') as File;
    
    if (!imageFile) {
      return errorResponse('No image file provided', 400);
    }
    
    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];
    if (!allowedTypes.includes(imageFile.type)) {
      return errorResponse('Invalid file type. Only PNG, JPEG, and WebP are allowed', 400);
    }
    
    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (imageFile.size > maxSize) {
      return errorResponse('File too large. Maximum size is 10MB', 400);
    }
    
    // Generate unique key for R2
    const timestamp = Date.now();
    const uniqueId = generateId();
    const extension = imageFile.name.split('.').pop() || 'png';
    const key = `palettes/user-upload-${timestamp}-${uniqueId}.${extension}`;
    
    console.log(`📤 Uploading user palette image to R2: ${key}`);
    
    // Upload to R2 bucket
    const arrayBuffer = await imageFile.arrayBuffer();
    await env.ASSET_BUCKET.put(key, arrayBuffer, {
      httpMetadata: {
        contentType: imageFile.type,
      },
      customMetadata: {
        originalFilename: imageFile.name,
        uploadedAt: new Date().toISOString(),
        source: 'user-upload',
      },
    });
    
    console.log(`✅ User palette image uploaded successfully: ${key}`);
    
    // Generate URL for accessing the image
    const url = `/api/assets/${key}`;
    
    return successResponse({
      key: key,
      url: url,
      filename: imageFile.name,
      size: imageFile.size,
      contentType: imageFile.type,
      message: 'Palette image uploaded successfully'
    }, 201);
    
  } catch (error: any) {
    console.error('Error uploading palette image:', error);
    return errorResponse(error.message || 'Failed to upload palette image', 500);
  }
};
