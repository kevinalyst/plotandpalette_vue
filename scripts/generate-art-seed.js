#!/usr/bin/env node
/**
 * Generate SQL INSERT statements from art_information.csv
 * Usage: node scripts/generate-art-seed.js
 * Output: scripts/seed-art-info.sql
 */

const fs = require('fs');
const path = require('path');

// Read and parse CSV manually (simple CSV parser)
function parseCSV(csvContent) {
  const lines = csvContent.split('\n').filter(line => line.trim());
  const headers = lines[0].split(',');
  const data = [];
  
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i];
    const values = line.split(',');
    
    if (values.length >= 4) {
      const row = {
        id: values[0].trim(),
        artist: values[1].trim(),
        title: values[2].trim(),
        year: values[3].trim()
      };
      
      // Skip empty rows
      if (row.id && row.artist) {
        data.push(row);
      }
    }
  }
  
  return data;
}

// Escape single quotes for SQL
function escapeSql(str) {
  return str.replace(/'/g, "''");
}

// Main function
function generateSeedSQL() {
  console.log('🎨 Generating SQL seed file for art_information...\n');
  
  // Read CSV file
  const csvPath = path.join(__dirname, '../data/Chinese_Contemporary_Art/art_information.csv');
  
  if (!fs.existsSync(csvPath)) {
    console.error('❌ CSV file not found at:', csvPath);
    process.exit(1);
  }
  
  const csvContent = fs.readFileSync(csvPath, 'utf8');
  const artworks = parseCSV(csvContent);
  
  console.log(`✅ Parsed ${artworks.length} artworks from CSV\n`);
  
  // Generate SQL statements
  let sql = `-- Generated SQL seed file for art_information table
-- Generated: ${new Date().toISOString()}
-- Total artworks: ${artworks.length}

`;
  
  let successCount = 0;
  
  for (const artwork of artworks) {
    const id = parseInt(artwork.id);
    
    // Skip if ID is not a valid number or out of range
    if (isNaN(id) || id < 1 || id > 155) {
      console.log(`⚠️  Skipping invalid ID: ${artwork.id}`);
      continue;
    }
    
    const artist = escapeSql(artwork.artist);
    const title = escapeSql(artwork.title);
    const year = escapeSql(artwork.year);
    const r2_key = `paintings/chinese-contemporary/${id}.jpg`;
    
    sql += `INSERT INTO art_information (id, artist, title, year, r2_key) VALUES (${id}, '${artist}', '${title}', '${year}', '${r2_key}');\n`;
    
    successCount++;
    
    if (successCount % 20 === 0) {
      console.log(`📝 Generated ${successCount} insert statements...`);
    }
  }
  
  // Write SQL file
  const outputPath = path.join(__dirname, 'seed-art-info.sql');
  fs.writeFileSync(outputPath, sql);
  
  console.log(`\n✅ Generated ${successCount} SQL insert statements`);
  console.log(`📄 Output file: ${outputPath}`);
  console.log(`\n📋 Next steps:`);
  console.log(`   1. Apply migration: cd apps/frontend && wrangler d1 migrations apply plotandplate-db`);
  console.log(`   2. Seed database: wrangler d1 execute plotandplate-db --file=../../scripts/seed-art-info.sql`);
  console.log(`   3. Verify: wrangler d1 execute plotandplate-db --command="SELECT COUNT(*) FROM art_information"`);
}

// Run
try {
  generateSeedSQL();
} catch (error) {
  console.error('❌ Error:', error.message);
  process.exit(1);
}
