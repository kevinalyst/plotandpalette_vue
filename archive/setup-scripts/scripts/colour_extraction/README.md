# 🎨 Batch Color Extraction for Chinese Contemporary Art

This directory contains scripts to extract dominant colors from all 155 paintings using Google Cloud Vision API.

## 📋 Prerequisites

- Python 3.8+
- Google Cloud service account with Vision API enabled
- Paintings in `data/Chinese_Contemporary_Art/paintings/` (155 JPG files)

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
cd scripts/colour_extraction

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or: venv\Scripts\activate  # On Windows

# Install required packages
pip install -r requirements.txt
```

### 2. Setup Google Cloud Credentials

Move your service account JSON file to this directory and rename it:

```bash
# Your credentials file should be:
scripts/colour_extraction/credentials.json

# The file is already gitignored for security
```

### 3. Test Run (Dry Run)

Test the script without making API calls:

```bash
python extract_colors_batch.py --dry-run
```

Expected output:
```
🎨 Extracting colors for artworks 1 to 155...
📁 Paintings directory: /path/to/paintings
📊 Mode: DRY RUN

Extracting colors: 100%|███████████████| 155/155
✅ Extraction complete!
   Successful: 155/155
```

## 🎯 Running Color Extraction

### Extract All Paintings (1-155)

```bash
python extract_colors_batch.py
```

**Time estimate:** ~8-10 minutes for 155 paintings

### Extract Specific Range

```bash
# Extract only paintings 1-50
python extract_colors_batch.py --start 1 --end 50

# Extract only paintings 51-155
python extract_colors_batch.py --start 51 --end 155
```

### Use Custom Credentials Path

```bash
python extract_colors_batch.py --credentials /path/to/credentials.json
```

## 📤 Output Files

After extraction, you'll find in `output/`:

1. **color_features.json** - Backup of all extracted data
   ```json
   {
     "1": {
       "colors": [
         {"r": 235, "g": 164, "b": 253, "percentage": 0.187},
         {"r": 143, "g": 84, "b": 181, "percentage": 0.103},
         ...
       ],
       "status": "success"
     }
   }
   ```

2. **update_local_db.sql** - SQL UPDATE statements for D1
   ```sql
   UPDATE art_information SET
     color_r_1 = 235, color_g_1 = 164, color_b_1 = 253, color_pct_1 = 0.187,
     ...
   WHERE id = 1;
   ```

3. **extraction_errors.txt** - Error log (if any failures)

## 💾 Applying to Database

### Step 1: Apply to LOCAL D1

```bash
cd ../../apps/frontend

# Apply color updates
npx wrangler d1 execute plotandplate-db --file=../../scripts/colour_extraction/output/update_local_db.sql

# Verify a sample record
npx wrangler d1 execute plotandplate-db --command="SELECT id, artist, title, color_r_1, color_g_1, color_b_1, color_pct_1 FROM art_information WHERE id=1"
```

### Step 2: Review and Verify

Check that colors look reasonable:
```bash
# View first 5 artworks with colors
npx wrangler d1 execute plotandplate-db --command="SELECT id, artist, color_r_1, color_g_1, color_b_1 FROM art_information LIMIT 5"
```

### Step 3: Apply to PRODUCTION

Once verified locally:

```bash
# Apply to remote/production database
npx wrangler d1 execute plotandplate-db --remote --file=../../scripts/colour_extraction/output/update_local_db.sql

# Verify production
npx wrangler d1 execute plotandplate-db --remote --command="SELECT COUNT(*) FROM art_information WHERE color_r_1 > 0"
```

Expected: 155 (all artworks should have colors)

## 🔍 Troubleshooting

### Google Vision API Errors

**Error:** `403 Forbidden` or `Permission Denied`
```bash
# Solution: Enable Vision API in your GCP project
# Visit: https://console.cloud.google.com/apis/library/vision.googleapis.com
```

**Error:** `401 Unauthorized` or `Could not load credentials`
```bash
# Solution: Check credentials file path and permissions
ls -la credentials.json
# Should show the file exists
```

**Error:** `429 Too Many Requests` (rate limit)
```bash
# Solution: The script already has 0.1s delay between requests
# If still hitting limits, you can:
# 1. Process in smaller batches (--start 1 --end 50, then --start 51 --end 155)
# 2. Increase delay in extract_colors_batch.py (change time.sleep(0.1) to time.sleep(0.5))
```

### Python Environment Issues

**Error:** `ModuleNotFoundError: No module named 'google'`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Error:** `Command 'python' not found`
```bash
# Solution: Use python3
python3 extract_colors_batch.py
```

## 📊 Performance

- **Processing rate:** ~0.5-1 second per painting
- **Total time:** 8-10 minutes for all  155 paintings
- **API costs:** ~$0.015 per 1000 images = ~$0.002 total (negligible)

## 🎨 Color Extraction Details

### What Gets Extracted

For each painting, the script extracts:
- **5 dominant colors** (RGB values 0-255)
- **Pixel percentages** (0.0-1.0) for each color
- Total: 20 values per artwork (5 colors × 4 properties)

### Database Schema

Colors are stored in `art_information` table:
```
color_r_1, color_g_1, color_b_1, color_pct_1  -- Color 1
color_r_2, color_g_2, color_b_2, color_pct_2  -- Color 2
color_r_3, color_g_3, color_b_3, color_pct_3  -- Color 3
color_r_4, color_g_4, color_b_4, color_pct_4  -- Color 4
color_r_5, color_g_5, color_b_5, color_pct_5  -- Color 5
```

## 🔄 Re-running Extraction

If you need to re-extract colors (e.g., after adding new paintings):

```bash
# Re-extract all
python extract_colors_batch.py

# Or just new ones
python extract_colors_batch.py --start 156 --end 200
```

The SQL will be regenerated and you can re-apply to the database.

## 📁 File Structure

```
scripts/colour_extraction/
├── extract_colors_batch.py    # Main script
├── requirements.txt            # Python dependencies
├── credentials.json            # Google Cloud credentials (gitignored)
├── .gitignore                  # Ignore credentials and outputs
├── README.md                   # This file
└── output/                     # Generated files
    ├── color_features.json     # Extracted color data (backup)
    ├── update_local_db.sql     # SQL UPDATE statements
    └── extraction_errors.txt   # Error log (if any)
```

## 🆘 Need Help?

Common issues:

1. **No paintings found:** Check that paintings exist in `data/Chinese_Contemporary_Art/paintings/`
2. **API quota exceeded:** Google Vision has generous free tier (1000 calls/month), but you can check usage in GCP Console
3. **Slow processing:** This is normal for API calls. 155 paintings × 1s each = ~3 minutes minimum

## ✅ Success Criteria

After running the script successfully, you should have:

- ✅ `output/color_features.json` with 155 artwork entries
- ✅ `output/update_local_db.sql` with 155 UPDATE statements
- ✅ No (or minimal) errors in `output/extraction_errors.txt`
- ✅ Each artwork has 5 colors with valid RGB values (0-255)

Good luck! 🎨
