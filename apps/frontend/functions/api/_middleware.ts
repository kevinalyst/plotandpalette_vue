/**
 * Cloudflare Pages Functions Middleware
 * Handles CORS, authentication, error handling
 */

import type { Env, RequestContext } from '../types/env';

// CORS headers
const corsHeaders = (origin: string) => ({
  'Access-Control-Allow-Origin': origin,
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, X-API-Key, X-Session-ID',
  'Access-Control-Max-Age': '86400',
});

// Standard JSON response helper
export function jsonResponse(data: any, status: number = 200, headers: Record<string, string> = {}): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
  });
}

// Error response helper
export function errorResponse(message: string, status: number = 500): Response {
  return jsonResponse({
    success: false,
    error: message,
  }, status);
}

// Success response helper
export function successResponse(data: any, status: number = 200): Response {
  return jsonResponse({
    success: true,
    data,
  }, status);
}

// Middleware function
export const onRequest: PagesFunction<Env> = async (context) => {
  const { request, env, next } = context;
  const url = new URL(request.url);

  // Handle CORS preflight
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      headers: corsHeaders(env.CORS_ORIGIN || '*'),
    });
  }

  // Skip auth for health/status endpoints and internal callbacks
  const publicPaths = ['/api/health', '/api/status', '/api/proxy', '/api/assets', '/api/internal'];
  const isPublic = publicPaths.some(path => url.pathname.startsWith(path));

  if (!isPublic) {
    // Check API key authentication
    const apiKey = request.headers.get('X-API-Key');
    
    if (!apiKey || apiKey !== env.API_KEY) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Unauthorized - Invalid or missing API key',
      }), {
        status: 401,
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders(env.CORS_ORIGIN || '*'),
        },
      });
    }
  }

  try {
    // Attach context to request (for use in handlers)
    const requestContext: RequestContext = {
      authenticated: !isPublic,
    };

    // Store context in a way handlers can access it
    // Note: This is a simplified approach; in production, use context.data or similar
    (request as any).context = requestContext;

    // Call next handler
    const response = await next();

    // Add CORS headers to response
    const newHeaders = new Headers(response.headers);
    Object.entries(corsHeaders(env.CORS_ORIGIN || '*')).forEach(([key, value]) => {
      newHeaders.set(key, value);
    });

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: newHeaders,
    });

  } catch (error: any) {
    console.error('Middleware error:', error);
    return new Response(JSON.stringify({
      success: false,
      error: 'Internal server error',
      message: env.ENVIRONMENT === 'development' ? error.message : undefined,
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        ...corsHeaders(env.CORS_ORIGIN || '*'),
      },
    });
  }
};
