/**
 * Painting Recommendation API - Cosine Similarity
 * Returns top 50 paintings sorted by color similarity for AI selection
 */

import type { Env } from '../../types/env';

interface RawColor {
  r: number;
  g: number;
  b: number;
  percentage: number;
}

interface PaintingCandidate {
  id: number;
  artist: string;
  title: string;
  year: string;
  r2_key: string;
  similarity_score: number;
  colors: RawColor[];
}

/**
 * Calculate cosine similarity between two color vectors
 */
function cosineSimilarity(vec1: number[], vec2: number[]): number {
  // Calculate dot product
  const dotProduct = vec1.reduce((sum, val, i) => sum + val * (vec2[i] || 0), 0);
  
  // Calculate magnitudes
  const magnitude1 = Math.sqrt(vec1.reduce((sum, val) => sum + val * val, 0));
  const magnitude2 = Math.sqrt(vec2.reduce((sum, val) => sum + val * val, 0));
  
  // Avoid division by zero
  if (magnitude1 === 0 || magnitude2 === 0) {
    return 0;
  }
  
  return dotProduct / (magnitude1 * magnitude2);
}

/**
 * Flatten color array to feature vector
 */
function colorsToVector(colors: RawColor[]): number[] {
  const vector: number[] = [];
  
  for (const color of colors) {
    vector.push(color.r, color.g, color.b, color.percentage);
  }
  
  return vector;
}

/**
 * Extract colors from database row
 */
function extractColorsFromRow(row: any): RawColor[] {
  const colors: RawColor[] = [];
  
  for (let i = 1; i <= 5; i++) {
    const r = row[`color_r_${i}`] || 0;
    const g = row[`color_g_${i}`] || 0;
    const b = row[`color_b_${i}`] || 0;
    const pct = row[`color_pct_${i}`] || 0;
    
    colors.push({ r, g, b, percentage: pct });
  }
  
  return colors;
}

/**
 * Main handler
 */
export async function onRequestPost(context: { request: Request; env: Env }) {
  const { request, env } = context;
  
  try {
    // Parse request body
    const body = await request.json() as { rawColors: RawColor[] };
    
    // Validate input
    if (!body.rawColors || !Array.isArray(body.rawColors) || body.rawColors.length !== 5) {
      return Response.json({
        success: false,
        error: 'Invalid request: rawColors must be an array of 5 colors'
      }, { status: 400 });
    }
    
    // Convert user colors to vector
    const userVector = colorsToVector(body.rawColors);
    
    // Query all artworks from D1
    const result = await env.DB
      .prepare(`
        SELECT 
          id, artist, title, year, r2_key,
          color_r_1, color_g_1, color_b_1, color_pct_1,
          color_r_2, color_g_2, color_b_2, color_pct_2,
          color_r_3, color_g_3, color_b_3, color_pct_3,
          color_r_4, color_g_4, color_b_4, color_pct_4,
          color_r_5, color_g_5, color_b_5, color_pct_5
        FROM art_information
        WHERE color_r_1 > 0
      `)
      .all();
    
    if (!result.results || result.results.length === 0) {
      return Response.json({
        success: false,
        error: 'No artworks found in database'
      }, { status: 404 });
    }
    
    // Calculate similarity scores for all paintings
    const candidates: PaintingCandidate[] = result.results.map((row: any) => {
      const paintingColors = extractColorsFromRow(row);
      const paintingVector = colorsToVector(paintingColors);
      const similarity = cosineSimilarity(userVector, paintingVector);
      
      return {
        id: row.id,
        artist: row.artist,
        title: row.title,
        year: row.year,
        r2_key: row.r2_key,
        similarity_score: Math.round(similarity * 10000) / 10000, // Round to 4 decimals
        colors: paintingColors
      };
    });
    
    // Sort by similarity score (descending) and take top 50
    const top50 = candidates
      .sort((a, b) => b.similarity_score - a.similarity_score)
      .slice(0, 50);
    
    // Return response
    return Response.json({
      success: true,
      total_candidates: top50.length,
      total_artworks_analyzed: candidates.length,
      candidates: top50
    });
    
  } catch (error) {
    console.error('Error computing recommendations:', error);
    
    return Response.json({
      success: false,
      error: 'Failed to compute recommendations',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}
