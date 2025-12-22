/**
 * Color Extraction API
 * POST /api/extract-colors
 * Extracts dominant colors from an image using simple color quantization
 * Replaces Imagga API ($79/month) with free solution
 */

import type { Env } from '../types/env';
import { successResponse, errorResponse } from './_middleware';
import { mapToBasicColors } from '../lib/colorMapping';

/**
 * Simple color quantization using median cut algorithm
 * Extracts dominant colors from image pixel data
 */
function extractDominantColors(
  pixels: Uint8ClampedArray,
  maxColors: number = 10
): Array<{ hex: string; count: number }> {
  // Count color occurrences (simplified: round to nearest 8 values per channel to reduce unique colors)
  const colorCounts = new Map<string, number>();
  
  for (let i = 0; i < pixels.length; i += 4) {
    const r = Math.round(pixels[i] / 8) * 8;
    const g = Math.round(pixels[i + 1] / 8) * 8;
    const b = Math.round(pixels[i + 2] / 8) * 8;
    const a = pixels[i + 3];
    
    // Skip transparent pixels
    if (a < 128) continue;
    
    const hex = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    colorCounts.set(hex, (colorCounts.get(hex) || 0) + 1);
  }
  
  // Sort by count and take top N colors
  const sortedColors = Array.from(colorCounts.entries())
    .map(([hex, count]) => ({ hex, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, maxColors);
  
  return sortedColors;
}

/**
 * Convert RGB component to hex
 */
function componentToHex(c: number): string {
  const hex = Math.round(c).toString(16);
  return hex.length === 1 ? '0' + hex : hex;
}

/**
 * Parse PNG or JPEG image and extract pixel data
 * Note: This is a simplified implementation
 * For production, you might want to use @cloudflare/workers-canvas
 */
async function getImagePixels(imageBuffer: ArrayBuffer): Promise<{pixels: Uint8ClampedArray, width: number, height: number}> {
  // For now, we'll use a placeholder that returns mock data
  // In production, you'd decode the actual image
  // This requires canvas API which may need additional setup
  
  throw new Error('Canvas API required - see implementation notes');
}

export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { request, env } = context;
  
  try {
    const body = await request.json() as any;
    
    if (!body.screenshot_key) {
      return errorResponse('Missing screenshot_key', 400);
    }
    
    const screenshotKey = body.screenshot_key;
    
    console.log('🎨 Extracting colors from:', screenshotKey);
    
    // Fetch image from R2
    const imageObject = await env.ASSET_BUCKET.get(screenshotKey);
    
    if (!imageObject) {
      return errorResponse(`Image not found in R2: ${screenshotKey}`, 404);
    }
    
    // Get image as buffer
    const imageBuffer = await imageObject.arrayBuffer();
    
    console.log('📦 Image loaded from R2, size:', imageBuffer.byteLength, 'bytes');
    
    // TODO: Implement proper image decoding
    // For now, return a placeholder error with instructions
    return errorResponse(
      'Color extraction requires canvas API - use Imagga temporarily or implement @cloudflare/workers-canvas',
      501
    );
    
    /* 
    // This will work once Canvas API is set up:
    
    const { pixels } = await getImagePixels(imageBuffer);
    const dominantColors = extractDominantColors(pixels, 10);
    const totalPixels = dominantColors.reduce((sum, c) => sum + c.count, 0);
    
    // Convert to rawColors format: { "#hex": percentage }
    const rawColors: Record<string, number> = {};
    dominantColors.forEach(color => {
      rawColors[color.hex] = color.count / totalPixels;
    });
    
    // Map to basic color names
    const colourData = mapToBasicColors(rawColors);
    
    console.log('✅ Color extraction complete');
    console.log('   Raw colors:', Object.keys(rawColors).length);
    console.log('   Basic colors:', Object.keys(colourData).length);
    
    return successResponse({
      filename: screenshotKey,
      rawColors,
      colourData,
      metadata: {
        total_colors: Object.keys(rawColors).length,
        extraction_method: 'median-cut-quantization',
        extracted_at: new Date().toISOString(),
      },
    });
    */
    
  } catch (error: any) {
    console.error('Error extracting colors:', error);
    return errorResponse(error.message || 'Failed to extract colors', 500);
  }
};
