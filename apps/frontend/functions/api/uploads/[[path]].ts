/**
 * R2 Uploads Proxy API
 * GET /api/uploads/[...path] - Serve uploaded files from R2 bucket (public, no auth)
 */

import type { Env } from '../../types/env';

export const onRequestGet: PagesFunction<Env> = async (context) => {
  const { params, env } = context;
  
  try {
    // Get the path from URL params (path is an array for catch-all routes)
    const path = Array.isArray(params.path) ? params.path.join('/') : params.path;
    
    if (!path) {
      return new Response('Path is required', { status: 400 });
    }
    
    // Fetch object from R2
    const object = await env.ASSET_BUCKET.get(path);
    
    if (!object) {
      return new Response('Upload not found', { status: 404 });
    }
    
    // Determine content type based on file extension
    const contentType = getContentType(path);
    
    // Return the file with appropriate headers
    return new Response(object.body, {
      headers: {
        'Content-Type': contentType,
        'Cache-Control': 'public, max-age=3600',
        'Access-Control-Allow-Origin': '*',
      },
    });
    
  } catch (error: any) {
    console.error('Error serving upload:', error);
    return new Response('Failed to load upload', { status: 500 });
  }
};

// Helper function to determine content type
function getContentType(path: string): string {
  const ext = path.split('.').pop()?.toLowerCase();
  
  const contentTypes: Record<string, string> = {
    'gif': 'image/gif',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'webp': 'image/webp',
    'svg': 'image/svg+xml',
    'mp4': 'video/mp4',
    'webm': 'video/webm',
  };
  
  return contentTypes[ext || ''] || 'application/octet-stream';
}
