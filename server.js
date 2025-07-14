const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs').promises;
const crypto = require('crypto');
const cors = require('cors');
const { spawn } = require('child_process');
const https = require('https');
const http = require('http');

const app = express();
const PORT = process.env.PORT || 3000;

// Create uploads directory if it doesn't exist
const uploadsDir = path.join(__dirname, 'uploads');
const publicDir = path.join(__dirname, 'public');

async function ensureDirectoryExists(dir) {
    try {
        await fs.access(dir);
    } catch {
        await fs.mkdir(dir, { recursive: true });
    }
}

// Initialize directories
(async () => {
    await ensureDirectoryExists(uploadsDir);
    await ensureDirectoryExists(publicDir);
})();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('.'));  // Serve static files from current directory
app.use('/uploads', express.static(uploadsDir)); // Serve upload files

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, uploadsDir);
    },
    filename: (req, file, cb) => {
        // Generate unique filename
        const uniqueSuffix = crypto.randomUUID();
        const timestamp = Date.now();
        cb(null, `palette-${timestamp}-${uniqueSuffix}.png`);
    }
});

const upload = multer({
    storage: storage,
    limits: {
        fileSize: 10 * 1024 * 1024, // 10MB limit
    },
    fileFilter: (req, file, cb) => {
        if (file.mimetype.startsWith('image/')) {
            cb(null, true);
        } else {
            cb(new Error('Only image files are allowed'));
        }
    }
});

// Helper function to download images
async function downloadImage(url, filename) {
    return new Promise((resolve, reject) => {
        const client = url.startsWith('https') ? https : http;
        const filePath = path.join(uploadsDir, filename);
        
        // Add timeout
        const timeout = setTimeout(() => {
            reject(new Error('Image download timeout'));
        }, 30000); // 30 second timeout
        
        const request = client.get(url, (response) => {
            clearTimeout(timeout);
            
            if (response.statusCode !== 200) {
                reject(new Error(`Failed to download image: ${response.statusCode} ${response.statusMessage}`));
                return;
            }
            
            const fileStream = require('fs').createWriteStream(filePath);
            response.pipe(fileStream);
            
            fileStream.on('finish', () => {
                fileStream.close();
                resolve(filePath);
            });
            
            fileStream.on('error', (error) => {
                clearTimeout(timeout);
                reject(error);
            });
        }).on('error', (error) => {
            clearTimeout(timeout);
            reject(error);
        });
        
        request.on('timeout', () => {
            request.destroy();
            reject(new Error('Image download timeout'));
        });
    });
}

// Routes
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Favicon route
app.get('/favicon.ico', (req, res) => {
    res.sendFile(path.join(__dirname, 'image/logo.png'));
});

// API endpoint to save palette
app.post('/api/save-palette', upload.single('image'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No image file provided' });
        }

        const colours = req.body.colours ? JSON.parse(req.body.colours) : [];
        const filename = req.file.filename;
        
        // Create metadata file
        const metadataPath = path.join(uploadsDir, `${path.parse(filename).name}.json`);
        const metadata = {
            filename: filename,
            colours: colours,
            timestamp: new Date().toISOString(),
            size: req.file.size,
            originalName: req.file.originalname
        };
        
        await fs.writeFile(metadataPath, JSON.stringify(metadata, null, 2));
        
        // Generate public URL
        const baseUrl = req.protocol + '://' + req.get('host');
        const imageUrl = `${baseUrl}/uploads/${filename}`;
        
        console.log(`Palette saved: ${filename}`);
        console.log(`Colours: ${colours.join(', ')}`);
        
        res.json({
            success: true,
            url: imageUrl,
            filename: filename,
            colours: colours,
            metadata: metadata
        });
        
    } catch (error) {
        console.error('Error saving palette:', error);
        res.status(500).json({ 
            error: 'Failed to save palette',
            message: error.message 
        });
    }
});

// API endpoint to get palette info
app.get('/api/palette/:filename', async (req, res) => {
    try {
        const filename = req.params.filename;
        const imagePath = path.join(uploadsDir, filename);
        const metadataPath = path.join(uploadsDir, `${path.parse(filename).name}.json`);
        
        // Check if files exist
        try {
            await fs.access(imagePath);
            await fs.access(metadataPath);
        } catch {
            return res.status(404).json({ error: 'Palette not found' });
        }
        
        const metadata = JSON.parse(await fs.readFile(metadataPath, 'utf8'));
        const baseUrl = req.protocol + '://' + req.get('host');
        
        res.json({
            ...metadata,
            url: `${baseUrl}/uploads/${filename}`,
            exists: true
        });
        
    } catch (error) {
        console.error('Error fetching palette info:', error);
        res.status(500).json({ 
            error: 'Failed to fetch palette info',
            message: error.message 
        });
    }
});

// API endpoint to list recent palettes
app.get('/api/recent-palettes', async (req, res) => {
    try {
        const limit = parseInt(req.query.limit) || 20;
        const files = await fs.readdir(uploadsDir);
        const jsonFiles = files.filter(file => file.endsWith('.json'));
        
        const palettes = await Promise.all(
            jsonFiles.map(async (file) => {
                try {
                    const metadata = JSON.parse(
                        await fs.readFile(path.join(uploadsDir, file), 'utf8')
                    );
                    const baseUrl = req.protocol + '://' + req.get('host');
                    return {
                        ...metadata,
                        url: `${baseUrl}/uploads/${metadata.filename}`
                    };
                } catch {
                    return null;
                }
            })
        );
        
        const validPalettes = palettes
            .filter(p => p !== null)
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
            .slice(0, limit);
            
        res.json({
            palettes: validPalettes,
            total: validPalettes.length
        });
        
    } catch (error) {
        console.error('Error fetching recent palettes:', error);
        res.status(500).json({ 
            error: 'Failed to fetch recent palettes',
            message: error.message 
        });
    }
});

// API endpoint to get painting recommendations
app.post('/api/get-recommendations', async (req, res) => {
    try {
        const { filename } = req.body;
        
        if (!filename) {
            return res.status(400).json({ error: 'Filename is required' });
        }
        
        console.log(`Getting recommendations for: ${filename}`);
        
        // Construct the full image path
        const imagePath = `uploads/${filename}`;
        
        // Check if the image file exists
        const fullImagePath = path.join(__dirname, imagePath);
        try {
            await fs.access(fullImagePath);
        } catch {
            return res.status(404).json({ error: 'Image file not found' });
        }
        
        // Modify the Python script to use the new image path
        const pythonScriptPath = path.join(__dirname, 'Recommandations/top10_recommandations.py');
        let scriptContent = await fs.readFile(pythonScriptPath, 'utf8');
        
        // Replace the IMAGE_PATH line
        const imagePathPattern = /IMAGE_PATH = ['"][^'"]*['"]/;
        const newImagePathLine = `IMAGE_PATH = '${imagePath}'`;
        
        if (imagePathPattern.test(scriptContent)) {
            scriptContent = scriptContent.replace(imagePathPattern, newImagePathLine);
        } else {
            console.error('Could not find IMAGE_PATH in Python script');
            return res.status(500).json({ error: 'Failed to update Python script' });
        }
        
        // Write the modified script to a temporary file
        const tempScriptPath = path.join(__dirname, 'Recommandations/temp_recommendations.py');
        await fs.writeFile(tempScriptPath, scriptContent);
        
        console.log('Running Python recommendation script...');
        
        // Run the Python script
        const result = await runPythonScript(tempScriptPath, fullImagePath);
        
        // Clean up temporary file
        await fs.unlink(tempScriptPath);
        
        // Use raw colors from Python output if available, otherwise fall back to JSON file
        let rawColors = result.rawColors || [];
        
        // If no raw colors from Python output, try reading from JSON file as fallback
        if (!rawColors || rawColors.length === 0) {
            try {
                const jsonFilename = filename.replace('.png', '.json');
                const jsonFilePath = path.join(__dirname, 'uploads', jsonFilename);
                console.log('No raw colors from Python, reading from JSON:', jsonFilePath);
                
                if (await fs.access(jsonFilePath).then(() => true).catch(() => false)) {
                    const jsonData = JSON.parse(await fs.readFile(jsonFilePath, 'utf8'));
                    if (jsonData.colours && Array.isArray(jsonData.colours)) {
                        // Convert hex colors to raw color format with equal percentages
                        const percentage = 1 / jsonData.colours.length;
                        rawColors = jsonData.colours.map(hexColor => ({
                            hex: hexColor,
                            percentage: percentage
                        }));
                        console.log('Found fallback hex colors:', rawColors);
                    }
                } else {
                    console.warn('JSON file not found:', jsonFilePath);
                }
            } catch (error) {
                console.error('Error reading fallback raw colors:', error);
            }
        } else {
            console.log('Using raw RGB colors from Python output:', rawColors);
        }

        console.log(`Found ${result.urls.length} recommendations`);
        console.log('Colour data:', result.colourData);
        console.log('Final raw colors for frontend:', rawColors);
        
        res.json({
            success: true,
            recommendations: result.urls,
            colourData: result.colourData,
            rawColors: rawColors,
            detailedRecommendations: result.detailedRecommendations,
            emotionPrediction: result.emotionPrediction,
            total: result.urls.length
        });
        
    } catch (error) {
        console.error('Error getting recommendations:', error);
        res.status(500).json({ 
            error: 'Failed to get recommendations',
            message: error.message 
        });
    }
});

// API endpoint to save user's selected paintings
app.post('/api/save-selection', async (req, res) => {
    try {
        const { selectedPaintings, originalFilename, sessionId } = req.body;
        
        if (!selectedPaintings || !Array.isArray(selectedPaintings) || selectedPaintings.length !== 3) {
            return res.status(400).json({ error: 'Exactly 3 selected paintings are required' });
        }
        
        if (!originalFilename) {
            return res.status(400).json({ error: 'Original filename is required' });
        }
        
        console.log(`Saving selection for ${originalFilename}:`, selectedPaintings);
        
        // Create selection metadata
        const selectionData = {
            originalFilename: originalFilename,
            sessionId: sessionId || crypto.randomUUID(),
            selectedPaintings: selectedPaintings.map(painting => ({
                url: painting.url,
                index: painting.index,
                slot: painting.slot,
                timestamp: new Date().toISOString()
            })),
            totalRecommendations: 10,
            selectionTimestamp: new Date().toISOString(),
            userAgent: req.get('User-Agent') || 'Unknown'
        };
        
        // Save selection to file
        const selectionFilename = `selection-${Date.now()}-${crypto.randomUUID().slice(0, 8)}.json`;
        const selectionPath = path.join(uploadsDir, selectionFilename);
        
        await fs.writeFile(selectionPath, JSON.stringify(selectionData, null, 2));
        
        console.log(`Selection saved to: ${selectionFilename}`);
        console.log('Selected painting URLs:');
        selectedPaintings.forEach((painting, index) => {
            console.log(`  ${index + 1}. Slot ${painting.slot + 1}: ${painting.url}`);
        });
        
        res.json({
            success: true,
            selectionId: selectionData.sessionId,
            selectionFilename: selectionFilename,
            message: 'Selection saved successfully',
            selectedPaintings: selectionData.selectedPaintings
        });
        
    } catch (error) {
        console.error('Error saving selection:', error);
        res.status(500).json({ 
            error: 'Failed to save selection',
            message: error.message 
        });
    }
});

// API endpoint to save user's emotion selection from Step 1
app.post('/api/save-emotion', async (req, res) => {
    try {
        const { emotion, probability, filename, sessionId } = req.body;
        
        if (!emotion) {
            return res.status(400).json({ error: 'Emotion is required' });
        }
        
        if (!filename) {
            return res.status(400).json({ error: 'Filename is required' });
        }
        
        console.log('🎭 EMOTION SELECTION:');
        console.log(`   User selected emotion: ${emotion}`);
        console.log(`   Probability: ${probability}%`);
        console.log(`   For palette: ${filename}`);
        console.log(`   Session ID: ${sessionId || 'anonymous'}`);
        
        // Create emotion selection metadata
        const emotionData = {
            emotion: emotion,
            probability: probability,
            filename: filename,
            sessionId: sessionId || crypto.randomUUID(),
            timestamp: new Date().toISOString(),
            userAgent: req.get('User-Agent') || 'Unknown'
        };
        
        // Save emotion selection to file
        const emotionFilename = `emotion-${Date.now()}-${crypto.randomUUID().slice(0, 8)}.json`;
        const emotionPath = path.join(uploadsDir, emotionFilename);
        
        await fs.writeFile(emotionPath, JSON.stringify(emotionData, null, 2));
        
        console.log(`   Emotion selection saved to: ${emotionFilename}`);
        
        res.json({
            success: true,
            emotionId: emotionData.sessionId,
            emotionFilename: emotionFilename,
            message: 'Emotion selection saved successfully',
            selectedEmotion: {
                emotion: emotion,
                probability: probability
            }
        });
        
    } catch (error) {
        console.error('Error saving emotion selection:', error);
        res.status(500).json({ 
            error: 'Failed to save emotion selection',
            message: error.message 
        });
    }
});

// API endpoint to get user's selection history
app.get('/api/selection-history', async (req, res) => {
    try {
        const limit = parseInt(req.query.limit) || 10;
        const files = await fs.readdir(uploadsDir);
        const selectionFiles = files.filter(file => file.startsWith('selection-') && file.endsWith('.json'));
        
        const selections = await Promise.all(
            selectionFiles.map(async (file) => {
                try {
                    const selectionData = JSON.parse(
                        await fs.readFile(path.join(uploadsDir, file), 'utf8')
                    );
                    return {
                        ...selectionData,
                        filename: file
                    };
                } catch {
                    return null;
                }
            })
        );
        
        const validSelections = selections
            .filter(s => s !== null)
            .sort((a, b) => new Date(b.selectionTimestamp) - new Date(a.selectionTimestamp))
            .slice(0, limit);
            
        res.json({
            selections: validSelections,
            total: validSelections.length
        });
        
    } catch (error) {
        console.error('Error fetching selection history:', error);
        res.status(500).json({ 
            error: 'Failed to fetch selection history',
            message: error.message 
        });
    }
});

// Helper function to check if Docker is available
function checkDockerAvailable() {
    try {
        const { execSync } = require('child_process');
        execSync('docker-compose --version', { stdio: 'ignore' });
        return true;
    } catch (error) {
        return false;
    }
}

// Helper function to run Python script and parse output
function runPythonScript(scriptPath, imagePath = null) {
    return new Promise((resolve, reject) => {
        // Always use the embedded Python script now since Python is installed in the web server container
        console.log('Using embedded Python script for recommendations');
        runContainerizedRecommendation(scriptPath, imagePath)
            .then(resolve)
            .catch(reject);
    });
}

// Helper function to run containerized recommendation service
function runContainerizedRecommendation(scriptPath, imagePath = null) {
    return new Promise((resolve, reject) => {
        const { spawn } = require('child_process');
        
        // Use the embedded Python script instead of docker-compose
        const embeddedScriptPath = path.join(__dirname, 'recommendation_service_embedded.py');
        const args = [embeddedScriptPath];
        
        if (imagePath) {
            args.push(imagePath);
        }
        
        console.log('Running embedded recommendation script:', 'python3', args);
        
        const python = spawn('python3', args, { cwd: __dirname });
        
        let stdout = '';
        let stderr = '';
        
        python.stdout.on('data', (data) => {
            stdout += data.toString();
        });
        
        python.stderr.on('data', (data) => {
            stderr += data.toString();
        });
        
        python.on('close', (code) => {
            if (code !== 0) {
                console.error('Embedded recommendation script error:', stderr);
                reject(new Error(`Embedded recommendation script failed with code ${code}: ${stderr}`));
                return;
            }
            
            console.log('Embedded recommendation script output:', stdout);
            
            // Parse the output to extract URLs, colour data, and detailed recommendations
            const { urls, colourData, rawColors, detailedRecommendations, emotionPrediction } = parseRecommendationOutput(stdout);
            resolve({
                urls: urls,
                colourData: colourData,
                rawColors: rawColors,
                detailedRecommendations: detailedRecommendations,
                emotionPrediction: emotionPrediction
            });
        });
        
        python.on('error', (error) => {
            console.error('Failed to start embedded recommendation script:', error);
            reject(error);
        });
    });
}

// Helper function to parse Python script output and extract URLs, colour data, and detailed recommendations
function parseRecommendationOutput(output) {
    const urls = [];
    const lines = output.split('\n');
    
    let inRecommendationSection = false;
    let colourData = {};
    let rawColorData = [];
    let detailedRecommendations = [];
    let emotionPrediction = null;
    
    // Parse raw extracted colors and mapped colour percentages
    for (const line of lines) {
        // Parse raw RGB colors from the new format: "  Raw Color 1: RGB(255, 165, 0) - 42.36%"
        const rawColorMatch = line.match(/\s*Raw Color \d+: RGB\((\d+), (\d+), (\d+)\) - ([\d.]+)%/);
        if (rawColorMatch) {
            const r = parseInt(rawColorMatch[1]);
            const g = parseInt(rawColorMatch[2]);
            const b = parseInt(rawColorMatch[3]);
            const percentage = parseFloat(rawColorMatch[4]) / 100; // Convert percentage to decimal
            rawColorData.push({ r, g, b, percentage });
        }
        
        // Also parse old format for backwards compatibility
        const oldRawColorMatch = line.match(/Analyzing extracted color: RGB\(.*?(\d+).*?(\d+).*?(\d+)\)/);
        if (oldRawColorMatch && rawColorData.length === 0) { // Only use if new format not found
            const r = parseInt(oldRawColorMatch[1]);
            const g = parseInt(oldRawColorMatch[2]);
            const b = parseInt(oldRawColorMatch[3]);
            rawColorData.push({ r, g, b });
        }
        
        if (line.includes('Final colour selection:')) {
            // Start parsing colour data from the next lines
            continue;
        }
        
        // Parse colour percentage lines like "  black: 0.5302"
        const colourMatch = line.match(/^\s+([a-z]+):\s+([\d.]+)$/);
        if (colourMatch) {
            const colourName = colourMatch[1];
            const percentage = parseFloat(colourMatch[2]);
            colourData[colourName] = percentage;
        }
        
        // Look for the section with recommendations
        if (line.includes('Top 10 Recommended Painting URLs')) {
            inRecommendationSection = true;
            continue;
        }
        
        if (inRecommendationSection) {
            // Look for numbered lines with URLs
            const match = line.match(/^\d+\.\s+(.+)$/);
            if (match) {
                const url = match[1].trim();
                if (url && url.startsWith('http')) {
                    urls.push(url);
                }
            }
        }
        
        // Stop if we've found URLs and hit an empty line or other content
        if (inRecommendationSection && urls.length > 0 && line.trim() === '') {
            break;
        }
    }
    
    // Raw colors now include percentages from the parsing above
    const rawColors = rawColorData;
    
    // Parse detailed recommendations JSON
    const jsonStartIndex = output.indexOf('--- DETAILED_RECOMMENDATIONS_JSON ---');
    const jsonEndIndex = output.indexOf('--- END_DETAILED_RECOMMENDATIONS_JSON ---');
    
    if (jsonStartIndex !== -1 && jsonEndIndex !== -1) {
        const jsonStr = output.substring(
            jsonStartIndex + '--- DETAILED_RECOMMENDATIONS_JSON ---'.length,
            jsonEndIndex
        ).trim();
        
        try {
            detailedRecommendations = JSON.parse(jsonStr);
            console.log(`Parsed ${detailedRecommendations.length} detailed recommendations`);
        } catch (error) {
            console.error('Error parsing detailed recommendations JSON:', error);
            // Fallback: create basic objects from URLs
            detailedRecommendations = urls.map((url, index) => ({
                url: url,
                title: `Painting ${index + 1}`,
                artist: 'Unknown Artist',
                year: 'Unknown Year'
            }));
        }
    } else {
        // Fallback: create basic objects from URLs
        detailedRecommendations = urls.map((url, index) => ({
            url: url,
            title: `Painting ${index + 1}`,
            artist: 'Unknown Artist',
            year: 'Unknown Year'
        }));
    }
    
    // Parse emotion prediction JSON
    const emotionStartIndex = output.indexOf('--- EMOTION_PREDICTION_JSON ---');
    const emotionEndIndex = output.indexOf('--- END_EMOTION_PREDICTION_JSON ---');
    
    if (emotionStartIndex !== -1 && emotionEndIndex !== -1) {
        const emotionJsonStr = output.substring(
            emotionStartIndex + '--- EMOTION_PREDICTION_JSON ---'.length,
            emotionEndIndex
        ).trim();
        
        try {
            emotionPrediction = JSON.parse(emotionJsonStr);
            console.log(`Parsed emotion prediction: ${emotionPrediction.emotion} (${emotionPrediction.confidence_percentage})`);
        } catch (error) {
            console.error('Error parsing emotion prediction JSON:', error);
            emotionPrediction = {
                emotion: 'unknown',
                confidence_percentage: '0%',
                all_probabilities: {}
            };
        }
    } else {
        // Fallback: create default emotion prediction
        emotionPrediction = {
            emotion: 'unknown',
            confidence_percentage: '0%',
            all_probabilities: {}
        };
    }
    
    return {
        urls: urls,
        colourData: colourData,
        rawColors: rawColors,
        detailedRecommendations: detailedRecommendations,
        emotionPrediction: emotionPrediction
    };
}

// API endpoint to generate story
app.post('/api/generate-story', async (req, res) => {
    try {
        const { paintings, narrative_style, user_name, emotion, emotion_probability } = req.body;
        
        if (!paintings || !Array.isArray(paintings) || paintings.length !== 3) {
            return res.status(400).json({ error: 'Exactly 3 paintings are required' });
        }
        
        if (!narrative_style) {
            return res.status(400).json({ error: 'Narrative style is required' });
        }
        
        console.log(`Generating ${narrative_style} story for paintings:`, paintings.map(p => p.title));
        if (user_name) {
            console.log(`User name: ${user_name}`);
        }
        if (emotion && emotion_probability !== undefined) {
            console.log(`Emotion: ${emotion} (${emotion_probability}%)`);
        }
        
        // Download images for each painting
        const paintingsWithImages = [];
        for (let i = 0; i < paintings.length; i++) {
            const painting = paintings[i];
            const imageFilename = `story_image_${Date.now()}_${i}.jpg`;
            
            try {
                console.log(`Downloading image ${i + 1}: ${painting.url}`);
                const imagePath = await downloadImage(painting.url, imageFilename);
                
                // Verify the downloaded file exists
                await fs.access(imagePath);
                
                paintingsWithImages.push({
                    ...painting,
                    imagePath: imagePath,
                    imageFilename: imageFilename
                });
            } catch (error) {
                console.error(`Failed to download image ${i + 1}:`, error);
                return res.status(500).json({ 
                    error: 'Failed to download painting images',
                    message: error.message 
                });
            }
        }
        
        // Prepare input for Python script with image paths and emotion data
        const inputData = {
            paintings: paintingsWithImages,
            narrative_style: narrative_style,
            user_name: user_name || '',
            emotion: emotion || null,
            emotion_probability: emotion_probability || null
        };
        
        console.log(`Generating story with ${inputData.paintings.length} paintings for user: ${inputData.user_name || 'anonymous'}`);
        if (inputData.emotion && inputData.emotion_probability !== null) {
            console.log(`Story will incorporate emotion: ${inputData.emotion} (${inputData.emotion_probability}%)`);
        }
        
        // Run Python story generator with secure wrapper
        const storyScriptPath = path.join(__dirname, 'story_generation/secure_story_generator.py');
        const result = await runPythonStoryScript(storyScriptPath, inputData);
        
        // Clean up downloaded images
        for (const painting of paintingsWithImages) {
            try {
                await fs.unlink(painting.imagePath);
                console.log(`Cleaned up image: ${painting.imageFilename}`);
            } catch (error) {
                console.error(`Failed to clean up image ${painting.imageFilename}:`, error);
            }
        }
        
        if (result.success) {
            console.log(`Story generated successfully (${result.word_count} words)`);
            res.json(result);
        } else {
            console.error('Story generation failed:', result.error);
            res.status(500).json({ 
                error: 'Failed to generate story',
                message: result.error 
            });
        }
        
    } catch (error) {
        console.error('Error generating story:', error);
        
        // Clean up downloaded images in case of error
        if (typeof paintingsWithImages !== 'undefined') {
            for (const painting of paintingsWithImages) {
                try {
                    await fs.unlink(painting.imagePath);
                    console.log(`Cleaned up image after error: ${painting.imageFilename}`);
                } catch (cleanupError) {
                    console.error(`Failed to clean up image ${painting.imageFilename}:`, cleanupError);
                }
            }
        }
        
        res.status(500).json({ 
            error: 'Failed to generate story',
            message: error.message 
        });
    }
});

// Helper function to run Python story script
function runPythonStoryScript(scriptPath, inputData) {
    return new Promise((resolve, reject) => {
        const inputJson = JSON.stringify(inputData);
        const python = spawn('python3', [scriptPath, inputJson]);
        
        let stdout = '';
        let stderr = '';
        
        python.stdout.on('data', (data) => {
            stdout += data.toString();
        });
        
        python.stderr.on('data', (data) => {
            stderr += data.toString();
        });
        
        python.on('close', (code) => {
            if (code !== 0) {
                console.error('Python story script error:', stderr);
                resolve({
                    success: false,
                    error: stderr || 'Story generation failed'
                });
                return;
            }
            
            try {
                // Log the raw output for debugging
                console.log('Raw Python output length:', stdout.length);
                console.log('Raw Python stderr:', stderr);
                
                // Try to parse the entire stdout as JSON first
                let result;
                try {
                    result = JSON.parse(stdout.trim());
                    console.log('Successfully parsed entire stdout as JSON');
                    resolve(result);
                    return;
                } catch (directParseError) {
                    console.log('Direct JSON parse failed, trying line-by-line extraction...');
                }
                
                // Extract JSON from stdout (may contain logging info)
                const lines = stdout.trim().split('\n');
                let jsonStartIndex = -1;
                let braceCount = 0;
                let jsonEndIndex = -1;
                
                // Find the first line that contains '{'
                for (let i = 0; i < lines.length; i++) {
                    if (lines[i].includes('{')) {
                        jsonStartIndex = i;
                        break;
                    }
                }
                
                if (jsonStartIndex === -1) {
                    throw new Error('No JSON start found in output');
                }
                
                // Find the matching closing brace by counting braces
                for (let i = jsonStartIndex; i < lines.length; i++) {
                    const line = lines[i];
                    for (let char of line) {
                        if (char === '{') braceCount++;
                        if (char === '}') braceCount--;
                        if (braceCount === 0 && char === '}') {
                            jsonEndIndex = i;
                            break;
                        }
                    }
                    if (jsonEndIndex !== -1) break;
                }
                
                if (jsonEndIndex === -1) {
                    throw new Error('No JSON end found in output');
                }
                
                // Extract and parse JSON
                const jsonLines = lines.slice(jsonStartIndex, jsonEndIndex + 1);
                const jsonStr = jsonLines.join('\n');
                
                console.log('Extracted JSON length:', jsonStr.length);
                console.log('JSON preview:', jsonStr.substring(0, 100) + '...');
                
                result = JSON.parse(jsonStr);
                resolve(result);
            } catch (error) {
                console.error('Error parsing story result:', error);
                console.error('Raw stdout (first 500 chars):', stdout.substring(0, 500));
                console.error('Raw stderr:', stderr);
                resolve({
                    success: false,
                    error: 'Failed to parse story generation result'
                });
            }
        });
        
        python.on('error', (error) => {
            console.error('Failed to start Python story script:', error);
            resolve({
                success: false,
                error: 'Failed to start story generator'
            });
        });
    });
}

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '1.0.0'
    });
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('Server error:', error);
    
    if (error instanceof multer.MulterError) {
        if (error.code === 'LIMIT_FILE_SIZE') {
            return res.status(400).json({ error: 'File too large' });
        }
    }
    
    res.status(500).json({ 
        error: 'Internal server error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({ error: 'Not found' });
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('SIGINT received, shutting down gracefully');
    process.exit(0);
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Gradient Palette Server running on http://localhost:${PORT}`);
    console.log(`📁 Uploads directory: ${uploadsDir}`);
    console.log(`🎨 Ready to create beautiful palettes!`);
});

module.exports = app; 