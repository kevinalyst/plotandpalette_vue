// IMMEDIATE DEBUG: Check if script loads
console.log('🔥 SCRIPT.JS STARTING TO LOAD');
console.log('Current time:', new Date().toLocaleTimeString());
console.log('Document ready state:', document.readyState);

// Ensure title is set correctly
document.title = 'Plot & Palette';

// Colour palette in LAB colour space for better perceptual uniformity
const LAB_COLOURS = [
    [70, 40, 60],    // Bright Red
    [60, -50, 40],   // Vibrant Green  
    [50, 20, -70],   // Deep Blue
    [80, 60, 80],    // Orange
    [40, 70, -50],   // Purple
    [90, -20, 90],   // Yellow
    [30, 50, -80],   // Indigo
    [85, -30, 50],   // Light Green
    [65, 50, -30],   // Pink
    [45, -40, -50],  // Cyan
    [75, 40, 70],    // Coral
    [25, 40, -70],   // Navy
    [55, -70, 60],   // Emerald
    [95, 5, 30],     // Cream
    [15, 10, 10],    // Dark Gray
    [65, -60, 30],   // Sage
    [85, 80, 50],    // Bright Orange
    [55, -30, 80],   // Lime
    [35, 60, -60],   // Magenta
    [75, -40, 70]    // Gold
];

console.log('✅ LAB_COLOURS loaded successfully');

class GradientPalette {
    constructor() {
        this.currentColours = [];
        this.isAnimating = true;
        this.gradientContainer = document.getElementById('gradient-container');
        this.animatedGifElement = document.getElementById('animated-gif');
        this.stopButton = document.getElementById('stop-btn');
        this.startButton = document.getElementById('start-btn');
        this.homepage = document.getElementById('homepage');
        this.modal = document.getElementById('result-modal');
        this.loading = document.getElementById('loading');
        this.resultUrl = document.getElementById('result-url');
        this.isCapturing = false;
        this.colourChart = null;
        this.floatingColourChart = null; // Add floating chart reference
        this.currentFilename = null;
        this.currentColourData = null; // Store color data for later use
        this.currentRecommendations = [];
        this.selectedPaintings = [];
        this.selectedCharacter = null; // Track selected character
        this.userName = ''; // Track user's name
        this.sessionId = null; // Track session ID for server communication
        
        // Step completion tracking for gallery validation
        this.step2Complete = false; // Step 2: Drag and drop 3 paintings
        this.step3Complete = false; // Step 3: Select a character
        
        // Auto-scroll properties for drag and drop
        this.isAutoScrolling = false;
        this.autoScrollInterval = null;
        this.autoScrollDirection = null;
        this.autoScrollSpeed = 0;
        this.mouseMoveHandler = null;
        this.currentMouseX = 0;
        this.currentMouseY = 0;
        
        // Color change interval
        this.colourChangeInterval = null;
        
        // Prompt animation interval
        this.promptAnimationInterval = null;
        
        // Global drag event handlers
        this.globalDragOverHandler = null;
        this.globalDragHandler = null;
        this.globalMouseMoveHandler = null;
        
        // Processing animation properties
        this.processingSteps = [
            'Analysing colour composition...',
            'Matching artistic styles...',
            'Curating recommendations...',
            'Finalizing selections...'
        ];
        this.currentProcessingStep = 0;
        this.processingInterval = null;
        
        // Story loading timeout
        this.storyLoadingTimeout = null;
        
        // GIF cycling properties for random background animations
        this.allGifs = Array.from({length: 30}, (_, i) => `palette GIF/${i + 1}.gif`);
        this.currentGifOrder = [];
        this.currentGifIndex = 0;
        this.gifCyclingInterval = null;
        this.currentlyDisplayedGif = '';
        this.gifSwitchDuration = 4000; // Switch GIF every 4 seconds
        
        this.init();
    }

    init() {
        this.detectAndOptimizeForChrome();
        this.generateRandomColours();
        this.applyColoursToCSS();
        this.setupEventListeners();
        this.addPeriodicColourChange();
        this.preventScrollOnHomepage();
        
        // Initialize capture button as hidden
        if (this.stopButton) {
            this.stopButton.style.opacity = '0';
            this.stopButton.style.visibility = 'hidden';
        }
        
        // Update capture prompt font styling
        this.updateCapturePromptStyling();
        
        // Force a repaint to ensure colours are visible
        setTimeout(() => {
            this.applyColoursToCSS();
        }, 100);
    }
    
    // Chrome-specific optimizations
    detectAndOptimizeForChrome() {
        // Debug browser info
        console.log('Browser detection info:');
        console.log('User Agent:', navigator.userAgent);
        console.log('Vendor:', navigator.vendor);
        
        // More comprehensive Chrome detection
        const isChrome = (
            /Chrome/.test(navigator.userAgent) && 
            /Google Inc/.test(navigator.vendor)
        ) || (
            /Chrome/.test(navigator.userAgent) && 
            navigator.vendor === 'Google Inc.'
        ) || (
            navigator.userAgent.includes('Chrome') &&
            !navigator.userAgent.includes('Edg') &&
            !navigator.userAgent.includes('OPR')
        );
        
        console.log('Chrome detected:', isChrome);
        
        if (isChrome) {
            console.log('✅ Chrome detected - applying Chrome-specific optimizations');
            
            // Force hardware acceleration and proper layer creation
            this.gradientContainer.style.willChange = 'background-position, transform';
            this.gradientContainer.style.transform = 'translateZ(0)';
            this.gradientContainer.style.isolation = 'isolate';
            
            // Fix Chrome's stacking context issues
            this.gradientContainer.style.webkitTransform = 'translate3d(0, 0, 0)';
            this.gradientContainer.style.webkitBackfaceVisibility = 'hidden';
            this.gradientContainer.style.webkitPerspective = '1000px';
            
            // Force Chrome to respect layer boundaries
            document.body.style.webkitTransformStyle = 'preserve-3d';
            
            // Add Chrome-specific class for CSS targeting
            this.gradientContainer.classList.add('chrome-optimized');
            
            // Force immediate composite layer creation
            this.gradientContainer.style.webkitFontSmoothing = 'antialiased';
            this.gradientContainer.style.mozOsxFontSmoothing = 'grayscale';
            
            // Prevent Chrome rendering bugs with gradients
            this.gradientContainer.style.backgroundAttachment = 'fixed';
            
            console.log('✅ Chrome optimizations successfully applied');
            console.log('Applied styles:', {
                willChange: this.gradientContainer.style.willChange,
                transform: this.gradientContainer.style.transform,
                isolation: this.gradientContainer.style.isolation
            });
        } else {
            console.log('❌ Chrome not detected - using standard rendering');
            console.log('Browser appears to be:', this.detectBrowserName());
            
            // Apply optimizations anyway for testing
            console.log('🔧 Applying optimizations anyway for testing...');
            this.gradientContainer.style.willChange = 'background-position, transform';
            this.gradientContainer.style.transform = 'translateZ(0)';
            this.gradientContainer.style.isolation = 'isolate';
            this.gradientContainer.style.webkitTransform = 'translate3d(0, 0, 0)';
            this.gradientContainer.classList.add('chrome-optimized');
        }
    }
    
    // Helper function to detect browser name
    detectBrowserName() {
        const userAgent = navigator.userAgent;
        if (userAgent.includes('Firefox')) return 'Firefox';
        if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) return 'Safari';
        if (userAgent.includes('Edge')) return 'Edge';
        if (userAgent.includes('Opera') || userAgent.includes('OPR')) return 'Opera';
        if (userAgent.includes('Chrome')) return 'Chrome (or Chromium-based)';
        return 'Unknown';
    }

    // LAB to XYZ colour space conversion
    labToXyz(l, a, b) {
        let y = (l + 16) / 116;
        let x = a / 500 + y;
        let z = y - b / 200;

        const xyz = [x, y, z].map(value => {
            const cubed = Math.pow(value, 3);
            return cubed > 0.008856 ? cubed : (value - 16/116) / 7.787;
        });

        // D65 illuminant
        return [
            xyz[0] * 95.047,
            xyz[1] * 100.000,
            xyz[2] * 108.883
        ];
    }

    // XYZ to RGB colour space conversion
    xyzToRgb(x, y, z) {
        x /= 100;
        y /= 100;
        z /= 100;

        let r = x *  3.2406 + y * -1.5372 + z * -0.4986;
        let g = x * -0.9689 + y *  1.8758 + z *  0.0415;
        let b = x *  0.0557 + y * -0.2040 + z *  1.0570;

        const rgb = [r, g, b].map(value => {
            const adjusted = value > 0.0031308 
                ? 1.055 * Math.pow(value, 1/2.4) - 0.055
                : 12.92 * value;
            return Math.max(0, Math.min(1, adjusted));
        });

        return rgb.map(value => Math.round(value * 255));
    }

    // Complete LAB to RGB conversion
    labToRgb(l, a, b) {
        const [x, y, z] = this.labToXyz(l, a, b);
        return this.xyzToRgb(x, y, z);
    }

    // Convert RGB array to hex string
    rgbToHex(r, g, b) {
        return '#' + [r, g, b].map(x => {
            const hex = x.toString(16);
            return hex.length === 1 ? '0' + hex : hex;
        }).join('');
    }

    // Generate 5 random colours from the LAB palette
    generateRandomColours() {
        // No longer generating dynamic colors since we're using a static GIF background
        // Keep method for compatibility but don't generate actual colors
        this.currentColours = [];
    }

    // Apply colours to CSS custom properties
    applyColoursToCSS() {
        // No longer applying dynamic colors since we're using a static GIF background
        // Keep method for compatibility but don't apply any CSS changes
        return;
    }

    // Update capture prompt font styling
    updateCapturePromptStyling() {
        // Update "Step 1:" styling to 1.2rem Poppins Bold
        const promptSteps = document.querySelectorAll('.prompt-step');
        promptSteps.forEach(step => {
            step.style.fontFamily = "'Poppins', sans-serif";
            step.style.fontWeight = '700'; // Bold
            step.style.fontSize = '1.2rem';
        });

        // Update descriptive text styling to 1.2rem Poppins Regular  
        const promptTexts = document.querySelectorAll('.prompt-text');
        promptTexts.forEach(text => {
            text.style.fontFamily = "'Poppins', sans-serif";
            text.style.fontWeight = '400'; // Regular
            text.style.fontSize = '1.2rem';
        });

        console.log('🎨 Capture prompt font styling updated: Step text = 1.2rem Poppins Bold, Description = 1.2rem Poppins Regular');
    }

    // Smoothly transition to new colours
    transitionToNewColours() {
        // No longer transitioning colors since we're using a static GIF background
        // Keep method for compatibility but don't perform any transitions
        return;
    }

    // Add periodic colour changes for more dynamic animation
    addPeriodicColourChange() {
        // No longer using periodic color changes since we're using a static GIF background
        // Keep method for compatibility but don't start any intervals
        console.log('🎨 Color change disabled - using static GIF background');
        return;
    }

    // Generate random order of GIFs for cycling
    generateRandomGifOrder() {
        // Create a shuffled copy of all GIFs
        this.currentGifOrder = [...this.allGifs].sort(() => Math.random() - 0.5);
        this.currentGifIndex = 0;
        console.log('🎲 Generated random GIF order:', this.currentGifOrder.map(gif => gif.split('/').pop()));
    }

    // Switch to next GIF in the random order
    switchToNextGif() {
        if (this.currentGifOrder.length === 0) {
            this.generateRandomGifOrder();
        }
        
        const nextGif = this.currentGifOrder[this.currentGifIndex];
        this.currentlyDisplayedGif = nextGif;
        
        // Update animated GIF element instead of background image for proper frame capture
        if (this.animatedGifElement) {
            this.animatedGifElement.src = nextGif;
            this.animatedGifElement.style.display = 'block';
            this.animatedGifElement.classList.add('visible');
            this.animatedGifElement.classList.remove('hidden');
        }
        
        // Clear any background image to avoid conflicts
        if (this.gradientContainer) {
            this.gradientContainer.style.backgroundImage = 'none';
        }
        
        console.log(`🎬 Switched to GIF: ${nextGif.split('/').pop()} (${this.currentGifIndex + 1}/${this.currentGifOrder.length})`);
        
        // Move to next GIF, loop back to start if at end
        this.currentGifIndex = (this.currentGifIndex + 1) % this.currentGifOrder.length;
        
        // If we've completed one full cycle, generate a new random order
        if (this.currentGifIndex === 0) {
            console.log('🔄 Completed full GIF cycle, generating new random order...');
            this.generateRandomGifOrder();
        }
    }

    // Start GIF cycling animation
    startGifCycling() {
        // Stop any existing cycling
        this.stopGifCycling();
        
        // Generate initial random order and display first GIF
        this.generateRandomGifOrder();
        this.switchToNextGif();
        
        // Set up interval to switch GIFs
        this.gifCyclingInterval = setInterval(() => {
            if (this.isAnimating) { // Only cycle if animation is active
                this.switchToNextGif();
            }
        }, this.gifSwitchDuration);
        
        console.log(`🎬 Started GIF cycling with ${this.gifSwitchDuration}ms intervals`);
    }

    // Stop GIF cycling animation
    stopGifCycling() {
        if (this.gifCyclingInterval) {
            clearInterval(this.gifCyclingInterval);
            this.gifCyclingInterval = null;
            console.log('⏹️ Stopped GIF cycling');
        }
    }

    // Get current GIF for capture purposes
    getCurrentGifPath() {
        return this.currentlyDisplayedGif || this.allGifs[0]; // Fallback to first GIF
    }

    // Setup all event listeners
    setupEventListeners() {
        this.stopButton.addEventListener('click', () => this.stopAndCapture());
        
        // START button functionality
        this.startButton.addEventListener('click', () => this.scrollToGradientPage());
        
        // Logo refresh button functionality
        const logoRefreshBtn = document.getElementById('logo-refresh-btn');
        if (logoRefreshBtn) {
            logoRefreshBtn.addEventListener('click', () => {
                location.reload();
            });
        }

        // Keyboard shortcut for refresh (Command+Shift+R)
        document.addEventListener('keydown', (e) => {
            if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.code === 'KeyR') {
                e.preventDefault();
                location.reload();
            }
        });
        
        document.getElementById('restart-btn').addEventListener('click', () => {
            this.hideModal();
            this.restart();
        });
        
        document.getElementById('copy-btn').addEventListener('click', () => {
            this.copyUrlToClipboard();
        });
        
        document.getElementById('close-modal').addEventListener('click', () => {
            this.hideModal();
        });
        
        // Continue to gallery button functionality
        document.getElementById('continue-to-gallery-btn').addEventListener('click', () => {
            this.continueToGallery();
        });

        // Close modal when clicking outside
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.hideModal();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && this.isAnimating) {
                e.preventDefault();
                this.stopAndCapture();
            } else if (e.code === 'Escape' && this.modal.classList.contains('visible')) {
                this.hideModal();
            }
            // Removed arrow key scroll prevention to allow natural scrolling
        });
    }

    // Reset button state to default
    resetButtonState() {
        this.stopButton.disabled = false;
        this.stopButton.textContent = 'Capture';
        this.stopButton.style.setProperty('opacity', '1', 'important');
        this.stopButton.style.setProperty('visibility', 'visible', 'important');
    }

    // Stop animation and capture image
    async stopAndCapture() {
        if (!this.isAnimating) return;
        
        // Stop the capture prompt animation
        this.stopCapturePromptAnimation();
        
        console.log(`🎬 Capturing current frame of GIF (${this.getCurrentGifPath().split('/').pop()})...`);
        
        // CRITICAL: Capture the EXACT current visual frame BEFORE making any changes
        // This ensures we get the exact frame the user sees when they click Capture
        let capturedCanvas;
        try {
            // Temporarily hide UI elements for clean capture
            const elementsToHide = [
                this.stopButton,
                document.querySelector('.controls'),
                document.querySelector('.capture-prompt')
            ].filter(el => el);
            
            elementsToHide.forEach(el => {
                if (el) el.style.visibility = 'hidden';
            });
            
            // Capture the exact current frame immediately
            capturedCanvas = await html2canvas(this.gradientContainer, {
                width: this.gradientContainer.offsetWidth,
                height: this.gradientContainer.offsetHeight,
                scale: 1,
                useCORS: true,
                allowTaint: true,
                backgroundColor: null,
                logging: false,
                foreignObjectRendering: false
            });
            
            // Restore UI elements
            elementsToHide.forEach(el => {
                if (el) el.style.visibility = 'visible';
            });
            
            console.log('✅ Successfully captured exact GIF frame');
            
        } catch (error) {
            console.error('❌ Failed to capture current frame:', error);
            // Restore UI elements on error
            const elementsToShow = [
                this.stopButton,
                document.querySelector('.controls'),
                document.querySelector('.capture-prompt')
            ].filter(el => el);
            
            elementsToShow.forEach(el => {
                if (el) el.style.visibility = 'visible';
            });
            
            this.showError('Failed to capture the current frame. Please try again.');
            return;
        }
        
        // NOW stop GIF cycling and freeze with the captured frame
        this.stopGifCycling();
        
        // Convert captured canvas to data URL and replace animated GIF with static captured frame
        const capturedFrameDataURL = capturedCanvas.toDataURL('image/png', 0.9);
        
        // Hide the animated GIF element and show static captured frame as background
        if (this.animatedGifElement) {
            this.animatedGifElement.style.display = 'none';
            this.animatedGifElement.classList.remove('visible');
            this.animatedGifElement.classList.add('hidden');
        }
        
        // Display the captured frame as background for visual feedback
        this.gradientContainer.style.backgroundImage = `url(${capturedFrameDataURL})`;
        this.gradientContainer.style.backgroundSize = 'cover';
        this.gradientContainer.style.backgroundPosition = 'center';
        this.gradientContainer.style.backgroundRepeat = 'no-repeat';
        
        console.log('🔒 Replaced animated GIF with captured static frame');
        
        // Store the captured canvas for direct upload (this is the exact frame)
        this.capturedState = {
            canvas: capturedCanvas,
            dataURL: capturedFrameDataURL,
            timestamp: Date.now()
        };
        
        // Mark animation as stopped
        this.isAnimating = false;
        this.gradientContainer.classList.add('paused');
        
        // Update button state
        this.stopButton.disabled = true;
        this.stopButton.textContent = 'Processing...';
        
        try {
            this.showLoading();
            await this.captureAndUpload();
        } catch (error) {
            console.error('Error capturing image:', error);
            this.showError('Failed to capture image. Please try again.');
            // Reset states on error
            this.isAnimating = true;
            this.gradientContainer.classList.remove('paused');
            this.stopButton.disabled = false;
            this.stopButton.textContent = 'Capture';
            // Restart GIF cycling
            this.startGifCycling();
        }
    }

    // Capture the gradient and upload to server
    async captureAndUpload() {
        try {
            console.log('Starting upload process with pre-captured frame...');
            
            // Use the canvas that was already captured in stopAndCapture()
            // This is the exact frame the user saw when they clicked Capture
            const canvas = this.capturedState.canvas;
            
            if (!canvas) {
                throw new Error('No captured canvas found');
            }
            
            console.log('Using pre-captured canvas for upload');
            
            // Convert to blob
            console.log('Converting to blob...');
            const blob = await new Promise((resolve, reject) => {
                canvas.toBlob((blob) => {
                    if (blob) {
                        resolve(blob);
                    } else {
                        reject(new Error('Failed to create blob from canvas'));
                    }
                }, 'image/png', 0.9);
            });
            
            console.log('Blob created, size:', blob.size);
            
            // Upload to server
            console.log('Uploading to server...');
            const formData = new FormData();
            formData.append('image', blob, 'gradient-palette.png');
            formData.append('colours', JSON.stringify(this.currentColours));
            
            const response = await fetch('/api/save-palette', {
                method: 'POST',
                body: formData
            });
            
            console.log('Server response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server error response:', errorText);
                throw new Error(`Server error: ${response.status} - ${errorText}`);
            }
            
            const result = await response.json();
            console.log('Success result:', result);
            
            // Now get recommendations
            await this.getRecommendations(result.filename);
            
        } catch (error) {
            console.error('Capture error details:', error);
            this.hideLoading();
            throw error;
        }
    }

    // Get painting recommendations
    async getRecommendations(filename) {
        try {
            console.log('Getting recommendations for:', filename);
            
            // Store the filename for later use
            this.currentFilename = filename;
            
            // Update loading message
            this.updateLoadingMessage('Your palette is being analysed. Please hold on a moment...');
            
            const response = await fetch('/api/get-recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ filename })
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Recommendations error:', errorText);
                throw new Error(`Failed to get recommendations: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Recommendations result:', result);
            
            // Store data for later use
            this.currentRecommendations = result.recommendations;
            this.currentColourData = result.colourData;
            this.currentRawColors = result.rawColors || [];
            this.currentDetailedRecommendations = result.detailedRecommendations || [];
            
            this.hideLoading();
            
            // Show dedicated color palette page instead of floating modal
            this.showColorPalettePage(result.colourData, result.rawColors, result.emotionPrediction);
            
        } catch (error) {
            console.error('Error getting recommendations:', error);
            this.hideLoading();
            this.showError('Failed to get painting recommendations. Please try again.');
        }
    }

    // Update loading message
    // Update loading message
    updateLoadingMessage(message) {
        const loadingText = document.querySelector('.loading-analysis-text');
        if (loadingText) {
            loadingText.textContent = message;
        }
    }

    // Show dedicated color palette page
    showColorPalettePage(colourData, rawColors = [], emotionPrediction = null) {
        console.log('🎨 Showing color palette page');
        
        // Hide gradient container and controls
        document.getElementById('gradient-container').style.display = 'none';
        document.querySelector('.controls').style.display = 'none';
        
        // Create or show color palette page
        let colorPalettePage = document.getElementById('color-palette-page');
        if (!colorPalettePage) {
            colorPalettePage = this.createColorPalettePage();
            document.body.appendChild(colorPalettePage);
        }
        
        colorPalettePage.style.display = 'block';
        
        // Update the captured image display
        const capturedImage = document.getElementById('captured-palette-image');
        if (capturedImage && this.currentFilename) {
            capturedImage.src = `/uploads/${this.currentFilename}`;
            capturedImage.style.display = 'block';
        }
        
        // Ensure event listeners are attached (backup)
        setTimeout(() => {
            const continueBtn = document.getElementById('continue-btn');
            const recaptureBtn = document.getElementById('recapture-btn');
            
            if (continueBtn && recaptureBtn) {
                console.log('✅ Color palette page buttons found, event listeners should already be attached');
            } else {
                console.warn('⚠️ Color palette page buttons not found, may need to re-attach listeners');
                
                if (continueBtn) {
                    continueBtn.addEventListener('click', () => {
                        console.log('🎯 Continue button clicked (backup listener)');
                        this.continueToGalleryFromPalette();
                    });
                }
                
                if (recaptureBtn) {
                    recaptureBtn.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('🎨 Re-capture button clicked (backup listener)');
                        this.recaptureColors();
                    });
                }
            }
        }, 100);
        
        // Scroll to top
        setTimeout(() => {
            window.scrollTo(0, 0);
        }, 100);
        
        // Create the color chart
        this.createColorPaletteChart(colourData, rawColors, emotionPrediction);
    }

    // Create dedicated color palette page
    createColorPalettePage() {
        const colorPalettePage = document.createElement('div');
        colorPalettePage.id = 'color-palette-page';
        colorPalettePage.innerHTML = `
            <div class="gallery-container">
                <h1 class="gallery-title">Colours extracted from your palette</h1>
                <p class="gallery-subtitle">Based on your captured gradient</p>
                
                <!-- Palette Analysis Container - matches Step 2 and Step 3 containers -->
                <div class="palette-analysis-container">
                    <!-- Captured Image Section -->
                    <div class="captured-image-section">
                        <h3 class="captured-image-title">Your captured palette</h3>
                        <img id="captured-palette-image" class="captured-palette-image" 
                             alt="Your captured gradient palette" style="display: none;">
                    </div>
                    
                    <!-- Spacing between captured image and extracted colors -->
                    <div style="height: 40px;"></div>
                    
                    <!-- Raw Colors Section -->
                    <div class="raw-colors-section">
                        <h3 class="raw-colors-title">Colours extracted from your palette</h3>
                        <div class="chart-container">
                            <div id="raw-color-palette-bar" class="color-bar raw-color-bar"></div>
                        </div>
                    </div>
                    
                    <!-- Spacing between original color bars and mapped colors -->
                    <div style="height: 40px;"></div>
                    
                    <!-- Mapped Colors Section -->
                    <div class="mapped-colors-section">
                        <h3 class="mapped-colors-title">Mapped to <span class="basic-colours-hover">basic colours*</span></h3>
                        <div class="chart-container">
                            <div id="color-palette-bar" class="color-bar"></div>
                        </div>
                        <div class="colour-legend" id="color-palette-legend">
                            <!-- Legend items will be populated here -->
                        </div>
                    </div>
                </div>
                
                <div class="color-palette-controls">
                    <button id="recapture-btn" class="btn-primary">Re-capture</button>
                    <button id="continue-btn" class="btn-secondary">Continue</button>
                </div>
            </div>
        `;
        
        // Apply gallery page styles
        colorPalettePage.className = 'color-palette-page';
        colorPalettePage.style.cssText = `
            display: none;
            min-height: 100vh;
            background: 
                radial-gradient(circle at 20% 20%, rgba(30, 30, 30, 0.8) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(15, 15, 25, 0.9) 0%, transparent 50%),
                radial-gradient(circle at 40% 60%, rgba(20, 25, 35, 0.7) 0%, transparent 40%),
                linear-gradient(135deg, #000000 0%, #0a0a0a 50%, #000000 100%);
            padding: 40px 20px;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow-y: auto;
            z-index: 2000;
        `;
        
        // Add event listeners
        const continueBtn = colorPalettePage.querySelector('#continue-btn');
        const recaptureBtn = colorPalettePage.querySelector('#recapture-btn');
        
        // Initialize Continue button state
        continueBtn.disabled = true;
        continueBtn.textContent = 'Choose a feeling';
        continueBtn.style.opacity = '0.6';
        continueBtn.style.cursor = 'not-allowed';
        
        continueBtn.addEventListener('click', () => {
            console.log('🎯 Continue button clicked from color palette page');
            if (this.selectedEmotion) {
                this.proceedWithSelectedEmotion();
            } else {
                console.log('⚠️ No emotion selected, button should be disabled');
            }
        });
        
        recaptureBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('🎨 Re-capture button clicked from color palette page');
            this.recaptureColors();
        });
        
        // Add backup event listener for re-capture button using event delegation
        colorPalettePage.addEventListener('click', (e) => {
            if (e.target.id === 'recapture-btn' || e.target.closest('#recapture-btn')) {
                e.preventDefault();
                e.stopPropagation();
                console.log('🎨 Re-capture button clicked (backup listener)');
                this.recaptureColors();
            }
        });
        
        return colorPalettePage;
    }

    // Create color palette bars for dedicated page
    createColorPaletteChart(colourData, rawColors = [], emotionPrediction = null) {
        console.log('🎨 Creating color palette bars with data:', colourData, 'Raw colors:', rawColors);
        
        if (!colourData || Object.keys(colourData).length === 0) {
            console.log('❌ No colour data available');
            return;
        }

        // Create raw colors bar first
        this.createRawColorBar(rawColors);

        // Define colour mappings for visualization
        const colourMap = {
            'black': '#1a1a1a',
            'blue': '#2196F3',
            'brown': '#8D6E63',
            'green': '#4CAF50',
            'grey': '#9E9E9E',
            'orange': '#FF9800',
            'pink': '#E91E63',
            'purple': '#9C27B0',
            'red': '#F44336',
            'turquoise': '#00BCD4',
            'white': '#FAFAFA',
            'yellow': '#FFEB3B'
        };

        // Create color bar in color palette page
        const colorBarContainer = document.getElementById('color-palette-bar');
        
        if (!colorBarContainer) {
            console.log('❌ Color bar container not found');
            return;
        }

        // Clear existing content
        colorBarContainer.innerHTML = '';

        // Sort colors by percentage (descending) for better visual flow
        const sortedColors = Object.entries(colourData)
            .filter(([colorName, percentage]) => percentage > 0)
            .sort((a, b) => b[1] - a[1]);

        // Create color segments
        sortedColors.forEach(([colorName, percentage]) => {
            const segment = document.createElement('div');
            segment.className = 'color-segment';
            segment.style.cssText = `
                background-color: ${colourMap[colorName] || '#666666'};
                width: ${(percentage * 100).toFixed(1)}%;
                height: 100%;
                display: inline-block;
                transition: all 0.3s ease;
                position: relative;
                border-right: 1px solid rgba(255, 255, 255, 0.1);
            `;
            
            // Add tooltip only (no hover interactions)
            segment.title = `${colorName.charAt(0).toUpperCase() + colorName.slice(1)}`;

            colorBarContainer.appendChild(segment);
        });

        // Create custom legend for color palette page
        const legendContainer = this.createColorPaletteLegend(colourData, colourMap, emotionPrediction);
        
        // Append the legend to the page
        const legendTargetContainer = document.getElementById('color-palette-legend');
        if (legendTargetContainer) {
            legendTargetContainer.innerHTML = '';
            legendTargetContainer.appendChild(legendContainer);
        }
    }

    // Create raw color bar showing original extracted colors
    createRawColorBar(rawColors) {
        console.log('🎨 Creating raw color bar with colors:', rawColors);
        
        const rawColorBarContainer = document.getElementById('raw-color-palette-bar');
        
        if (!rawColorBarContainer) {
            console.log('❌ Raw color bar container not found');
            return;
        }

        // Clear existing content
        rawColorBarContainer.innerHTML = '';

        if (!rawColors || rawColors.length === 0) {
            console.log('❌ No raw colors available');
            rawColorBarContainer.innerHTML = '<div style="color: rgba(255,255,255,0.5); text-align: center; padding: 20px; background: rgba(255, 255, 255, 0.05); border: 1px dashed rgba(255, 255, 255, 0.2); border-radius: 30px; display: flex; align-items: center; justify-content: center; min-height: 60px;">No raw color data available</div>';
            return;
        }

        // Sort colors by percentage (descending) for better visual flow
        const sortedRawColors = [...rawColors].sort((a, b) => b.percentage - a.percentage);

        // Create color segments for raw colors using RGB values
        sortedRawColors.forEach((colorData, index) => {
            const segment = document.createElement('div');
            segment.className = 'color-segment raw-color-segment';
            
            // Handle both hex format (from JSON) and RGB format (from Python output)
            let colorValue, tooltipText;
            if (colorData.hex) {
                // Hex color from JSON file
                colorValue = colorData.hex;
                tooltipText = colorValue.toUpperCase();
            } else if (colorData.r !== undefined && colorData.g !== undefined && colorData.b !== undefined) {
                // RGB color from Python output
                colorValue = `rgb(${colorData.r}, ${colorData.g}, ${colorData.b})`;
                tooltipText = `RGB(${colorData.r}, ${colorData.g}, ${colorData.b})`;
            } else {
                // Fallback
                colorValue = colorData;
                tooltipText = colorValue;
            }
            
            segment.style.cssText = `
                background-color: ${colorValue};
                width: ${(colorData.percentage * 100).toFixed(1)}%;
                height: 100%;
                display: inline-block;
                transition: all 0.3s ease;
                position: relative;
                border-right: 1px solid rgba(255, 255, 255, 0.1);
            `;
            
            // Add tooltip only (no hover interactions)
            segment.title = tooltipText;

            rawColorBarContainer.appendChild(segment);
        });
    }

    // Create custom color palette legend
    createColorPaletteLegend(colourData, colourMap, emotionPrediction = null) {
        const legendContainer = document.createElement('div');
        legendContainer.className = 'colour-legend';
        
        // Create legend items - only show colors that have a percentage > 0
        Object.entries(colourData)
            .filter(([colorName, percentage]) => percentage > 0)
            .forEach(([colorName, percentage]) => {
                const legendItem = document.createElement('div');
                legendItem.className = 'legend-item';
                
                const colourBox = document.createElement('div');
                colourBox.className = 'legend-colour';
                colourBox.style.backgroundColor = colourMap[colorName] || '#666666';
                
                const colourText = document.createElement('div');
                colourText.className = 'legend-text';
                colourText.textContent = `${colorName.charAt(0).toUpperCase() + colorName.slice(1)} (${(percentage * 100).toFixed(1)}%)`;
                
                legendItem.appendChild(colourBox);
                legendItem.appendChild(colourText);
                legendContainer.appendChild(legendItem);
            });

        // Add explanatory section
        const explanatorySection = document.createElement('div');
        explanatorySection.className = 'mapping-explanation-section';
        
        // Question text
        const questionText = document.createElement('div');
        questionText.className = 'mapping-question-text';
        questionText.textContent = 'Why and how to map to basic colours?';
        
        // Answer text
        const answerText = document.createElement('div');
        answerText.className = 'mapping-answer-text';
        answerText.textContent = 'Your extracted colours are automatically mapped into 12 basic colour categories using CIEDE2000, a mathematical formula that measures how similar colours appear to the human eye. This mapping helps our system find paintings with matching colour themes from the art database more accurately.';
        
        explanatorySection.appendChild(questionText);
        explanatorySection.appendChild(answerText);
        legendContainer.appendChild(explanatorySection);

        // Add emotion prediction section if available
        if (emotionPrediction && emotionPrediction.all_probabilities) {
            // Add spacing before emotion section
            const emotionSpacingDiv = document.createElement('div');
            emotionSpacingDiv.style.height = '40px';
            legendContainer.appendChild(emotionSpacingDiv);
            
            // Create emotion prediction section
            this.createEmotionPredictionSection(emotionPrediction, legendContainer);
        }

        return legendContainer;
    }

    // Create emotion prediction section (separate from color analysis)
    createEmotionPredictionSection(emotionPrediction, container) {
        // Create emotion prediction container with same style as palette analysis
        const emotionContainer = document.createElement('div');
        emotionContainer.className = 'emotion-prediction-container';
        
        // Emotion categories
        const emotionCategories = {
            positive: ['gratitude', 'happiness', 'love', 'optimism', 'trust'],
            negative: ['anger', 'arrogance', 'disagreeableness', 'disgust', 'fear', 'pessimism', 'sadness'],
            neutral: ['anticipation', 'humility', 'surprise']
        };

        // Initialize reset count and selected emotion
        if (!this.emotionResetCount) {
            this.emotionResetCount = 0;
        }
        this.selectedEmotion = null;

        // Create main title section
        const titleSection = document.createElement('div');
        titleSection.className = 'emotion-selection-title-section';
        
        const stepTitle = document.createElement('div');
        stepTitle.className = 'emotion-step-title';
        stepTitle.textContent = 'Step 2:';
        
        const mainTitle = document.createElement('div');
        mainTitle.className = 'emotion-main-title';
        mainTitle.textContent = 'Which feeling best describes your palette? Choose one to set your story\'s vibe...';
        
        titleSection.appendChild(stepTitle);
        titleSection.appendChild(mainTitle);
        emotionContainer.appendChild(titleSection);

        // Create emotion cards container
        const cardsContainer = document.createElement('div');
        cardsContainer.className = 'emotion-cards-container';
        cardsContainer.id = 'emotion-cards-container';

        // Select random emotions from each category
        const selectedEmotions = this.selectRandomEmotionsFromCategories(emotionCategories, emotionPrediction.all_probabilities);

        // Create emotion cards
        const emotionOrder = ['negative', 'neutral', 'positive'];
        emotionOrder.forEach(categoryKey => {
            const emotion = selectedEmotions[categoryKey];
            if (emotion) {
                const emotionCard = this.createEmotionCard(emotion, emotionPrediction.all_probabilities);
                cardsContainer.appendChild(emotionCard);
            }
        });

        emotionContainer.appendChild(cardsContainer);

        // Create More feelings button
        const moreFeelingsButton = document.createElement('button');
        moreFeelingsButton.className = 'more-feelings-btn';
        moreFeelingsButton.textContent = 'More feelings';
        moreFeelingsButton.disabled = this.emotionResetCount >= 3;
        if (this.emotionResetCount >= 3) {
            moreFeelingsButton.classList.add('disabled');
        }
        
        moreFeelingsButton.addEventListener('click', () => {
            if (this.emotionResetCount < 3) {
                this.emotionResetCount++;
                this.resetEmotionCards(emotionCategories, emotionPrediction.all_probabilities);
                
                if (this.emotionResetCount >= 3) {
                    moreFeelingsButton.disabled = true;
                    moreFeelingsButton.classList.add('disabled');
                }
            }
        });

        emotionContainer.appendChild(moreFeelingsButton);
        
        // Add emotion container to the main container
        container.appendChild(emotionContainer);
    }

    // Select random emotions from each category
    selectRandomEmotionsFromCategories(categories, allProbabilities) {
        const selected = {};
        
        Object.keys(categories).forEach(categoryKey => {
            const categoryEmotions = categories[categoryKey];
            const availableEmotions = categoryEmotions.filter(emotion => 
                allProbabilities.hasOwnProperty(emotion)
            );
            
            if (availableEmotions.length > 0) {
                const randomIndex = Math.floor(Math.random() * availableEmotions.length);
                selected[categoryKey] = availableEmotions[randomIndex];
            }
        });
        
        return selected;
    }

    // Create individual emotion card with new structure
    createEmotionCard(emotion, allProbabilities) {
        const card = document.createElement('div');
        card.className = 'emotion-card';
        card.dataset.emotion = emotion;

        // Emotion name (at the top)
        const emotionName = document.createElement('div');
        emotionName.className = 'emotion-card-name';
        emotionName.textContent = emotion.charAt(0).toUpperCase() + emotion.slice(1);
        card.appendChild(emotionName);

        // Emotion image container
        const imageContainer = document.createElement('div');
        imageContainer.className = 'emotion-card-image-container';
        
        const image = document.createElement('img');
        image.className = 'emotion-card-image';
        image.src = `15 emotion illustrations/${emotion}.jpg`;
        image.alt = emotion;
        image.onerror = () => {
            // Fallback if image doesn't exist
            image.style.display = 'none';
            imageContainer.innerHTML = `<div class="emotion-card-placeholder">${emotion}</div>`;
        };
        
        imageContainer.appendChild(image);
        card.appendChild(imageContainer);

        // Probability percentage
        const probability = (allProbabilities[emotion] * 100).toFixed(1);
        const probabilityDiv = document.createElement('div');
        probabilityDiv.className = 'emotion-card-probability';
        probabilityDiv.textContent = `${probability}%`;
        card.appendChild(probabilityDiv);

        // Description
        const description = document.createElement('div');
        description.className = 'emotion-card-description';
        description.textContent = 'people have this feeling';
        card.appendChild(description);

        // Click handler for selection
        card.addEventListener('click', () => {
            this.handleEmotionCardSelection(emotion, probability, card);
        });

        return card;
    }

    // Handle emotion card selection
    handleEmotionCardSelection(emotion, probability, card) {
        // Deselect all other emotion cards
        const allCards = document.querySelectorAll('.emotion-card');
        allCards.forEach(c => {
            c.classList.remove('emotion-card-selected');
        });

        // Select the clicked emotion card
        card.classList.add('emotion-card-selected');

        // Store the selected emotion
        this.selectedEmotion = {
            emotion: emotion,
            probability: probability
        };

        // Update the main Continue button at the bottom of the page
        this.updateMainContinueButton();

        console.log(`User selected emotion: ${emotion} (${probability}%)`);
    }

    // Update the main Continue button based on emotion selection
    updateMainContinueButton() {
        const continueBtn = document.getElementById('continue-btn');
        if (continueBtn) {
            if (this.selectedEmotion) {
                // Enable the button
                continueBtn.disabled = false;
                continueBtn.textContent = 'Continue';
                continueBtn.style.opacity = '1';
                continueBtn.style.cursor = 'pointer';
            } else {
                // Disable the button
                continueBtn.disabled = true;
                continueBtn.textContent = 'Choose a feeling';
                continueBtn.style.opacity = '0.6';
                continueBtn.style.cursor = 'not-allowed';
            }
        }
    }

    // Reset emotion cards with new random selections
    resetEmotionCards(categories, allProbabilities) {
        const cardsContainer = document.getElementById('emotion-cards-container');
        if (!cardsContainer) return;

        // Clear existing cards
        cardsContainer.innerHTML = '';

        // Reset selected emotion
        this.selectedEmotion = null;

        // Update main Continue button
        this.updateMainContinueButton();

        // Select new random emotions
        const selectedEmotions = this.selectRandomEmotionsFromCategories(categories, allProbabilities);

        // Create new emotion cards
        const emotionOrder = ['negative', 'neutral', 'positive'];
        emotionOrder.forEach(categoryKey => {
            const emotion = selectedEmotions[categoryKey];
            if (emotion) {
                const emotionCard = this.createEmotionCard(emotion, allProbabilities);
                cardsContainer.appendChild(emotionCard);
            }
        });
    }

    // Legacy function - kept for compatibility but redirects to new structure
    createEmotionPredictionBanners(emotionPrediction, container) {
        // This function is now replaced by createEmotionPredictionSection
        // Keeping for backward compatibility
        this.createEmotionPredictionSection(emotionPrediction, container);
    }

    // Legacy function - kept for compatibility but redirects to new structure
    createEmotionContainer(emotion, allProbabilities) {
        // This function is now replaced by createEmotionCard
        // Keeping for backward compatibility
        return this.createEmotionCard(emotion, allProbabilities);
    }

    // Legacy function - kept for compatibility but redirects to new structure
    handleEmotionSelection(emotion, probability, container) {
        // This function is now replaced by handleEmotionCardSelection
        // Keeping for backward compatibility
        this.handleEmotionCardSelection(emotion, probability, container);
    }

    // Legacy function - kept for compatibility but redirects to new structure
    resetEmotionBanners(categories, allProbabilities) {
        // This function is now replaced by resetEmotionCards
        // Keeping for backward compatibility
        this.resetEmotionCards(categories, allProbabilities);
    }

    // Deselect emotion
    deselectEmotion() {
        const allCards = document.querySelectorAll('.emotion-card');
        allCards.forEach(card => {
            card.classList.remove('emotion-card-selected');
        });

        // Clear selected emotion
        this.selectedEmotion = null;

        // Update main Continue button
        this.updateMainContinueButton();
    }

    // Proceed with selected emotion
    proceedWithSelectedEmotion() {
        if (this.selectedEmotion) {
            console.log(`Proceeding with emotion: ${this.selectedEmotion.emotion} (${this.selectedEmotion.probability}%)`);
            
            // Send emotion selection to server
            this.sendEmotionToServer(this.selectedEmotion.emotion, this.selectedEmotion.probability);
            
            // Continue to gallery as before
            this.continueToGalleryFromPalette();
        }
    }

    // Send emotion selection to server
    async sendEmotionToServer(emotion, probability) {
        try {
            console.log('📤 Sending emotion selection to server:', { emotion, probability });
            
            const response = await fetch('/api/save-emotion', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    emotion: emotion,
                    probability: probability,
                    filename: this.currentFilename,
                    sessionId: this.generateSessionId()
                })
            });
            
            if (!response.ok) {
                console.error('Failed to save emotion selection:', response.status);
                return;
            }
            
            const result = await response.json();
            console.log('✅ Emotion selection saved successfully:', result);
            
        } catch (error) {
            console.error('❌ Error sending emotion selection to server:', error);
            // Don't block the user flow if server request fails
        }
    }

    // Generate or get session ID
    generateSessionId() {
        if (!this.sessionId) {
            this.sessionId = crypto.randomUUID ? crypto.randomUUID() : 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        }
        return this.sessionId;
    }

    // Continue to gallery from color palette page
    continueToGalleryFromPalette() {
        console.log('🎯 Continuing to gallery from palette page');
        
        // Show keyboard loading animation instead of changing button text
        this.showKeyboardLoading();
        
        // Hide color palette page and show gallery after 3 seconds
        setTimeout(() => {
            this.hideKeyboardLoading();
            
            const colorPalettePage = document.getElementById('color-palette-page');
            if (colorPalettePage) {
                colorPalettePage.style.display = 'none';
            }
            
            // Get recommendations and show gallery
            if (this.lastCapturedFilename) {
                this.getRecommendations(this.lastCapturedFilename)
                    .then(recommendations => {
                        this.currentRecommendations = recommendations;
                        this.showGalleryWithoutColorDashboard(recommendations);
                    })
                    .catch(error => {
                        console.error('Error getting recommendations:', error);
                        this.showError('Failed to get painting recommendations. Please try again.');
                    });
            } else {
                // Fallback to existing recommendations if available
                this.showGalleryWithoutColorDashboard(this.currentRecommendations);
            }
        }, 5000); // 5 second processing time
    }

    // Re-capture palette - redirect to gradient page
    recaptureColors() {
        try {
            console.log('🎨 Re-capturing colors');
            console.log('Recapture colors function called successfully!');
            
            // Hide story interface
            const storyInterface = document.getElementById('story-interface');
            if (storyInterface) {
                storyInterface.remove();
                console.log('✅ Story interface removed');
            }
            
            // Hide gallery page
            const galleryPage = document.getElementById('gallery-page');
            if (galleryPage) {
                galleryPage.style.display = 'none';
                console.log('✅ Gallery page hidden');
            }
            
            // Hide color palette page if it exists
            const colorPalettePage = document.getElementById('color-palette-page');
            if (colorPalettePage) {
                colorPalettePage.style.display = 'none';
                console.log('✅ Color palette page hidden');
            }
            
            // Hide homepage if visible
            const homepage = document.getElementById('homepage');
            if (homepage) {
                homepage.style.display = 'none';
            }
            
            // Show and ensure gradient container is visible
            const gradientContainer = document.getElementById('gradient-container');
            if (gradientContainer) {
                gradientContainer.style.display = 'block';
                gradientContainer.style.visibility = 'visible';
                gradientContainer.style.opacity = '1';
                console.log('✅ Gradient container shown');
            }
            
            // Reset all state
            this.selectedPaintings = [];
            this.selectedCharacter = null;
            this.selectedNarrativeStyle = null;
            this.userName = '';
            this.step2Complete = false;
            this.step3Complete = false;
            this.currentDetailedRecommendations = [];
            this.currentColourData = null;
            this.currentStory = null;
            this.isAnimating = true;
            this.isCaptured = false;
            
            // Clear any existing intervals
            if (this.colourChangeInterval) {
                clearInterval(this.colourChangeInterval);
                this.colourChangeInterval = null;
            }
            
            // Stop any existing prompt animation
            this.stopCapturePromptAnimation();
            
            // Reset capture button and make it visible IMMEDIATELY
            const stopButton = document.getElementById('stop-btn');
            if (stopButton) {
                stopButton.textContent = 'Capture';
                stopButton.disabled = false;
                // Use more specific styling to override CSS rules
                stopButton.style.setProperty('opacity', '1', 'important');
                stopButton.style.setProperty('visibility', 'visible', 'important');
                stopButton.style.setProperty('display', 'block', 'important');
                stopButton.style.transition = 'opacity 0.3s ease-in-out, visibility 0.3s ease-in-out';
                // Add a flag to indicate this is a re-capture scenario
                stopButton.dataset.recapture = 'true';
                console.log('✅ Capture button reset and made visible immediately');
            }
            
            // Show capture prompt immediately
            const capturePrompt = document.getElementById('capture-prompt');
            if (capturePrompt) {
                capturePrompt.classList.remove('hidden');
                capturePrompt.style.display = 'block';
                console.log('✅ Capture prompt shown immediately');
            }
            
            // Ensure body allows scrolling again
            document.body.classList.remove('no-scroll');
            
            // Reset gradient container styles and restart random GIF cycling
            if (gradientContainer) {
                gradientContainer.style.animation = '';
                gradientContainer.style.animationPlayState = '';
                gradientContainer.classList.remove('paused');
                
                // Clear any captured background image and restore animated GIF element
                gradientContainer.style.backgroundImage = 'none';
                if (this.animatedGifElement) {
                    this.animatedGifElement.style.display = 'block';
                    this.animatedGifElement.classList.add('visible');
                    this.animatedGifElement.classList.remove('hidden');
                }
                
                // Restart random GIF cycling with new random order
                this.startGifCycling();
                
                console.log('🎬 Restarted random GIF cycling for recapture');
            }
            
            // Generate fresh colors and apply them (disabled for GIF background)
            this.generateRandomColours();
            this.applyColoursToCSS();
            
            // Restart gradient animation (disabled for GIF background)
            this.addPeriodicColourChange();
            
            // Start capture prompt animation with immediate button visibility for re-capture
            setTimeout(() => {
                this.startCapturePromptAnimation();
            }, 100);
            
            // Scroll to gradient container and ensure it's fully visible
            setTimeout(() => {
                if (gradientContainer) {
                    // Scroll to top of page first
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                    // Then scroll to gradient container
                    setTimeout(() => {
                        gradientContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 200);
                }
            }, 200);
            
            console.log('🔄 Ready to capture new palette - all systems reset');
        } catch (error) {
            console.error('❌ Error re-capturing colors:', error);
            alert('Unable to re-capture palette. Please refresh the page.');
        }
    }

    // Hide floating color palette
    hideFloatingColorPalette() {
        console.log('Hiding floating color palette...');
        const floatingModal = document.querySelector('.floating-color-palette');
        if (floatingModal) {
            floatingModal.style.display = 'none';
            floatingModal.classList.remove('visible');
            setTimeout(() => {
                floatingModal.classList.add('hidden');
            }, 300);
        }
    }

    // Show loading state
    showLoading() {
        this.loading.classList.remove('hidden');
        this.loading.classList.add('visible');
    }

    // Hide loading state
    hideLoading() {
        console.log('Hiding loading...');
        this.loading.classList.add('hidden');
        this.loading.classList.remove('visible');
        this.loading.style.display = 'none'; // Force hide
    }

    // Show keyboard loading state for Continue button
    showKeyboardLoading() {
        console.log('🎹 Showing keyboard loading...');
        
        // Hide the palette page buttons during loading
        const recaptureBtn = document.getElementById('recapture-btn');
        const continueBtn = document.getElementById('continue-btn');
        if (recaptureBtn) {
            recaptureBtn.style.display = 'none';
        }
        if (continueBtn) {
            continueBtn.style.display = 'none';
        }
        
        // Create keyboard loading overlay if it doesn't exist
        let keyboardLoading = document.getElementById('keyboard-loading');
        if (!keyboardLoading) {
            keyboardLoading = document.createElement('div');
            keyboardLoading.id = 'keyboard-loading';
            keyboardLoading.className = 'keyboard-loading';
            keyboardLoading.innerHTML = `
                <div class="keyboard-animation">
                    <img src="image/keyboard.gif" alt="Loading..." class="keyboard-gif">
                </div>
                <p class="keyboard-loading-text">Your recommended artworks are being prepared. Please hold on a moment...</p>
            `;
            document.body.appendChild(keyboardLoading);
        }
        
        keyboardLoading.classList.remove('hidden');
        keyboardLoading.classList.add('visible');
    }

    // Hide keyboard loading state
    hideKeyboardLoading() {
        console.log('🎹 Hiding keyboard loading...');
        
        // Restore the palette page buttons visibility
        const recaptureBtn = document.getElementById('recapture-btn');
        const continueBtn = document.getElementById('continue-btn');
        if (recaptureBtn) {
            recaptureBtn.style.display = 'inline-block';
        }
        if (continueBtn) {
            continueBtn.style.display = 'inline-block';
        }
        
        const keyboardLoading = document.getElementById('keyboard-loading');
        if (keyboardLoading) {
            keyboardLoading.classList.remove('visible');
            keyboardLoading.classList.add('hidden');
            setTimeout(() => {
                keyboardLoading.style.display = 'none';
            }, 300);
        }
    }

    // Show processing screen for AI recommendation calculation
    showProcessingScreen() {
        console.log('🤖 Showing AI processing screen...');
        
        // Create processing screen if it doesn't exist
        let processingScreen = document.getElementById('processing-screen');
        if (!processingScreen) {
            processingScreen = document.createElement('div');
            processingScreen.id = 'processing-screen';
            processingScreen.className = 'processing-screen';
            processingScreen.innerHTML = `
                <div class="processing-content">
                    <div class="processing-animation">
                        <div class="neural-network">
                            <div class="node node-1"></div>
                            <div class="node node-2"></div>
                            <div class="node node-3"></div>
                            <div class="node node-4"></div>
                            <div class="node node-5"></div>
                            <div class="connection conn-1"></div>
                            <div class="connection conn-2"></div>
                            <div class="connection conn-3"></div>
                            <div class="connection conn-4"></div>
                        </div>
                    </div>
                    <h2 class="processing-title">AI Analysis in Progress</h2>
                    <div class="processing-steps">
                        <div class="processing-step active" data-step="1">
                            <span class="step-icon">🎨</span>
                            <span class="step-text">Analyzing colour palette</span>
                        </div>
                        <div class="processing-step" data-step="2">
                            <span class="step-icon">🧠</span>
                            <span class="step-text">Processing neural networks</span>
                        </div>
                        <div class="processing-step" data-step="3">
                            <span class="step-icon">🖼️</span>
                            <span class="step-text">Matching art database</span>
                        </div>
                        <div class="processing-step" data-step="4">
                            <span class="step-icon">✨</span>
                            <span class="step-text">Generating recommendations</span>
                        </div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                </div>
            `;
            document.body.appendChild(processingScreen);
        }
        
        // Show the processing screen
        processingScreen.style.display = 'flex';
        setTimeout(() => {
            processingScreen.classList.add('visible');
        }, 100);
        
        // Animate through the processing steps
        this.animateProcessingSteps();
    }

    // Hide processing screen
    hideProcessingScreen() {
        console.log('🤖 Hiding AI processing screen...');
        const processingScreen = document.getElementById('processing-screen');
        if (processingScreen) {
            processingScreen.classList.remove('visible');
            setTimeout(() => {
                processingScreen.style.display = 'none';
            }, 300);
        }
    }

    // Animate processing steps for credibility
    animateProcessingSteps() {
        const steps = document.querySelectorAll('.processing-step');
        const progressFill = document.querySelector('.progress-fill');
        let currentStep = 0;
        
        const stepInterval = setInterval(() => {
            // Remove active class from previous step
            if (currentStep > 0) {
                steps[currentStep - 1].classList.remove('active');
                steps[currentStep - 1].classList.add('completed');
            }
            
            // Add active class to current step
            if (currentStep < steps.length) {
                steps[currentStep].classList.add('active');
                
                // Update progress bar
                const progress = ((currentStep + 1) / steps.length) * 100;
                if (progressFill) {
                    progressFill.style.width = `${progress}%`;
                }
                
                currentStep++;
            } else {
                clearInterval(stepInterval);
            }
        }, 600); // Each step takes 0.6 seconds
    }

    // Show result modal
    showResult(url) {
        this.resultUrl.textContent = url;
        this.modal.style.display = 'flex';
        this.modal.classList.remove('hidden');
        this.modal.classList.add('visible');
    }

    // Show error message
    showError(message) {
        this.hideLoading();
        this.resetButtonState();
        alert(message); // In a real app, you'd use a nicer error modal
    }

    // Hide modal
    hideModal() {
        console.log('Hiding modal...');
        this.modal.classList.remove('visible');
        this.modal.style.display = 'none'; // Force hide immediately
        setTimeout(() => {
            this.modal.classList.add('hidden');
        }, 300);
    }

    // Copy URL to clipboard
    async copyUrlToClipboard() {
        try {
            await navigator.clipboard.writeText(this.resultUrl.textContent);
            const copyBtn = document.getElementById('copy-btn');
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copied!';
            copyBtn.style.background = '#28a745';
            
            setTimeout(() => {
                copyBtn.textContent = originalText;
                copyBtn.style.background = '#007bff';
            }, 2000);
        } catch (error) {
            console.error('Failed to copy URL:', error);
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = this.resultUrl.textContent;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
        }
    }

    // Restart the animation
    restart() {
        this.isAnimating = true;
        this.gradientContainer.classList.remove('paused');
        this.stopButton.disabled = false;
        this.stopButton.textContent = 'Capture';
        this.generateRandomColours();
        this.applyColoursToCSS();
        
        // Clear any captured background image and restore animated GIF element
        this.gradientContainer.style.backgroundImage = 'none';
        if (this.animatedGifElement) {
            this.animatedGifElement.style.display = 'block';
            this.animatedGifElement.classList.add('visible');
            this.animatedGifElement.classList.remove('hidden');
        }
        
        // Restart GIF cycling instead of color changes
        this.startGifCycling();
        
        console.log('🔄 Animation restarted with random GIF cycling');
    }

    // Scroll to gradient page
    scrollToGradientPage() {
        // Enable scrolling when START button is clicked
        document.body.classList.remove('no-scroll');
        document.body.classList.add('allow-scroll');
        
        // Always ensure animation and color changes are running when going to gradient page
        this.isAnimating = true;
        this.generateRandomColours();
        this.applyColoursToCSS();
        
        // Start the color change interval (this will clear any existing interval first)
        this.addPeriodicColourChange();
        
        console.log('🎨 Gradient page loaded with color animation active');
        
        // Show gradient container and controls
        document.getElementById('gradient-container').style.display = 'flex';
        document.querySelector('.controls').style.display = 'flex';
        
        // Start random GIF cycling animation
        const gradientContainer = document.getElementById('gradient-container');
        if (gradientContainer) {
            gradientContainer.classList.remove('paused');
            this.startGifCycling(); // Start random cycling through all 30 GIFs
            console.log('🎬 Random GIF cycling started on gradient page');
        }
        
        // Initially hide the capture button - it will appear with the prompt
        const captureButton = document.getElementById('stop-btn');
        if (captureButton) {
            captureButton.style.opacity = '0';
            captureButton.style.visibility = 'hidden';
            captureButton.style.transition = ''; // Clear any existing transitions
        }
        
        // Hide any other pages
        const galleryPage = document.getElementById('gallery-page');
        if (galleryPage) {
            galleryPage.style.display = 'none';
        }
        const colorPalettePage = document.getElementById('color-palette-page');
        if (colorPalettePage) {
            colorPalettePage.style.display = 'none';
        }
        
        // Scroll to gradient page
        this.gradientContainer.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
        
        // Start the capture prompt animation after scrolling and a 1-second delay
        setTimeout(() => {
            this.startCapturePromptAnimation();
        }, 1000);
    }

    // Scroll to homepage
    scrollToHomepage() {
        this.homepage.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }

    // Prevent scrolling on homepage until START is clicked
    preventScrollOnHomepage() {
        const preventScroll = (e) => {
            // Only prevent scroll if we're on the homepage (no-scroll class is active)
            if (document.body.classList.contains('no-scroll')) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        };

        // Prevent wheel events (mouse wheel, trackpad)
        document.addEventListener('wheel', preventScroll, { passive: false });
        
        // Prevent touch scroll on mobile
        document.addEventListener('touchmove', preventScroll, { passive: false });
        
        // Prevent keyboard scroll
        document.addEventListener('keydown', (e) => {
            if (document.body.classList.contains('no-scroll')) {
                // Prevent arrow keys, page up/down, space, home, end
                if ([32, 33, 34, 35, 36, 37, 38, 39, 40].includes(e.keyCode)) {
                    e.preventDefault();
                    return false;
                }
            }
        });
    }

    // Get current colour palette (useful for debugging)
    getCurrentColours() {
        return this.currentColours;
    }

    // Start the capture prompt animation
    startCapturePromptAnimation() {
        const promptElement = document.getElementById('capture-prompt');
        const captureButton = document.getElementById('stop-btn');
        if (!promptElement || !captureButton) return;
        
        // Clear any existing animation interval
        if (this.promptAnimationInterval) {
            clearInterval(this.promptAnimationInterval);
            this.promptAnimationInterval = null;
        }
        
        // Ensure capture prompt font styling is applied
        this.updateCapturePromptStyling();
        
        // Check if this is a re-capture scenario (button already visible or has re-capture flag)
        const isRecapture = captureButton.dataset.recapture === 'true' || 
                           captureButton.style.visibility === 'visible' ||
                           captureButton.style.opacity === '1';
        
        // For re-capture scenarios, show button immediately with no delay
        if (isRecapture) {
            console.log('🔄 Re-capture detected - showing button immediately');
            captureButton.style.transition = 'opacity 0.3s ease-in-out, visibility 0.3s ease-in-out';
            captureButton.style.setProperty('opacity', '1', 'important');
            captureButton.style.setProperty('visibility', 'visible', 'important');
            captureButton.style.setProperty('display', 'block', 'important');
            
            // Start the continuous CSS animation cycle immediately
            promptElement.classList.remove('hidden', 'visible');
            promptElement.classList.add('animating');
            
            // Clear the re-capture flag
            delete captureButton.dataset.recapture;
        } else {
            // For initial capture, hide button initially and show after delay
            console.log('🎨 Initial capture - using delay for button visibility');
            captureButton.style.opacity = '0';
            captureButton.style.visibility = 'hidden';
            
            // Start the continuous CSS animation cycle with delay for initial capture
            setTimeout(() => {
                promptElement.classList.remove('hidden', 'visible');
                promptElement.classList.add('animating');
                
                // Show the capture button at the same time with a smooth fade-in
                captureButton.style.transition = 'opacity 0.5s ease-in-out, visibility 0.5s ease-in-out';
                captureButton.style.setProperty('opacity', '1', 'important');
                captureButton.style.setProperty('visibility', 'visible', 'important');
            }, 1000);
        }
    }

    // Animate the capture prompt (single cycle) - legacy method, keeping for compatibility
    animateCapturePrompt(promptElement) {
        // This method is now handled by CSS animation
        // Keeping for any legacy calls
    }

    // Stop the capture prompt animation
    stopCapturePromptAnimation() {
        if (this.promptAnimationInterval) {
            clearInterval(this.promptAnimationInterval);
            this.promptAnimationInterval = null;
        }
        
        const promptElement = document.getElementById('capture-prompt');
        const captureButton = document.getElementById('stop-btn');
        if (promptElement) {
            promptElement.classList.remove('visible', 'animating');
            promptElement.classList.add('hidden');
        }
        
        // Only hide the capture button if it's not currently processing
        if (captureButton && !captureButton.disabled) {
            captureButton.style.opacity = '0';
            captureButton.style.visibility = 'hidden';
        }
    }

    // Initialize drag and drop functionality
    setupDropZones(galleryPage) {
        // Clear any existing global listeners first
        this.removeGlobalDragListeners();
        
        const dropZones = galleryPage.querySelectorAll('.drop-zone');
        console.log('🎯 Setting up', dropZones.length, 'drop zones');
        
        dropZones.forEach((dropZone, index) => {
            console.log(`Setting up drop zone ${index + 1}`);
            
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('drag-over');
                console.log('🎯 Drag over drop zone', index + 1);
            });
            
            dropZone.addEventListener('dragleave', (e) => {
                if (!dropZone.contains(e.relatedTarget)) {
                    dropZone.classList.remove('drag-over');
                    console.log('🎯 Drag leave drop zone', index + 1);
                }
            });
            
            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('drag-over');
                console.log('🎯 Drop on drop zone', index + 1);
                this.handleDrop(e, dropZone);
            });
        });
        
        // Set up global drag event listeners
        this.setupGlobalDragListeners();
    }
    
    // Handle drop event on drop zones
    handleDrop(e, dropZone) {
        try {
            const data = JSON.parse(e.dataTransfer.getData('text/plain'));
            const slot = parseInt(dropZone.dataset.slot);
            
            console.log('🎯 Handling drop:', { data, slot });
            
            // Check if this image is already selected in any slot
            const alreadySelected = this.selectedPaintings.find(p => p.url === data.url);
            if (alreadySelected) {
                console.log('⚠️ Image already selected in slot', alreadySelected.slot);
                this.showSelectionMessage(`This painting is already selected in box ${alreadySelected.slot + 1}`, 'warning');
                return;
            }
            
            // Check if this slot is already filled
            const existingPainting = this.selectedPaintings.find(p => p.slot === slot);
            if (existingPainting) {
                console.log('🔄 Replacing existing painting in slot', slot);
                // Remove the existing painting
                this.selectedPaintings = this.selectedPaintings.filter(p => p.slot !== slot);
            }
            
            // Add the new painting
            const painting = {
                url: data.url,
                index: data.index,
                slot: slot
            };
            
            this.selectedPaintings.push(painting);
            console.log('✅ Painting added to selection:', painting);
            
            // Update the drop zone UI
            dropZone.innerHTML = `
                <div class="selected-painting">
                    <div class="selected-painting-container">
                        <img src="${data.url}" alt="Selected Painting" class="selected-painting-image">
                        <div class="selected-painting-overlay">
                            <button class="remove-painting-btn" data-slot="${slot}">×</button>
                        </div>
                    </div>
                </div>
            `;
            dropZone.classList.add('filled');
            
            // Add event listener to the remove button
            const removeBtn = dropZone.querySelector('.remove-painting-btn');
            if (removeBtn) {
                removeBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('🗑️ Remove button clicked for slot:', slot);
                    this.removePaintingFromSlot(slot);
                });
            }
            
            // Update button states
            this.updateSelectionButtons();
            
            // Removed success message as requested by user
            
        } catch (error) {
            console.error('❌ Error handling drop:', error);
            this.showSelectionMessage('Error selecting painting. Please try again.', 'warning');
        }
    }
    
    // Remove painting from slot
    removePaintingFromSlot(slot) {
        console.log('🗑️ Removing painting from slot', slot);
        
        // Remove from selected paintings array
        this.selectedPaintings = this.selectedPaintings.filter(p => p.slot !== slot);
        
        // Reset drop zone UI
        const dropZone = document.querySelector(`.drop-zone[data-slot="${slot}"]`);
        if (dropZone) {
            const icons = ['🎨', '🖼️', '🎭'];
            dropZone.innerHTML = `
                <div class="drop-zone-content">
                    <div class="drop-zone-icon">${icons[slot]}</div>
                    <div class="drop-zone-text">Drop painting ${slot + 1} here</div>
                </div>
            `;
            dropZone.classList.remove('filled');
        }
        
        // Update button states
        this.updateSelectionButtons();
        
        // Remove the "painting removed" message - no longer showing it
    }
    
    // Update selection button states and step completion
    updateSelectionButtons() {
        const clearBtn = document.getElementById('clear-selection-btn');
        const confirmBtn = document.getElementById('confirm-selection-btn');
        
        if (clearBtn) {
            clearBtn.disabled = this.selectedPaintings.length === 0;
        }
        
        if (confirmBtn) {
            confirmBtn.disabled = this.selectedPaintings.length !== 3;
        }
        
        // Update step 2 completion status
        const wasStep2Complete = this.step2Complete;
        this.step2Complete = this.selectedPaintings.length === 3;
        
        // If step 2 just got completed, enable character cards
        if (!wasStep2Complete && this.step2Complete) {
            this.enableCharacterCards();
            console.log('✅ Step 2 completed - Character cards enabled');
        } else if (wasStep2Complete && !this.step2Complete) {
            this.disableCharacterCards();
            console.log('⚠️ Step 2 incomplete - Character cards disabled');
        }
        
        // Update name input visibility and story button state
        this.updateNameInputVisibility();
        this.updateStoryButton();
        
        console.log(`🔄 Updated buttons: ${this.selectedPaintings.length}/3 paintings selected, Step 2: ${this.step2Complete ? 'Complete' : 'Incomplete'}`);
    }
    
    // Set up global drag listeners (separate method to avoid duplicates)
    setupGlobalDragListeners() {
        this.globalDragOverHandler = (e) => {
            e.preventDefault();
            this.currentMouseX = e.clientX;
            this.currentMouseY = e.clientY;
            
            // Handle auto-scroll during drag
            this.handleAutoScroll(e.clientY);
        };
        
        this.globalDragHandler = (e) => {
            // Some browsers don't provide mouse coordinates in drag events
            if (e.clientX !== 0 || e.clientY !== 0) {
                this.currentMouseX = e.clientX;
                this.currentMouseY = e.clientY;
                
                // Handle auto-scroll during drag
                this.handleAutoScroll(e.clientY);
            }
        };
        
        // Enhanced mouse tracking for better auto-scroll during drag
        this.globalMouseMoveHandler = (e) => {
            // Track during active drag for better responsiveness
            if (document.querySelector('.gallery-item.dragging')) {
                this.currentMouseX = e.clientX;
                this.currentMouseY = e.clientY;
                
                // Handle auto-scroll during drag with immediate response
                this.handleAutoScroll(e.clientY);
            }
        };
        
        // Additional drag enter/leave handlers for better edge detection
        this.globalDragEnterHandler = (e) => {
            if (document.querySelector('.gallery-item.dragging')) {
                this.currentMouseX = e.clientX;
                this.currentMouseY = e.clientY;
                this.handleAutoScroll(e.clientY);
            }
        };
        
        document.addEventListener('dragover', this.globalDragOverHandler);
        document.addEventListener('drag', this.globalDragHandler);
        document.addEventListener('mousemove', this.globalMouseMoveHandler);
        document.addEventListener('dragenter', this.globalDragEnterHandler);
        
        console.log('✅ Enhanced global drag listeners set up');
    }
    
    // Remove global drag listeners
    removeGlobalDragListeners() {
        if (this.globalDragOverHandler) {
            document.removeEventListener('dragover', this.globalDragOverHandler);
        }
        if (this.globalDragHandler) {
            document.removeEventListener('drag', this.globalDragHandler);
        }
        if (this.globalMouseMoveHandler) {
            document.removeEventListener('mousemove', this.globalMouseMoveHandler);
        }
        if (this.globalDragEnterHandler) {
            document.removeEventListener('dragenter', this.globalDragEnterHandler);
        }
        
        // Stop auto-scroll when drag ends
        this.stopAutoScroll();
        
        console.log('🧹 Enhanced global drag listeners removed');
    }
    
    // Handle auto-scroll during drag operations
    handleAutoScroll(mouseY) {
        const scrollThreshold = 150; // Optimal distance from edge to trigger auto-scroll
        const windowHeight = window.innerHeight;
        const maxScrollSpeed = 45; // Increased maximum scroll speed for faster scrolling
        const minScrollSpeed = 12; // Higher minimum speed for more responsive scrolling
        
        // Calculate distance from edges
        const distanceFromTop = mouseY;
        const distanceFromBottom = windowHeight - mouseY;
        
        // Determine if we should scroll up
        if (distanceFromTop < scrollThreshold) {
            const intensity = Math.max(0, 1 - (distanceFromTop / scrollThreshold));
            // Use quadratic curve for more responsive acceleration
            const smoothIntensity = Math.pow(intensity, 0.5);
            const speed = Math.max(minScrollSpeed, maxScrollSpeed * smoothIntensity);
            this.startAutoScroll('up', speed);
            return;
        }
        
        // Determine if we should scroll down
        if (distanceFromBottom < scrollThreshold) {
            const intensity = Math.max(0, 1 - (distanceFromBottom / scrollThreshold));
            // Use quadratic curve for more responsive acceleration
            const smoothIntensity = Math.pow(intensity, 0.5);
            const speed = Math.max(minScrollSpeed, maxScrollSpeed * smoothIntensity);
            this.startAutoScroll('down', speed);
            return;
        }
        
        // Stop auto-scroll if not near edges
        this.stopAutoScroll();
    }
    
    // Start auto-scroll in specified direction
    startAutoScroll(direction, speed) {
        // Allow speed updates for smoother transitions
        if (this.isAutoScrolling && this.autoScrollDirection === direction) {
            // Update speed if it's significantly different
            if (Math.abs(this.autoScrollSpeed - speed) > 2) {
                this.autoScrollSpeed = speed;
            }
            return;
        }
        
        // Stop any existing auto-scroll
        this.stopAutoScroll();
        
        this.isAutoScrolling = true;
        this.autoScrollDirection = direction;
        this.autoScrollSpeed = speed;
        
        // Add visual indicators
        document.body.classList.add('auto-scrolling');
        document.body.classList.add(`scroll-${direction}`);
        
        console.log(`🔄 Starting auto-scroll ${direction} at speed ${speed}`);
        
        this.autoScrollInterval = setInterval(() => {
            const galleryPage = document.getElementById('gallery-page');
            if (!galleryPage) return;
            
            const scrollAmount = direction === 'up' ? -this.autoScrollSpeed : this.autoScrollSpeed;
            galleryPage.scrollTop += scrollAmount;
            
            // Check if we've reached the limits
            if (direction === 'up' && galleryPage.scrollTop <= 0) {
                this.stopAutoScroll();
            } else if (direction === 'down' && 
                      galleryPage.scrollTop >= galleryPage.scrollHeight - galleryPage.clientHeight) {
                this.stopAutoScroll();
            }
        }, 8); // Increased to ~125fps for ultra-smooth scrolling
    }
    
    // Stop auto-scroll
    stopAutoScroll() {
        if (!this.isAutoScrolling) return;
        
        this.isAutoScrolling = false;
        this.autoScrollDirection = null;
        this.autoScrollSpeed = 0;
        
        // Remove visual indicators
        document.body.classList.remove('auto-scrolling', 'scroll-up', 'scroll-down');
        
        if (this.autoScrollInterval) {
            clearInterval(this.autoScrollInterval);
            this.autoScrollInterval = null;
        }
        
        console.log('⏹️ Auto-scroll stopped');
    }
    
    // Debug helper to test drag functionality
    debugDragSetup() {
        console.log('🔧 DEBUG: Testing drag setup...');
        
        const draggableItems = document.querySelectorAll('.gallery-item.draggable');
        console.log(`Found ${draggableItems.length} draggable items`);
        
        draggableItems.forEach((item, index) => {
            const rect = item.getBoundingClientRect();
            const computedStyle = window.getComputedStyle(item);
            
            console.log(`Item ${index + 1} debug info:`, {
                draggable: item.draggable,
                pointerEvents: computedStyle.pointerEvents,
                userSelect: computedStyle.userSelect,
                cursor: computedStyle.cursor,
                position: `${rect.left}, ${rect.top}`,
                size: `${rect.width}x${rect.height}`,
                visible: rect.width > 0 && rect.height > 0,
                hasEventListeners: item.getAttribute('data-has-listeners') === 'true'
            });
            
            // Mark that we've checked this item
            item.setAttribute('data-has-listeners', 'true');
        });
        
        // Test if we can programmatically trigger a drag event
        if (draggableItems.length > 0) {
            const testItem = draggableItems[0];
            console.log('🧪 Testing programmatic drag event...');
            
            const dragEvent = new DragEvent('dragstart', {
                bubbles: true,
                cancelable: true,
                dataTransfer: new DataTransfer()
            });
            
            const result = testItem.dispatchEvent(dragEvent);
            console.log('Drag event dispatch result:', result);
        }
    }

    // Continue to gallery (legacy function - now redirects to new flow)
    continueToGallery() {
        console.log('🎯 Continuing to gallery (legacy redirect)');
        this.continueToGalleryFromPalette();
    }

    // Show gallery without color dashboard
    showGalleryWithoutColorDashboard(recommendations) {
        console.log('🖼️ Showing gallery without color dashboard');
        
        // Hide main page
        document.getElementById('gradient-container').style.display = 'none';
        document.querySelector('.controls').style.display = 'none';
        
        // Show gallery page
        let galleryPage = document.getElementById('gallery-page');
        if (!galleryPage) {
            console.log('📄 Creating new gallery page without color dashboard');
            galleryPage = this.createGalleryPageWithoutColorDashboard();
            document.body.appendChild(galleryPage);
        } else {
            console.log('📄 Using existing gallery page');
        }
        
        galleryPage.style.display = 'block';
        
        // Scroll to top of the gallery page
        setTimeout(() => {
            galleryPage.scrollTop = 0;
            window.scrollTo(0, 0);
        }, 100);
        
        // Populate gallery
        this.populateGallery(galleryPage, recommendations);
    }

    // Create gallery page without color dashboard
    createGalleryPageWithoutColorDashboard() {
        const galleryPage = document.createElement('div');
        galleryPage.id = 'gallery-page';
        galleryPage.innerHTML = `
                    <div class="gallery-container">
            <h1 class="gallery-title">Paintings for you</h1>
            <p class="gallery-subtitle">See the 10 paintings recommended from your captured colours</p>
                
                <div style="position: relative;">
                    <button class="gallery-nav-buttons gallery-nav-left" id="gallery-nav-left">
                        <img src="image/left.png" alt="Previous" style="width: 40px; height: 40px;">
                    </button>
                    <button class="gallery-nav-buttons gallery-nav-right" id="gallery-nav-right">
                        <img src="image/left copy.png" alt="Next" style="width: 40px; height: 40px;">
                    </button>
                    <div class="gallery-grid" id="gallery-grid">
                        <!-- Thumbnails will be populated here -->
                    </div>
                </div>
                
                <!-- Drag and Drop Selection Area -->
                <div class="selection-area">
                    <h3 class="selection-title"><strong>Step 3:</strong> Which paintings spark your curiosity?<br/>Pick three to craft a unique story...</h3>
                    <br/>
                    <p class="selection-subtitle">Drag and drop paintings into the boxes</p>
                    <div class="drop-zone-container">
                        <div class="drop-zone" data-slot="0">
                            <div class="drop-zone-content">
                                <div class="drop-zone-icon">🎨</div>
                                <div class="drop-zone-text">Drop painting 1 here</div>
                            </div>
                        </div>
                        <div class="drop-zone" data-slot="1">
                            <div class="drop-zone-content">
                                <div class="drop-zone-icon">🖼️</div>
                                <div class="drop-zone-text">Drop painting 2 here</div>
                            </div>
                        </div>
                        <div class="drop-zone" data-slot="2">
                            <div class="drop-zone-content">
                                <div class="drop-zone-icon">🎭</div>
                                <div class="drop-zone-text">Drop painting 3 here</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Step 3 Character Selection Area -->
                <div class="character-area">
                    <h3 class="character-title"><strong>Step 4:</strong> Which character resonates with you?<br/>Dive into their story...</h3>
                    <br/>
                    <p class="character-subtitle">Select the perspective that interests you the most</p>
                    <p class="character-hover-instruction" style="font-family: 'Poppins', sans-serif; font-weight: 200; font-size: 1rem; color: rgba(255, 255, 255, 0.7); text-align: center; margin-bottom: 30px; font-style: normal;">Hover your cursor <img src="image/cursor.png" alt="cursor" class="inline-cursor-icon"> over the cards below to see each story's style</p>
                    <div class="character-grid">
                        <div class="character-card" data-style="1">
                            <img src="image/style1-a.png" alt="Style 1" class="character-image">
                        </div>
                        <div class="character-card" data-style="2">
                            <img src="image/style2-a.png" alt="Style 2" class="character-image">
                        </div>
                        <div class="character-card" data-style="3">
                            <img src="image/style3-a.png" alt="Style 3" class="character-image">
                        </div>
                        <div class="character-card" data-style="4">
                            <img src="image/style4-a.png" alt="Style 4" class="character-image">
                        </div>
                        <div class="character-card" data-style="5">
                            <img src="image/style5-a.png" alt="Style 5" class="character-image">
                        </div>
                    </div>
                </div>
                
                <!-- Name Input Area -->
                <div class="name-input-area" id="name-input-area" style="display: none;">
                    <h3 class="name-input-title">What shall we call you?<br/>Personalise your story...</h3>
                    <br/>
                    <p class="name-input-subtitle">Enter your name to create a unique story</p>
                    <div class="name-input-container">
                        <input type="text" id="user-name-input" class="name-input-field" placeholder="Enter your name..." maxlength="50">
                    </div>
                </div>
                
                <!-- Let's get into the story button (positioned under Step 4) -->
                <div class="story-button-container">
                    <button id="story-button" class="btn-primary story-btn" disabled>
                        All done!
                    </button>
                </div>
            </div>
        `;
        
        // Add event listeners
        const navLeftBtn = galleryPage.querySelector('#gallery-nav-left');
        const navRightBtn = galleryPage.querySelector('#gallery-nav-right');
        
        // Navigation button event listeners
        navLeftBtn.addEventListener('click', () => {
            this.scrollGalleryLeft();
        });
        
        navRightBtn.addEventListener('click', () => {
            this.scrollGalleryRight();
        });
        
        return galleryPage;
    }

    // Populate gallery with painting thumbnails
    populateGallery(galleryPage, recommendations) {
        console.log('🎨 Populating gallery with recommendations:', recommendations);
        
        if (!recommendations || recommendations.length === 0) {
            console.error('❌ No recommendations provided to populateGallery');
            return;
        }

        const galleryGrid = galleryPage.querySelector('#gallery-grid');
        if (!galleryGrid) {
            console.error('❌ Gallery grid not found');
            return;
        }

        // Clear existing content
        galleryGrid.innerHTML = '';

        // Create gallery items
        recommendations.forEach((url, index) => {
            const galleryItem = document.createElement('div');
            galleryItem.className = 'gallery-item draggable';
            galleryItem.draggable = true;
            galleryItem.dataset.index = index;
            galleryItem.dataset.url = url;

            // Get detailed information for this painting
            const detailedInfo = this.currentDetailedRecommendations && this.currentDetailedRecommendations[index] 
                ? this.currentDetailedRecommendations[index] 
                : { title: `Painting ${index + 1}`, artist: 'Unknown Artist', year: 'Unknown Year' };
            
            console.log(`🎨 Painting ${index + 1} details:`, detailedInfo);

            galleryItem.innerHTML = `
                <div class="thumbnail-container">
                    <img src="${url}" alt="Painting ${index + 1}" class="thumbnail-image" 
                         onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjgwIiBoZWlnaHQ9IjIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIG5vdCBhdmFpbGFibGU8L3RleHQ+PC9zdmc+'">
                    <div class="thumbnail-overlay">${index + 1}</div>
                    <div class="view-full-overlay">
                        <div class="view-full-content">
                            <div class="painting-title">${detailedInfo.title}</div>
                            <div class="painting-artist-year">${detailedInfo.artist}, ${detailedInfo.year}</div>
                            <div class="painting-action">Click to view the painting</div>
                        </div>
                        <span class="view-full-text default-text">Click to view this painting</span>
                    </div>
                </div>
            `;

            // Add click handler for full view (separate from drag functionality)
            galleryItem.addEventListener('click', (e) => {
                // Only trigger if not currently dragging
                if (!galleryItem.classList.contains('dragging')) {
                    e.preventDefault();
                    e.stopPropagation();
                    this.openPaintingFullView(url, index + 1);
                }
            });

            galleryGrid.appendChild(galleryItem);
        });

        // Setup drag and drop functionality
        this.setupDropZones(galleryPage);
        this.setupGalleryDragAndDrop(galleryPage);
        
        // Setup character cards
        this.setupCharacterCards(galleryPage);
        
        // Setup name input functionality
        this.setupNameInput(galleryPage);
        
        console.log(`✅ Gallery populated with ${recommendations.length} paintings`);
    }

    // Open painting in new tab when clicked
    openPaintingFullView(url, index) {
        console.log(`🎨 Opening painting ${index} in new tab:`, url);
        try {
            window.open(url, '_blank', 'noopener,noreferrer');
        } catch (error) {
            console.error('❌ Error opening painting URL:', error);
            // Fallback: try to open directly
            const link = document.createElement('a');
            link.href = url;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }

    // Setup drag and drop for gallery items
    setupGalleryDragAndDrop(galleryPage) {
        const galleryItems = galleryPage.querySelectorAll('.gallery-item.draggable');
        
        galleryItems.forEach(item => {
            // Mouse events for drag start/end
            item.addEventListener('mousedown', (e) => {
                item.classList.add('mouse-down');
                setTimeout(() => item.classList.remove('mouse-down'), 200);
            });

            // Drag events
            item.addEventListener('dragstart', (e) => {
                console.log('🎯 Drag started for item:', item.dataset.index);
                
                item.classList.add('dragging');
                
                // Set drag data
                e.dataTransfer.setData('text/plain', JSON.stringify({
                    index: parseInt(item.dataset.index),
                    url: item.dataset.url
                }));
                
                // Create custom drag image with complete styling
                const originalImage = item.querySelector('.thumbnail-image');
                const dragImage = document.createElement('div');
                
                // Style the drag container
                dragImage.style.position = 'absolute';
                dragImage.style.top = '-2000px'; // Position far off-screen
                dragImage.style.left = '-2000px';
                dragImage.style.width = '280px';
                dragImage.style.height = '220px';
                dragImage.style.borderRadius = '15px';
                dragImage.style.overflow = 'hidden';
                dragImage.style.boxShadow = '0 15px 35px rgba(255, 255, 255, 0.4)';
                dragImage.style.border = '2px solid rgba(255, 255, 255, 0.6)';
                dragImage.style.background = 'rgba(255, 255, 255, 0.08)';
                dragImage.style.pointerEvents = 'none';
                dragImage.style.zIndex = '9999';
                dragImage.style.transform = 'rotate(3deg)';
                
                // Clone and style the image
                const clonedImage = originalImage.cloneNode(true);
                clonedImage.style.width = '100%';
                clonedImage.style.height = '100%';
                clonedImage.style.objectFit = 'cover';
                clonedImage.style.opacity = '0.9';
                clonedImage.style.display = 'block';
                clonedImage.style.margin = '0';
                clonedImage.style.padding = '0';
                clonedImage.style.border = 'none';
                clonedImage.style.borderRadius = '0';
                
                // Add image to container
                dragImage.appendChild(clonedImage);
                
                // Append to body and ensure it's rendered
                document.body.appendChild(dragImage);
                
                // Force a reflow to ensure the element is fully rendered
                dragImage.offsetHeight;
                
                // Set drag image with proper offset for cursor positioning
                e.dataTransfer.setDragImage(dragImage, 140, 110);
                
                // Remove the temporary drag image after drag starts
                setTimeout(() => {
                    if (document.body.contains(dragImage)) {
                        document.body.removeChild(dragImage);
                    }
                }, 100);
                
                // Setup auto-scroll
                this.setupGlobalDragListeners();
            });

            item.addEventListener('dragend', (e) => {
                console.log('🏁 Drag ended for item:', item.dataset.index);
                
                item.classList.remove('dragging');
                item.classList.add('recently-dragged');
                
                // Remove recently-dragged class after animation
                setTimeout(() => {
                    item.classList.remove('recently-dragged');
                }, 300);
                
                // Clean up auto-scroll
                this.removeGlobalDragListeners();
            });
        });
    }

    // Setup character card click handlers
    setupCharacterCards(galleryPage) {
        const characterCards = galleryPage.querySelectorAll('.character-card');
        
        characterCards.forEach(card => {
            card.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const styleNumber = card.dataset.style;
                console.log(`🎭 Character style ${styleNumber} selected`);
                
                this.handleCharacterSelection(styleNumber);
            });
            
            // Add hover effects with image swapping
            card.addEventListener('mouseenter', () => {
                card.classList.add('character-hover');
                
                // Swap image from style{n}-a.png to style{n}-b.png
                const img = card.querySelector('.character-image');
                const styleNumber = card.dataset.style;
                if (img && styleNumber) {
                    const originalSrc = img.src;
                    // Store original src for restoration
                    img.dataset.originalSrc = originalSrc;
                    // Change to -b version
                    const newSrc = originalSrc.replace(`style${styleNumber}-a.png`, `style${styleNumber}-b.png`);
                    img.src = newSrc;
                }
            });
            
            card.addEventListener('mouseleave', () => {
                card.classList.remove('character-hover');
                
                // Restore original image
                const img = card.querySelector('.character-image');
                if (img && img.dataset.originalSrc) {
                    img.src = img.dataset.originalSrc;
                    // Clean up the data attribute
                    delete img.dataset.originalSrc;
                }
            });
        });
        
        // Initialize character cards in disabled state (Step 2 must be completed first)
        this.disableCharacterCards();
        
        // Setup story button event listener
        const storyButton = galleryPage.querySelector('#story-button');
        if (storyButton) {
            storyButton.addEventListener('click', () => {
                this.handleStoryButtonClick();
            });
        }
        
        // Initialize story button with proper state
        this.updateStoryButton();
        
        console.log('🎭 Character cards initialized in disabled state');
    }

    // Handle character selection
    handleCharacterSelection(styleNumber) {
        // Check if step 2 is complete before allowing character selection
        if (!this.step2Complete) {
            this.showValidationMessage('Please complete Step 2 first by dragging 3 paintings into the boxes');
            console.log('⚠️ Character selection blocked - Step 2 not complete');
            return;
        }
        
        console.log(`🎨 Processing character selection: Style ${styleNumber}`);
        
        // Remove selection from previously selected character
        if (this.selectedCharacter !== null) {
            const previousCard = document.querySelector(`.character-card[data-style="${this.selectedCharacter}"]`);
            if (previousCard) {
                previousCard.classList.remove('character-selected');
                // Remove cancel button from previous card
                const existingCancelBtn = previousCard.querySelector('.character-cancel-btn');
                if (existingCancelBtn) {
                    existingCancelBtn.remove();
                }
                // Restore original image if it was swapped
                const previousImg = previousCard.querySelector('.character-image');
                if (previousImg && previousImg.dataset.originalSrc) {
                    previousImg.src = previousImg.dataset.originalSrc;
                    delete previousImg.dataset.originalSrc;
                }
            }
        }
        
        // Select the new character
        this.selectedCharacter = styleNumber;
        const selectedCard = document.querySelector(`.character-card[data-style="${styleNumber}"]`);
        if (selectedCard) {
            selectedCard.classList.add('character-selected');
            
            // Add circular cancel button with white cross to selected card
            const cancelBtn = document.createElement('div');
            cancelBtn.className = 'character-cancel-btn';
            cancelBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.cancelCharacterSelection();
            });
            selectedCard.appendChild(cancelBtn);
        }
        
        // Update step 3 completion status
        this.step3Complete = this.selectedCharacter !== null;
        
        // Update name input visibility and story button state
        this.updateNameInputVisibility();
        this.updateStoryButton();
        
        console.log('✅ Step 3 completed - Character selected');
        
        // Note: Removed the selection message as requested
    }
    
    // Cancel character selection
    cancelCharacterSelection() {
        console.log('❌ Cancelling character selection');
        
        if (this.selectedCharacter !== null) {
            const selectedCard = document.querySelector(`.character-card[data-style="${this.selectedCharacter}"]`);
            if (selectedCard) {
                selectedCard.classList.remove('character-selected');
                // Remove cancel button
                const cancelBtn = selectedCard.querySelector('.character-cancel-btn');
                if (cancelBtn) {
                    cancelBtn.remove();
                }
                // Ensure image reverts to -a version
                const img = selectedCard.querySelector('.character-image');
                if (img) {
                    const styleNumber = this.selectedCharacter;
                    const originalSrc = img.src.replace(`style${styleNumber}-b.png`, `style${styleNumber}-a.png`);
                    img.src = originalSrc;
                    // Clean up any stored original src
                    if (img.dataset.originalSrc) {
                        delete img.dataset.originalSrc;
                    }
                }
            }
        }
        
        // Reset selected character
        this.selectedCharacter = null;
        
        // Update step 3 completion status
        this.step3Complete = false;
        
        // Update name input visibility and story button state
        this.updateNameInputVisibility();
        this.updateStoryButton();
        
        console.log('⚠️ Step 3 incomplete - Character deselected');
    }
    
    // Enable character cards when step 2 is complete
    enableCharacterCards() {
        const characterCards = document.querySelectorAll('.character-card');
        characterCards.forEach(card => {
            card.classList.remove('disabled');
            card.style.pointerEvents = 'auto';
            card.style.opacity = '1';
        });
        
        // Update step 3 title to show it's now available
        const step3Title = document.querySelector('.character-title');
        if (step3Title) {
            step3Title.classList.remove('step-disabled');
        }
    }
    
    // Disable character cards when step 2 is incomplete
    disableCharacterCards() {
        const characterCards = document.querySelectorAll('.character-card');
        characterCards.forEach(card => {
            card.classList.add('disabled');
            card.style.pointerEvents = 'none';
            card.style.opacity = '0.5';
        });
        
        // Reset character selection if step 2 becomes incomplete
        if (this.selectedCharacter !== null) {
            this.cancelCharacterSelection();
        }
        
        // Update step 3 title to show it's disabled
        const step3Title = document.querySelector('.character-title');
        if (step3Title) {
            step3Title.classList.add('step-disabled');
        }
    }
    
    // Update story button state based on steps completion and name input
    updateStoryButton() {
        const storyButton = document.getElementById('story-button');
        if (storyButton) {
            const hasName = this.userName && this.userName.trim().length > 0;
            const shouldEnable = this.step2Complete && this.step3Complete && hasName;
            storyButton.disabled = !shouldEnable;
            
            // Update visual styles based on enabled state
            if (shouldEnable) {
                storyButton.style.opacity = '1';
                storyButton.style.cursor = 'pointer';
            } else {
                storyButton.style.opacity = '0.6';
                storyButton.style.cursor = 'not-allowed';
            }
            
            // Update button text based on state
            if (!this.step2Complete && !this.step3Complete) {
                storyButton.textContent = 'Complete All Steps';
                storyButton.title = 'Please complete Step 2 (drag 3 paintings) and Step 3 (select a character)';
            } else if (!this.step2Complete) {
                storyButton.textContent = 'Complete Step 2';
                storyButton.title = 'Please complete Step 2 by dragging 3 paintings into the boxes';
            } else if (!this.step3Complete) {
                storyButton.textContent = 'Complete Step 3';
                storyButton.title = 'Please complete Step 3 by selecting a character';
            } else {
                storyButton.textContent = "All done!";
                if (hasName) {
                    storyButton.title = ''; // Remove tooltip when ready
                } else {
                    storyButton.title = 'Please enter your name to continue';
                }
            }
        }
    }
    
    // Setup name input functionality
    setupNameInput(galleryPage) {
        const nameInput = galleryPage.querySelector('#user-name-input');
        
        if (nameInput) {
            // Handle input changes
            nameInput.addEventListener('input', (e) => {
                const name = e.target.value.trim();
                this.userName = name;
                
                // Update story button state
                this.updateStoryButton();
                
                console.log(`📝 Name input: "${name}"`);
            });
            
            // Handle enter key
            nameInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && this.userName && this.userName.trim().length > 0) {
                    this.handleStoryButtonClick();
                }
            });
        }
        
        console.log('📝 Name input functionality initialized');
    }
    
    // Update name input area visibility based on steps 2 and 3 completion
    updateNameInputVisibility() {
        const nameInputArea = document.getElementById('name-input-area');
        if (nameInputArea) {
            const shouldShow = this.step2Complete && this.step3Complete;
            if (shouldShow && nameInputArea.style.display === 'none') {
                nameInputArea.style.display = 'block';
                console.log('📝 Name input area shown');
                
                // Focus on the name input when it becomes visible
                setTimeout(() => {
                    const nameInput = document.getElementById('user-name-input');
                    if (nameInput) {
                        nameInput.focus();
                    }
                }, 100);
            } else if (!shouldShow && nameInputArea.style.display !== 'none') {
                nameInputArea.style.display = 'none';
                console.log('📝 Name input area hidden');
                
                // Reset name input when hidden
                this.userName = '';
                const nameInput = document.getElementById('user-name-input');
                if (nameInput) {
                    nameInput.value = '';
                }
            }
        }
    }
    
    // Show validation message when user tries to interact prematurely
    showValidationMessage(message) {
        // Create or get existing validation message element
        let validationMsg = document.getElementById('validation-message');
        if (!validationMsg) {
            validationMsg = document.createElement('div');
            validationMsg.id = 'validation-message';
            validationMsg.className = 'validation-message';
            validationMsg.style.cssText = `
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(255, 87, 87, 0.95);
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-family: 'Poppins', sans-serif;
                font-weight: 500;
                font-size: 14px;
                z-index: 10000;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                opacity: 0;
                transition: opacity 0.3s ease;
                pointer-events: none;
            `;
            document.body.appendChild(validationMsg);
        }
        
        validationMsg.textContent = message;
        validationMsg.style.opacity = '1';
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            validationMsg.style.opacity = '0';
        }, 3000);
    }
    
    // Handle story button click
    async handleStoryButtonClick() {
        console.log('📖 Story button clicked');
        
        // Show loading popup immediately
        this.showStoryLoadingPopup();
        
        try {
            if (this.selectedCharacter && this.selectedPaintings.length === 3 && this.userName.trim()) {
                // Update button state
                const storyButton = document.getElementById('story-button');
                if (storyButton) {
                    storyButton.textContent = 'Processing...';
                    storyButton.disabled = true;
                    storyButton.style.opacity = '0.6';
                    storyButton.style.cursor = 'not-allowed';
                }
                
                // Map selected paintings to their detailed information
                const paintingsWithDetails = this.selectedPaintings.map(painting => {
                    const detailedInfo = this.currentDetailedRecommendations[painting.index];
                    if (!detailedInfo) {
                        console.error('❌ No detailed info found for painting index:', painting.index);
                        return {
                            title: 'Unknown Title',
                            artist: 'Unknown Artist',
                            year: 'Unknown Year',
                            url: painting.url
                        };
                    }
                    return {
                        title: detailedInfo.title,
                        artist: detailedInfo.artist,
                        year: detailedInfo.year,
                        url: detailedInfo.url
                    };
                });
                
                // Prepare story data with emotion information
                const storyData = {
                    paintings: paintingsWithDetails,
                    narrative_style: this.getSelectedNarrativeStyle(),
                    user_name: this.userName.trim(),
                    emotion: this.selectedEmotion ? this.selectedEmotion.emotion : null,
                    emotion_probability: this.selectedEmotion ? parseFloat(this.selectedEmotion.probability) : null
                };
                
                console.log('📤 Sending story generation request:', storyData);
                if (storyData.emotion && storyData.emotion_probability !== null) {
                    console.log(`📭 Including emotion data: ${storyData.emotion} (${storyData.emotion_probability}%)`);
                }
                
                // Send to backend with timeout using AbortController for better compatibility
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout
                
                const response = await fetch('/api/generate-story', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(storyData),
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                
                console.log('📥 Response status:', response.status);
                console.log('📥 Response headers:', response.headers);
                
                if (!response.ok) {
                    const errorText = await response.text();
                    console.error('❌ Server error response:', errorText);
                    throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
                }
                
                const result = await response.json();
                console.log('📖 Story generation result:', result);
                
                if (result.success) {
                    console.log('✅ Story generated successfully');
                    // Store the story data
                    this.currentStory = result;
                    
                    // Hide loading popup
                    this.hideStoryLoadingPopup();
                    
                    // Show story page - fix the function call
                    this.showStoryInterface(result);
                } else {
                    console.error('❌ Story generation failed:', result.error);
                    throw new Error(result.error || 'Story generation failed');
                }
            } else {
                // Hide loading popup if validation fails
                this.hideStoryLoadingPopup();
                console.log('❌ Validation failed - missing requirements');
                this.showValidationMessage('Please ensure you have selected 3 paintings, a character, and entered your name.');
            }
        } catch (error) {
            console.error('❌ Story generation failed:', error);
            
            // Always hide loading popup on error
            this.hideStoryLoadingPopup();
            
            // Reset button state
            const storyButton = document.getElementById('story-button');
            if (storyButton) {
                storyButton.textContent = 'All done!';
                storyButton.disabled = false;
                storyButton.style.opacity = '1';
                storyButton.style.cursor = 'pointer';
            }
            
            // Show appropriate error message
            if (error.name === 'AbortError') {
                this.showValidationMessage('Story generation timed out. Please try again.');
            } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                this.showValidationMessage('Network error. Please check your connection and try again.');
            } else if (error.message.includes('HTTP error')) {
                this.showValidationMessage('Server error. Please try again in a moment.');
            } else {
                this.showValidationMessage('Failed to generate story. Please try again.');
            }
        }
    }
    
    // Get selected narrative style based on character selection
    getSelectedNarrativeStyle() {
        const styleMap = {
            1: 'historian',
            2: 'poet', 
            3: 'detective',
            4: 'critic',
            5: 'time_traveller'
        };
        
        return styleMap[this.selectedCharacter] || 'historian';
    }
    
    // Show story loading popup
    showStoryLoadingPopup() {
        // Remove existing popup if any
        this.hideStoryLoadingPopup();
        
        // Clear any existing timeout
        if (this.storyLoadingTimeout) {
            clearTimeout(this.storyLoadingTimeout);
        }
        
        // Freeze the page
        document.body.classList.add('story-loading');
        
        // Create loading popup
        const loadingPopup = document.createElement('div');
        loadingPopup.id = 'story-loading-popup';
        loadingPopup.className = 'story-loading-popup';
        
        loadingPopup.innerHTML = `
            <div class="story-loading-content">
                <img src="image/dance.gif" alt="Loading..." class="story-loading-gif">
            </div>
            <p class="story-loading-text">Your story is creating. Please hold on a moment...</p>
        `;
        
        document.body.appendChild(loadingPopup);
        
        // Trigger animation
        setTimeout(() => {
            loadingPopup.classList.add('visible');
        }, 10);
        
        // Safety timeout - automatically hide after 60 seconds
        this.storyLoadingTimeout = setTimeout(() => {
            console.warn('⚠️ Story loading popup timed out after 60 seconds');
            this.hideStoryLoadingPopup();
            this.showValidationMessage('Story generation is taking longer than expected. Please try again.');
            
            // Reset button state
            const storyButton = document.getElementById('story-button');
            if (storyButton) {
                storyButton.textContent = 'All done!';
                storyButton.disabled = false;
                storyButton.style.opacity = '1';
                storyButton.style.cursor = 'pointer';
            }
        }, 60000);
        
        console.log('🎭 Story loading popup shown with page frozen (60s timeout set)');
    }
    
    // Hide story loading popup
    hideStoryLoadingPopup() {
        // Clear timeout
        if (this.storyLoadingTimeout) {
            clearTimeout(this.storyLoadingTimeout);
            this.storyLoadingTimeout = null;
        }
        
        const loadingPopup = document.getElementById('story-loading-popup');
        if (loadingPopup) {
            loadingPopup.classList.remove('visible');
            setTimeout(() => {
                loadingPopup.remove();
                // Unfreeze the page
                document.body.classList.remove('story-loading');
            }, 300);
        } else {
            // Make sure page is unfrozen even if popup doesn't exist
            document.body.classList.remove('story-loading');
        }
        console.log('🎭 Story loading popup hidden and page unfrozen');
    }

    // Scroll gallery left
    scrollGalleryLeft() {
        console.log('⬅️ Scrolling gallery left');
        const galleryGrid = document.querySelector('#gallery-grid');
        if (galleryGrid) {
            // Calculate scroll amount based on gallery item width + gap
            const galleryItem = galleryGrid.querySelector('.gallery-item');
            const scrollAmount = galleryItem ? galleryItem.offsetWidth + 15 : 300; // 15px is the gap between items
            
            galleryGrid.scrollBy({
                left: -scrollAmount * 2, // Scroll 2 items at a time
                behavior: 'smooth'
            });
        }
    }

    // Scroll gallery right  
    scrollGalleryRight() {
        console.log('➡️ Scrolling gallery right');
        const galleryGrid = document.querySelector('#gallery-grid');
        if (galleryGrid) {
            // Calculate scroll amount based on gallery item width + gap
            const galleryItem = galleryGrid.querySelector('.gallery-item');
            const scrollAmount = galleryItem ? galleryItem.offsetWidth + 15 : 300; // 15px is the gap between items
            
            galleryGrid.scrollBy({
                left: scrollAmount * 2, // Scroll 2 items at a time
                behavior: 'smooth'
            });
        }
    }
    

    
    // Show new story interface
    showStoryInterface(storyData) {
        console.log('📖 Showing story interface');
        
        // Hide gallery page
        const galleryPage = document.getElementById('gallery-page');
        if (galleryPage) {
            galleryPage.style.display = 'none';
        }
        
        // Split story into paragraphs
        const storyParagraphs = storyData.story.split('\n\n').filter(p => p.trim().length > 0);
        
        // Distribute paragraphs across paintings (roughly equal distribution)
        const totalParagraphs = storyParagraphs.length;
        const paragraphsPerPainting = Math.floor(totalParagraphs / 3);
        const remainingParagraphs = totalParagraphs % 3;
        
        // Calculate paragraph distribution
        let painting1Paragraphs = paragraphsPerPainting + (remainingParagraphs > 0 ? 1 : 0);
        let painting2Paragraphs = paragraphsPerPainting + (remainingParagraphs > 1 ? 1 : 0);
        let painting3Paragraphs = paragraphsPerPainting;
        
        // Extract paragraphs for each painting
        const painting1Text = storyParagraphs.slice(0, painting1Paragraphs).join('\\n\\n');
        const painting2Text = storyParagraphs.slice(painting1Paragraphs, painting1Paragraphs + painting2Paragraphs).join('\\n\\n');
        const painting3Text = storyParagraphs.slice(painting1Paragraphs + painting2Paragraphs, painting1Paragraphs + painting2Paragraphs + painting3Paragraphs).join('\\n\\n');
        
        // Remaining text (if any)
        const remainingText = storyParagraphs.slice(painting1Paragraphs + painting2Paragraphs + painting3Paragraphs).join('\\n\\n');
        
        // Create story interface
        const storyInterface = document.createElement('div');
        storyInterface.id = 'story-interface';
        storyInterface.className = 'story-interface';
        
        storyInterface.innerHTML = `
            <div class="story-container">
                <!-- Story Title -->
                <div class="story-header">
                    <h1 class="story-main-title">${storyData.narrative_style}</h1>
                </div>
                
                <!-- Painting 1 Section -->
                <div class="story-painting-section">
                    <img src="${storyData.paintings[0].url}" alt="${storyData.paintings[0].title}" class="story-painting-image">
                    <h3 class="story-painting-title">${storyData.paintings[0].title}</h3>
                    <p class="story-painting-details">${storyData.paintings[0].artist}, ${storyData.paintings[0].year}</p>
                    <div class="story-text-paragraph">
                        ${painting1Text.split('\\n\\n').map(p => `<p>${p}</p>`).join('')}
                    </div>
                </div>
                
                <!-- Painting 2 Section -->
                <div class="story-painting-section">
                    <img src="${storyData.paintings[1].url}" alt="${storyData.paintings[1].title}" class="story-painting-image">
                    <h3 class="story-painting-title">${storyData.paintings[1].title}</h3>
                    <p class="story-painting-details">${storyData.paintings[1].artist}, ${storyData.paintings[1].year}</p>
                    <div class="story-text-paragraph">
                        ${painting2Text.split('\\n\\n').map(p => `<p>${p}</p>`).join('')}
                    </div>
                </div>
                
                <!-- Painting 3 Section -->
                <div class="story-painting-section">
                    <img src="${storyData.paintings[2].url}" alt="${storyData.paintings[2].title}" class="story-painting-image">
                    <h3 class="story-painting-title">${storyData.paintings[2].title}</h3>
                    <p class="story-painting-details">${storyData.paintings[2].artist}, ${storyData.paintings[2].year}</p>
                    <div class="story-text-paragraph">
                        ${painting3Text.split('\\n\\n').map(p => `<p>${p}</p>`).join('')}
                    </div>
                </div>
                
                ${remainingText ? `
                <!-- Remaining Story Text -->
                <div class="story-remaining-text">
                    ${remainingText.split('\\n\\n').map(p => `<p>${p}</p>`).join('')}
                </div>
                ` : ''}
                
                <!-- Story Actions -->
                <div class="story-actions">
                    <button class="story-action-btn btn-share" id="share-story-btn" onclick="window.gradientApp.showSharePopup()">Share my story</button>
                    <button class="story-action-btn btn-primary" id="create-another-btn" onclick="window.gradientApp.createAnotherStory()">Create another story</button>
                    <button class="story-action-btn btn-secondary" id="story-recapture-btn" onclick="window.gradientApp.recaptureColors()">Re-capture palettes</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(storyInterface);
        
        // Add backup event listeners for story action buttons
        setTimeout(() => {
            const shareBtn = document.getElementById('share-story-btn');
            const createAnotherBtn = document.getElementById('create-another-btn');
            const recaptureBtn = document.getElementById('story-recapture-btn');
            
            if (shareBtn) {
                shareBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    console.log('📤 Share button clicked (backup listener)');
                    this.showSharePopup();
                });
            }
            
            if (createAnotherBtn) {
                createAnotherBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    console.log('🔄 Create another button clicked (backup listener)');
                    this.createAnotherStory();
                });
            }
            
            if (recaptureBtn) {
                recaptureBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('🎨 Story page re-capture button clicked (backup listener)');
                    console.log('Button element:', recaptureBtn);
                    console.log('Calling recaptureColors...');
                    try {
                        this.recaptureColors();
                        console.log('✅ recaptureColors called successfully from story page');
                    } catch (error) {
                        console.error('❌ Error calling recaptureColors from story page:', error);
                        alert('Error re-capturing palette. Please refresh the page.');
                    }
                });
                console.log('✅ Story page re-capture button listener attached');
            } else {
                console.warn('⚠️ Story re-capture button not found for event listener');
            }
            
            console.log('✅ Story action button listeners attached');
        }, 100);
        
        console.log('📖 Story interface displayed');
    }
    
    // Show share popup
    showSharePopup() {
        console.log('📤 Showing share popup');
        console.log('Share popup function called successfully!');
        
        try {
            // Remove existing popup if any
            this.hideSharePopup();
            
            // Create share popup
            const sharePopup = document.createElement('div');
            sharePopup.id = 'share-popup';
            sharePopup.className = 'share-popup';
            
            sharePopup.innerHTML = `
                <div class="share-popup-content">
                    <div class="share-close-btn" onclick="window.gradientApp.hideSharePopup()">×</div>
                    <div class="share-options">
                        <div class="share-option" onclick="window.gradientApp.shareToInstagram()">
                            <img src="image/ig.png" alt="Instagram">
                        </div>
                        <div class="share-option" onclick="window.gradientApp.shareToX()">
                            <img src="image/x.png" alt="X (Twitter)">
                        </div>
                        <div class="share-option" onclick="window.gradientApp.shareToFacebook()">
                            <img src="image/f.png" alt="Facebook">
                        </div>
                    </div>
                    <p class="share-popup-title">Choose where to share...</p>
                </div>
            `;
            
            document.body.appendChild(sharePopup);
            
            // Add backup event listener for close button
            setTimeout(() => {
                const closeBtn = sharePopup.querySelector('.share-close-btn');
                if (closeBtn) {
                    closeBtn.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('❌ Share popup close button clicked (backup listener)');
                        this.hideSharePopup();
                    });
                }
            }, 50);
            
            // Trigger animation
            setTimeout(() => {
                sharePopup.classList.add('visible');
            }, 10);
            
            console.log('✅ Share popup created and displayed');
        } catch (error) {
            console.error('❌ Error showing share popup:', error);
            alert('Share functionality temporarily unavailable');
        }
    }

    // Hide share popup
    hideSharePopup() {
        try {
            const sharePopup = document.getElementById('share-popup');
            if (sharePopup) {
                sharePopup.classList.remove('visible');
                setTimeout(() => {
                    sharePopup.remove();
                }, 300);
                console.log('✅ Share popup hidden');
            }
        } catch (error) {
            console.error('❌ Error hiding share popup:', error);
        }
    }

    // Share to Instagram
    shareToInstagram() {
        try {
            console.log('📱 Sharing to Instagram');
            // Note: Instagram doesn't support direct web sharing, so we'll copy link to clipboard
            this.copyStoryLinkToClipboard();
            alert('Story link copied to clipboard! You can paste it in Instagram.');
            this.hideSharePopup();
        } catch (error) {
            console.error('❌ Error sharing to Instagram:', error);
            alert('Instagram sharing temporarily unavailable');
        }
    }

    // Share to X (Twitter)
    shareToX() {
        try {
            console.log('🐦 Sharing to X');
            const shareText = encodeURIComponent('Check out my personalized art story created with Plot & Palette! 🎨');
            const shareUrl = encodeURIComponent(window.location.href);
            window.open(`https://twitter.com/intent/tweet?text=${shareText}&url=${shareUrl}`, '_blank');
            this.hideSharePopup();
        } catch (error) {
            console.error('❌ Error sharing to X:', error);
            alert('X sharing temporarily unavailable');
        }
    }

    // Share to Facebook
    shareToFacebook() {
        try {
            console.log('👥 Sharing to Facebook');
            const shareUrl = encodeURIComponent(window.location.href);
            window.open(`https://www.facebook.com/sharer/sharer.php?u=${shareUrl}`, '_blank');
            this.hideSharePopup();
        } catch (error) {
            console.error('❌ Error sharing to Facebook:', error);
            alert('Facebook sharing temporarily unavailable');
        }
    }

    // Copy story link to clipboard
    async copyStoryLinkToClipboard() {
        try {
            await navigator.clipboard.writeText(window.location.href);
            console.log('🔗 Story link copied to clipboard');
        } catch (error) {
            console.error('Failed to copy link:', error);
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = window.location.href;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
        }
    }

    // Create another story - redirect to gallery page with same paintings but clear selections
    createAnotherStory() {
        try {
            console.log('🔄 Creating another story');
            console.log('Create another story function called successfully!');
            
            // Hide story interface
            const storyInterface = document.getElementById('story-interface');
            if (storyInterface) {
                storyInterface.remove();
                console.log('✅ Story interface removed');
            }
            
            // Show gallery page
            const galleryPage = document.getElementById('gallery-page');
            if (galleryPage) {
                galleryPage.style.display = 'block';
                // Scroll to top of gallery page to show paintings
                galleryPage.scrollTop = 0;
                console.log('✅ Gallery page shown and scrolled to top');
            } else {
                // If gallery page doesn't exist, recreate it
                if (this.currentDetailedRecommendations && this.currentDetailedRecommendations.length > 0) {
                    console.log('🔄 Recreating gallery page');
                    this.showGalleryWithoutColorDashboard(this.currentDetailedRecommendations);
                    return;
                } else {
                    console.error('❌ No recommendations available for gallery recreation');
                    alert('Unable to return to gallery. Please re-capture palette.');
                    return;
                }
            }
            
            // Clear user selections but keep paintings
            this.selectedPaintings = [];
            this.selectedCharacter = null;
            this.selectedNarrativeStyle = null;
            this.userName = '';
            this.step2Complete = false;
            this.step3Complete = false;
            
            // Reset drop zones
            for (let i = 0; i < 3; i++) {
                const dropZone = document.querySelector(`.drop-zone[data-slot="${i}"]`);
                if (dropZone) {
                    const icons = ['🎨', '🖼️', '🎭'];
                    dropZone.innerHTML = `
                        <div class="drop-zone-content">
                            <div class="drop-zone-icon">${icons[i]}</div>
                            <div class="drop-zone-text">Drop painting ${i + 1} here</div>
                        </div>
                    `;
                    dropZone.classList.remove('filled');
                }
            }
            
            // Reset character selection completely
            const characterCards = document.querySelectorAll('.character-card');
            characterCards.forEach(card => {
                card.classList.remove('character-selected');
                
                // Remove any existing cancel buttons (cross buttons)
                const existingCancelBtn = card.querySelector('.character-cancel-btn');
                if (existingCancelBtn) {
                    existingCancelBtn.remove();
                }
                
                // Ensure image reverts to original -a version
                const img = card.querySelector('.character-image');
                if (img) {
                    const styleNumber = card.dataset.style;
                    if (styleNumber) {
                        // Force image back to -a version
                        const originalSrc = `image/style${styleNumber}-a.png`;
                        img.src = originalSrc;
                        // Clean up any stored original src
                        if (img.dataset.originalSrc) {
                            delete img.dataset.originalSrc;
                        }
                    }
                }
            });
            
            // Reset name input
            const nameInput = document.getElementById('name-input');
            if (nameInput) {
                nameInput.value = '';
            }
            
            // Update button states
            this.updateSelectionButtons();
            this.updateNameInputVisibility();
            this.updateStoryButton();
            
            // Ensure story button is properly reset
            const storyButton = document.getElementById('story-button');
            if (storyButton) {
                storyButton.disabled = true; // Will be enabled when all steps are complete
                storyButton.textContent = 'Complete All Steps';
                storyButton.style.opacity = '0.6';
                storyButton.style.cursor = 'not-allowed';
            }
            
            // Reset character cards to disabled state initially
            this.disableCharacterCards();
            
            console.log('✅ Ready for new story creation');
        } catch (error) {
            console.error('❌ Error creating another story:', error);
            alert('Unable to create another story. Please refresh the page.');
        }
    }
}

// Add immediate console log to verify script loading
console.log('🚀 Script.js loading...');

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎯 DOM loaded, initializing app...');
    try {
        const app = new GradientPalette();
        console.log('✅ GradientPalette created successfully');
        
        // Force hide all overlay elements immediately
        const loading = document.getElementById('loading');
        const modal = document.getElementById('result-modal');
        
        if (loading) {
            loading.classList.add('hidden');
            loading.classList.remove('visible');
            loading.style.display = 'none';
            console.log('Loading overlay force hidden');
        }
        
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('visible');
            modal.style.display = 'none';
            console.log('Modal overlay force hidden');
        }
        
        // Add some visual feedback for performance
        const preferredReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
        if (preferredReducedMotion.matches) {
            document.documentElement.style.setProperty('--animation-duration', '30s');
        }
        
        // Add touch support for mobile
        let touchStartTime = 0;
        document.addEventListener('touchstart', (e) => {
            touchStartTime = Date.now();
        });
        
        document.addEventListener('touchend', (e) => {
            const touchDuration = Date.now() - touchStartTime;
            if (touchDuration > 500 && app.isAnimating) { // Long press
                e.preventDefault();
                app.stopAndCapture();
            }
        });
        
        // Expose app to global scope for debugging
        window.gradientApp = app;
        
    } catch (error) {
        console.error('❌ Error initializing GradientPalette:', error);
        console.error('Error stack:', error.stack);
    }
});

// Performance optimizations
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => console.log('SW registered'))
            .catch(registrationError => console.log('SW registration failed'));
    });
}

// Prevent right-click context menu for cleaner experience
document.addEventListener('contextmenu', (e) => {
    e.preventDefault();
});

// Handle visibility change to pause/resume animations
document.addEventListener('visibilitychange', () => {
    const app = window.gradientApp;
    if (app && document.hidden) {
        app.gradientContainer.style.animationPlayState = 'paused';
    } else if (app && !document.hidden && app.isAnimating) {
        app.gradientContainer.style.animationPlayState = 'running';
    }
}); 