#!/bin/bash
# Upload Chinese Contemporary Art paintings to Cloudflare R2
# Usage: bash scripts/upload-paintings-to-r2.sh

set -e  # Exit on error

BUCKET="plotpalette-assets-prod"
PREFIX="paintings/chinese-contemporary"
PAINTINGS_DIR="data/Chinese_Contemporary_Art/paintings"

echo "🎨 Uploading Chinese Contemporary Art paintings to R2..."
echo "📦 Bucket: $BUCKET"
echo "📁 Prefix: $PREFIX"
echo ""

# Check if paintings directory exists
if [ ! -d "$PAINTINGS_DIR" ]; then
  echo "❌ Error: Paintings directory not found at $PAINTINGS_DIR"
  exit 1
fi

# Count total files
TOTAL=$(ls -1 "$PAINTINGS_DIR"/*.jpg 2>/dev/null | wc -l | tr -d ' ')
echo "📊 Found $TOTAL image files to upload"
echo ""

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
  echo "❌ Error: wrangler CLI not found. Please install it:"
  echo "   npm install -g wrangler"
  exit 1
fi

# Upload each painting
COUNT=0
FAILED=0

for i in {1..155}; do
  FILE="$PAINTINGS_DIR/${i}.jpg"
  
  if [ -f "$FILE" ]; then
    COUNT=$((COUNT + 1))
    R2_KEY="$PREFIX/${i}.jpg"
    
    echo "[$COUNT/$TOTAL] Uploading ${i}.jpg..."
    
    if wrangler r2 object put "$BUCKET/$R2_KEY" --file="$FILE" 2>/dev/null; then
      echo "  ✅ Success: $R2_KEY"
    else
      echo "  ❌ Failed: $R2_KEY"
      FAILED=$((FAILED + 1))
    fi
  else
    echo "  ⚠️  File not found: ${i}.jpg"
    FAILED=$((FAILED + 1))
  fi
  
  # Small delay to avoid rate limiting
  sleep 0.1
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Upload Summary:"
echo "   Total files: $TOTAL"
echo "   Uploaded: $((COUNT - FAILED))"
echo "   Failed: $FAILED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $FAILED -eq 0 ]; then
  echo "✅ All paintings uploaded successfully!"
  echo ""
  echo "📋 Next steps:"
  echo "   1. Verify uploads: wrangler r2 object list $BUCKET --prefix=$PREFIX"
  echo "   2. Test access: curl https://your-r2-domain/$PREFIX/1.jpg"
else
  echo "⚠️  Some uploads failed. Please check and retry."
  exit 1
fi
