/**
 * Cloudflare Pages Functions Environment
 * Type definitions for bindings and environment variables
 */

// Import Cloudflare Workers types
/// <reference types="@cloudflare/workers-types" />

export interface Env {
  // D1 Database binding
  DB: D1Database;
  
  // R2 Bucket binding
  ASSET_BUCKET: R2Bucket;
  
  // Environment variables
  ENVIRONMENT: string;
  N8N_WEBHOOK_URL: string;
  CORS_ORIGIN: string;
  
  // Secrets (set via wrangler secret put)
  API_KEY: string;
  N8N_SHARED_SECRET: string;
  N8N_CALLBACK_SECRET: string;
}

// Job types
export type JobType = 'PALETTE_ANALYSIS' | 'PAINTING_RECOMMENDATION' | 'STORY_GENERATION';

// Job status
export type JobStatus = 'QUEUED' | 'RUNNING' | 'SUCCEEDED' | 'FAILED';

// Job interface
export interface Job {
  job_id: string;
  session_id: string;
  type: JobType;
  status: JobStatus;
  client_request_id?: string;
  input_data: string; // JSON
  error_message?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

// API Response types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Request context for middleware
export interface RequestContext {
  session_id?: string;
  username?: string;
  authenticated: boolean;
}
