#!/usr/bin/env python3
"""
Batch Color Extraction for Chinese Contemporary Art Collection
Uses Google Cloud Vision API to extract dominant colors from 155 paintings
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple
from google.cloud import vision
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
PAINTINGS_DIR = Path("../../data/Chinese_Contemporary_Art/paintings")
OUTPUT_DIR = Path("output")
CREDENTIALS_FILE = "credentials.json"
NUM_COLORS = 5  # Extract top 5 dominant colors

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)


class ColorExtractor:
    """Google Vision API color extraction"""
    
    def __init__(self, credentials_path: str):
        """Initialize Vision API client"""
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        self.client = vision.ImageAnnotatorClient()
        self.errors = []
        self.results = {}
    
    def extract_colors(self, image_path: Path, artwork_id: int) -> List[Dict]:
        """
        Extract dominant colors from an image using Google Vision API
        
        Returns: List of dicts with r, g, b, percentage
        """
        try:
            # Read image file
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            # Create Vision API image object
            image = vision.Image(content=content)
            
            # Call Image Properties API
            response = self.client.image_properties(image=image)
            
            # Extract dominant colors
            colors = []
            dominant_colors = response.image_properties_annotation.dominant_colors.colors
            
            # Get top N colors
            for color_info in dominant_colors[:NUM_COLORS]:
                colors.append({
                    'r': int(color_info.color.red),
                    'g': int(color_info.color.green),
                    'b': int(color_info.color.blue),
                    'percentage': round(color_info.pixel_fraction, 4)
                })
            
            # Pad with zeros if less than NUM_COLORS
            while len(colors) < NUM_COLORS:
                colors.append({'r': 0, 'g': 0, 'b': 0, 'percentage': 0.0})
            
            return colors[:NUM_COLORS]
            
        except Exception as e:
            error_msg = f"ID {artwork_id}: {str(e)}"
            self.errors.append(error_msg)
            print(f"\n❌ Error extracting colors for artwork {artwork_id}: {str(e)}")
            return None
    
    def process_all_paintings(self, start_id: int = 1, end_id: int = 155, dry_run: bool = False):
        """
        Process all paintings and extract colors
        
        Args:
            start_id: Starting artwork ID
            end_id: Ending artwork ID
            dry_run: If True, don't make API calls (for testing)
        """
        print(f"🎨 Extracting colors for artworks {start_id} to {end_id}...")
        print(f"📁 Paintings directory: {PAINTINGS_DIR.resolve()}")
        print(f"🔐 Credentials: {CREDENTIALS_FILE}")
        print(f"📊 Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        print()
        
        success_count = 0
        skip_count = 0
        
        # Process each artwork
        for artwork_id in tqdm(range(start_id, end_id + 1), desc="Extracting colors"):
            image_path = PAINTINGS_DIR / f"{artwork_id}.jpg"
            
            # Check if image exists
            if not image_path.exists():
                skip_count += 1
                self.errors.append(f"ID {artwork_id}: Image file not found")
                tqdm.write(f"⚠️  Skipping {artwork_id}: File not found")
                continue
            
            # Dry run = skip API call
            if dry_run:
                self.results[artwork_id] = {
                    'colors': [{'r': 0, 'g': 0, 'b': 0, 'percentage': 0.0}] * NUM_COLORS,
                    'status': 'dry_run'
                }
                success_count += 1
                continue
            
            # Extract colors via Google Vision
            colors = self.extract_colors(image_path, artwork_id)
            
            if colors:
                self.results[artwork_id] = {
                    'colors': colors,
                    'status': 'success'
                }
                success_count += 1
            
            # Small delay to respect rate limits
            time.sleep(0.1)
        
        print(f"\n✅ Extraction complete!")
        print(f"   Successful: {success_count}/{end_id - start_id + 1}")
        print(f"   Skipped: {skip_count}")
        print(f"   Failed: {len(self.errors)}")
        
        return success_count, skip_count, len(self.errors)
    
    def save_json_backup(self, filename: str = "color_features.json"):
        """Save extracted colors to JSON file"""
        output_path = OUTPUT_DIR / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Backup saved: {output_path}")
        return output_path
    
    def generate_sql_updates(self, filename: str = "update_local_db.sql"):
        """Generate SQL UPDATE statements for D1"""
        output_path = OUTPUT_DIR / filename
        
        sql_lines = [
            "-- Generated SQL UPDATE statements for art_information table",
            f"-- Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"-- Total updates: {len(self.results)}",
            ""
        ]
        
        for artwork_id, data in sorted(self.results.items()):
            if data['status'] != 'success' and data['status'] != 'dry_run':
                continue
            
            colors = data['colors']
            
            # Build UPDATE statement
            sets = []
            for i, color in enumerate(colors, 1):
                sets.extend([
                    f"color_r_{i} = {color['r']}",
                    f"color_g_{i} = {color['g']}",
                    f"color_b_{i} = {color['b']}",
                    f"color_pct_{i} = {color['percentage']}"
                ])
            
            sql = f"UPDATE art_information SET\n  {', '.join(sets)},\n  updated_at = CURRENT_TIMESTAMP\nWHERE id = {artwork_id};\n"
            sql_lines.append(sql)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_lines))
        
        print(f"📝 SQL updates generated: {output_path}")
        print(f"   Total UPDATE statements: {len([r for r in self.results.values() if r['status'] in ['success', 'dry_run']])}")
        return output_path
    
    def generate_error_report(self, filename: str = "extraction_errors.txt"):
        """Generate error report"""
        if not self.errors:
            print("✅ No errors to report!")
            return None
        
        output_path = OUTPUT_DIR / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Color Extraction Errors\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total errors: {len(self.errors)}\n\n")
            
            for error in self.errors:
                f.write(f"- {error}\n")
        
        print(f"⚠️  Error report: {output_path}")
        return output_path


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract colors from artwork using Google Vision API')
    parser.add_argument('--dry-run', action='store_true', help='Test run without API calls')
    parser.add_argument('--start', type=int, default=1, help='Start artwork ID (default: 1)')
    parser.add_argument('--end', type=int, default=155, help='End artwork ID (default: 155)')
    parser.add_argument('--credentials', type=str, default=CREDENTIALS_FILE, help='Path to Google credentials JSON')
    
    args = parser.parse_args()
    
    # Validate credentials file
    cred_path = Path(args.credentials)
    if not cred_path.exists() and not args.dry_run:
        print(f"❌ Credentials file not found: {cred_path}")
        print(f"   Please place your Google Cloud service account JSON at:")
        print(f"   scripts/colour_extraction/credentials.json")
        sys.exit(1)
    
    # Validate paintings directory
    if not PAINTINGS_DIR.exists():
        print(f"❌ Paintings directory not found: {PAINTINGS_DIR.resolve()}")
        sys.exit(1)
    
    print("=" * 60)
    print("🎨 Batch Color Extraction - Chinese Contemporary Art")
    print("=" * 60)
    print()
    
    # Initialize extractor
    extractor = ColorExtractor(str(cred_path.resolve()))
    
    # Process paintings
    start_time = time.time()
    success, skipped, failed = extractor.process_all_paintings(
        start_id=args.start,
        end_id=args.end,
        dry_run=args.dry_run
    )
    elapsed = time.time() - start_time
    
    print()
    print("=" * 60)
    print(f"⏱️  Total time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
    print("=" * 60)
    print()
    
    # Save outputs
    print("💾 Saving results...")
    extractor.save_json_backup()
    extractor.generate_sql_updates()
    
    if extractor.errors:
        extractor.generate_error_report()
    
    print()
    print("=" * 60)
    print("📋 Next Steps:")
    print("=" * 60)
    print()
    print("1. Review the generated files in scripts/colour_extraction/output/")
    print("2. Check color_features.json for extracted data")
    print("3. Apply to LOCAL D1:")
    print("   cd apps/frontend")
    print("   npx wrangler d1 execute plotandplate-db --file=../../scripts/colour_extraction/output/update_local_db.sql")
    print()
    print("4. Verify data:")
    print('   npx wrangler d1 execute plotandplate-db --command="SELECT id, color_r_1, color_g_1, color_b_1 FROM art_information WHERE id=1"')
    print()
    print("5. After verification, apply to PRODUCTION:")
    print("   npx wrangler d1 execute plotandplate-db --remote --file=../../scripts/colour_extraction/output/update_local_db.sql")
    print()
    
    # Exit code
    if failed > 0:
        print(f"⚠️  {failed} artworks failed. Check extraction_errors.txt")
        sys.exit(1)
    else:
        print("✅ All artworks processed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
