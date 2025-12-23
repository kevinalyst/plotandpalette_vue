# 🎨 Art Information Setup Guide

This guide walks you through setting up the Chinese Contemporary Art collection in your Cloudflare infrastructure.

## 📋 Prerequisites

- ✅ Wrangler CLI installed (`npm install -g wrangler`)
- ✅ Authenticated with Cloudflare (`wrangler login`)
- ✅ 155 paintings in `data/Chinese_Contemporary_Art/paintings/`
- ✅ CSV file at `data/Chinese_Contemporary_Art/art_information.csv`

## 🚀 Quick Start (All Steps)

```bash
# From project root
cd /Users/kevinlee/Desktop/plotandpalette_vue

# Step 1: Apply migration
cd apps/frontend && npx wrangler d1 migrations apply plotandplate-db

# Step 2: Seed database
npx wrangler d1 execute plotandplate-db --file=../../scripts/seed-art-info.sql

# Step 3: Verify database
npx wrangler d1 execute plotandplate-db --command="SELECT COUNT(*) FROM art_information"
npx wrangler d1 execute plotandplate-db --command="SELECT * FROM art_information LIMIT 5"

# Step 4: Upload paintings to R2
cd ../.. && bash scripts/upload-paintings-to-r2.sh

# Step 5: Verify R2 uploads
npx wrangler r2 object list plotpalette-assets-prod --prefix=paintings/chinese-contemporary | head -20
```

---

## 📖 Detailed Step-by-Step Guide

### **Step 1: Apply D1 Migration**

Creates the `art_information` table in your D1 database.

```bash
cd apps/frontend
npx wrangler d1 migrations apply plotandplate-db
```

**Expected Output:**
```
Migrations to be applied:
  - 0006_create_art_information_table.sql
✅ Successfully applied migration
```

**What this does:**
- Creates `art_information` table with 155 rows capacity
- Adds columns for basic metadata (artist, title, year)
- Adds R2 reference column
- Adds 20 color feature columns (5 colors × 4 properties)
- Creates indexes for fast queries

---

### **Step 2: Seed D1 Database**

Populates the table with 155 artworks from CSV.

```bash
# Still in apps/frontend
npx wrangler d1 execute plotandplate-db --file=../../scripts/seed-art-info.sql
```

**Expected Output:**
```
🌀 Executing on plotandplate-db (...)
🚣 Executed 155 commands in 2.34 seconds
```

**What this does:**
- Inserts 155 rows with artwork metadata
- Links each record to its R2 image path
- Sets initial color features to 0 (will be populated later)

---

### **Step 3: Verify Database**

Check that data was inserted correctly.

```bash
# Check total count
npx wrangler d1 execute plotandplate-db --command="SELECT COUNT(*) FROM art_information"

# View first 5 records
npx wrangler d1 execute plotandplate-db --command="SELECT id, artist, title, year FROM art_information LIMIT 5"

# Check specific artist
npx wrangler d1 execute plotandplate-db --command="SELECT COUNT(*) as count, artist FROM art_information GROUP BY artist"
```

**Expected Output:**
```
┌─────────┐
│ COUNT(*) │
├─────────┤
│ 155     │
└─────────┘

┌────┬─────────┬────────────┬──────┐
│ id │ artist  │ title      │ year │
├────┼─────────┼────────────┼──────┤
│ 1  │ 王玉平   │ 七零后      │ 2010 │
│ 2  │ 王玉平   │ 无题        │ 1992 │
│ 3  │ 王玉平   │ 春光        │ 1997 │
│ 4  │ 王玉平   │ 梦          │ 1992 │
│ 5  │ 王玉平   │ 梦2         │ 1992 │
└────┴─────────┴────────────┴──────┘
```

---

### **Step 4: Upload Paintings to R2**

Uploads all 155 JPG files to Cloudflare R2.

```bash
cd ../..  # Back to project root
bash scripts/upload-paintings-to-r2.sh
```

**Expected Output:**
```
🎨 Uploading Chinese Contemporary Art paintings to R2...
📦 Bucket: plotpalette-assets-prod
📁 Prefix: paintings/chinese-contemporary

📊 Found 155 image files to upload

[1/155] Uploading 1.jpg...
  ✅ Success: paintings/chinese-contemporary/1.jpg
[2/155] Uploading 2.jpg...
  ✅ Success: paintings/chinese-contemporary/2.jpg
...
[155/155] Uploading 155.jpg...
  ✅ Success: paintings/chinese-contemporary/155.jpg

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Upload Summary:
   Total files: 155
   Uploaded: 155
   Failed: 0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ All paintings uploaded successfully!
```

**Time estimate:** ~5-10 minutes (depending on internet speed)

**What this does:**
- Uploads each painting to R2 with path `paintings/chinese-contemporary/{id}.jpg`
- Preserves original filenames (1.jpg to 155.jpg)
- Validates each upload
- Provides progress feedback

---

### **Step 5: Verify R2 Uploads**

Check that images are accessible in R2.

```bash
# List first 20 paintings
npx wrangler r2 object list plotpalette-assets-prod --prefix=paintings/chinese-contemporary | head -20

# Get details of a specific painting
npx wrangler r2 object get plotpalette-assets-prod/paintings/chinese-contemporary/1.jpg --file=/tmp/test-painting.jpg

# Check file downloaded correctly
open /tmp/test-painting.jpg  # macOS
# or: xdg-open /tmp/test-painting.jpg  # Linux
```

**Expected Output:**
```
📦 plotpalette-assets-prod
├─ paintings/chinese-contemporary/1.jpg (245 KB)
├─ paintings/chinese-contemporary/2.jpg (198 KB)
├─ paintings/chinese-contemporary/3.jpg (312 KB)
...
```

---

## 🔍 Troubleshooting

### **Database Issues**

**Problem:** Migration already applied error
```bash
Error: Migration 0006 has already been applied
```
**Solution:** Skip this step, table already exists

**Problem:** SQL syntax error
```bash
Error: near "INSERT": syntax error
```
**Solution:** Regenerate seed file
```bash
node scripts/generate-art-seed.js
```

### **R2 Upload Issues**

**Problem:** Wrangler not found
```bash
wrangler: command not found
```
**Solution:** Install globally
```bash
npm install -g wrangler
wrangler login
```

**Problem:** Upload fails with 401
```bash
❌ Failed: paintings/chinese-contemporary/1.jpg
```
**Solution:** Re-authenticate
```bash
wrangler logout
wrangler login
```

**Problem:** Some files missing (< 155 uploaded)
```bash
Total files: 150
```
**Solution:** Check which files are missing
```bash
cd data/Chinese_Contemporary_Art/paintings
ls *.jpg | wc -l  # Should be 155
# Re-run upload script
```

---

## ✅ Verification Checklist

After completing all steps, verify:

- [ ] **D1 Table Created**
  ```bash
  npx wrangler d1 execute plotandplate-db --command="SELECT name FROM sqlite_master WHERE type='table' AND name='art_information'"
  ```

- [ ] **155 Records in D1**
  ```bash
  npx wrangler d1 execute plotandplate-db --command="SELECT COUNT(*) FROM art_information"
  ```

- [ ] **Sample Data Looks Correct**
  ```bash
  npx wrangler d1 execute plotandplate-db --command="SELECT * FROM art_information WHERE id=1"
  ```

- [ ] **155 Images in R2**
  ```bash
  npx wrangler r2 object list plotpalette-assets-prod --prefix=paintings/chinese-contemporary | grep ".jpg" | wc -l
  ```

- [ ] **Random Image Accessible**
  ```bash
  curl -I "https://your-r2-domain.com/paintings/chinese-contemporary/1.jpg"
  # Should return 200 OK
  ```

---

## 🎯 Next Steps

After completing this setup:

1. **Extract Color Features**
   - Use the `/api/extract-colors` endpoint
   - Process all 155 paintings
   - Update D1 records with color data

2. **Build Recommendation Function**
   - Create cosine similarity algorithm
   - Test with sample user colors
   - Benchmark performance

3. **Test End-to-End**
   - User captures palette
   - System recommends paintings
   - Verify recommendations make sense

---

## 📊 Summary

**Created:**
- ✅ `art_information` table in D1 (155 capacity)
- ✅ 155 metadata records (artist, title, year)
- ✅ 155 painting images in R2
- ✅ Indexed for fast queries

**Storage Usage:**
- D1: ~50 KB (155 rows × ~300 bytes each)
- R2: ~30-50 MB (155 images × ~200-300 KB each)

**Performance:**
- Query time: <10ms (with indexes)
- Recommendation time: <500ms (after color extraction)
- Image load time: <1s (via CDN)

**Ready for:** Color extraction → Recommendation system → Production!

---

## 🆘 Need Help?

If you encounter issues:

1. Check Cloudflare Dashboard → D1 → Browse data
2. Check Cloudflare Dashboard → R2 → Browse bucket
3. Review logs: `npx wrangler tail`
4. Test individual endpoints: `curl https://your-app.pages.dev/api/...`

Good luck! 🎨
