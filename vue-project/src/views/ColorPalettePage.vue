<template>
  <div class="palette-page">
    <div class="palette-container">
      <!-- Header Section -->
      <div class="header-section">
        <h2 class="page-title">Color Palette Analysis</h2>
        <p class="page-subtitle">Discover emotions and art connections through your colors</p>
      </div>

      <!-- Color Palette Display -->
      <div class="palette-section">
        <div class="palette-header">
          <h3>Your Color Palette</h3>
          <p>{{ extractedColors.length }} dominant colors extracted from your image</p>
        </div>
        
        <div class="palette-grid">
          <div 
            v-for="(color, index) in extractedColors" 
            :key="index"
            class="palette-card"
            :class="{ 'selected': selectedColors.includes(index) }"
            @click="toggleColorSelection(index)"
          >
            <div 
              class="color-preview"
              :style="{ backgroundColor: color.hex }"
            ></div>
            <div class="color-info">
              <h4>{{ color.name }}</h4>
              <p class="color-hex">{{ color.hex }}</p>
              <p class="color-percentage">{{ color.percentage }}%</p>
              <div class="color-properties">
                <span class="property-tag">{{ getColorTemperature(color.hex) }}</span>
                <span class="property-tag">{{ getColorBrightness(color.hex) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Emotion Analysis Section -->
      <div class="emotion-section">
        <div class="emotion-header">
          <h3>🎭 Emotion Analysis</h3>
          <p>Based on your color palette, we detect these emotions</p>
        </div>
        
        <div class="emotion-results">
          <div v-if="emotionLoading" class="emotion-loading">
            <div class="loading-spinner"></div>
            <p>Analyzing emotional resonance...</p>
          </div>
          
          <div v-else-if="detectedEmotions.length > 0" class="emotion-grid">
            <div 
              v-for="emotion in detectedEmotions" 
              :key="emotion.name"
              class="emotion-card"
              :class="{ 'primary': emotion.confidence > 0.7 }"
            >
              <div class="emotion-icon">{{ emotion.icon }}</div>
              <h4>{{ emotion.name }}</h4>
              <div class="confidence-bar">
                <div 
                  class="confidence-fill"
                  :style="{ width: `${emotion.confidence * 100}%` }"
                ></div>
              </div>
              <p class="confidence-text">{{ Math.round(emotion.confidence * 100) }}% confidence</p>
            </div>
          </div>
          
          <div v-else class="emotion-placeholder">
            <p>Click "Analyze Emotions" to discover the emotional impact of your colors</p>
            <button @click="analyzeEmotions" class="analyze-btn">
              🔍 Analyze Emotions
            </button>
          </div>
        </div>
      </div>

      <!-- Art Matching Section -->
      <div class="art-section">
        <div class="art-header">
          <h3>🎨 Art Matching</h3>
          <p>Find famous paintings that share your color palette</p>
        </div>
        
        <div class="art-results">
          <div v-if="artLoading" class="art-loading">
            <div class="loading-spinner"></div>
            <p>Searching through art history...</p>
          </div>
          
          <div v-else-if="matchingArtworks.length > 0" class="art-grid">
            <div 
              v-for="artwork in matchingArtworks" 
              :key="artwork.id"
              class="art-card"
              @click="selectArtwork(artwork)"
            >
              <div class="art-image">
                <img :src="artwork.image" :alt="artwork.title" />
                <div class="art-overlay">
                  <div class="match-score">{{ artwork.matchScore }}% match</div>
                </div>
              </div>
              <div class="art-info">
                <h4>{{ artwork.title }}</h4>
                <p class="artist">{{ artwork.artist }}</p>
                <p class="year">{{ artwork.year }}</p>
              </div>
            </div>
          </div>
          
          <div v-else class="art-placeholder">
            <p>Click "Find Art Matches" to discover paintings with similar colors</p>
            <button @click="findArtMatches" class="find-art-btn">
              🖼️ Find Art Matches
            </button>
          </div>
        </div>
      </div>

      <!-- Palette Actions -->
      <div class="actions-section">
        <div class="action-buttons">
          <button @click="downloadPalette" class="download-btn">
            💾 Download Palette
          </button>
          <button @click="generateStory" class="story-btn">
            📖 Generate Story
          </button>
          <button @click="viewGallery" class="gallery-btn">
            🖼️ View Gallery
          </button>
        </div>
      </div>

      <!-- Navigation -->
      <div class="navigation-section">
        <button @click="goBack" class="back-btn">
          ← Back to Gradient
        </button>
        <button @click="proceedToNext" class="continue-btn">
          Continue to Story →
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'ColorPalettePage',
  setup() {
    const router = useRouter()
    const extractedColors = ref([])
    const selectedColors = ref([])
    const detectedEmotions = ref([])
    const matchingArtworks = ref([])
    const emotionLoading = ref(false)
    const artLoading = ref(false)
    
    // Inject global state
    const appState = inject('appState')
    const showLoading = inject('showLoading')
    const hideLoading = inject('hideLoading')
    const showValidation = inject('showValidation')

    // Initialize colors from previous page
    onMounted(() => {
      if (appState?.currentColourData?.value) {
        extractedColors.value = appState.currentColourData.value
      } else {
        // Fallback colors for demo
        extractedColors.value = [
          { hex: '#FF6B6B', name: 'Coral Red', percentage: 25 },
          { hex: '#4ECDC4', name: 'Turquoise', percentage: 20 },
          { hex: '#45B7D1', name: 'Sky Blue', percentage: 18 },
          { hex: '#96CEB4', name: 'Mint Green', percentage: 15 },
          { hex: '#FFEAA7', name: 'Soft Yellow', percentage: 12 },
          { hex: '#DDA0DD', name: 'Plum', percentage: 10 }
        ]
      }
    })

    // Color analysis functions
    const getColorTemperature = (hex) => {
      const rgb = hexToRgb(hex)
      if (!rgb) return 'Neutral'
      
      const { r, g, b } = rgb
      const temp = (r - b) / 255
      
      if (temp > 0.3) return 'Warm'
      if (temp < -0.3) return 'Cool'
      return 'Neutral'
    }

    const getColorBrightness = (hex) => {
      const rgb = hexToRgb(hex)
      if (!rgb) return 'Medium'
      
      const { r, g, b } = rgb
      const brightness = (r * 299 + g * 587 + b * 114) / 1000
      
      if (brightness > 180) return 'Light'
      if (brightness < 75) return 'Dark'
      return 'Medium'
    }

    const hexToRgb = (hex) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
      return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
      } : null
    }

    // Color selection
    const toggleColorSelection = (index) => {
      const selectedIndex = selectedColors.value.indexOf(index)
      if (selectedIndex > -1) {
        selectedColors.value.splice(selectedIndex, 1)
      } else {
        selectedColors.value.push(index)
      }
    }

    // Emotion analysis
    const analyzeEmotions = async () => {
      emotionLoading.value = true
      
      try {
        // Simulate API call to emotion analysis service
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // Mock emotion results based on color analysis
        const emotions = generateEmotionResults(extractedColors.value)
        detectedEmotions.value = emotions
        
        // Store in global state
        if (appState) {
          appState.selectedEmotion.value = emotions[0]?.name || null
        }
        
      } catch (error) {
        console.error('Error analyzing emotions:', error)
        showValidation('Error analyzing emotions. Please try again.')
      } finally {
        emotionLoading.value = false
      }
    }

    const generateEmotionResults = (colors) => {
      const emotionMapping = {
        'red': { name: 'Passion', icon: '❤️', baseConfidence: 0.8 },
        'blue': { name: 'Calm', icon: '💙', baseConfidence: 0.7 },
        'green': { name: 'Harmony', icon: '💚', baseConfidence: 0.75 },
        'yellow': { name: 'Joy', icon: '💛', baseConfidence: 0.85 },
        'purple': { name: 'Mystery', icon: '💜', baseConfidence: 0.65 },
        'orange': { name: 'Energy', icon: '🧡', baseConfidence: 0.8 },
        'pink': { name: 'Love', icon: '💗', baseConfidence: 0.7 },
        'brown': { name: 'Stability', icon: '🤎', baseConfidence: 0.6 },
        'gray': { name: 'Balance', icon: '🩶', baseConfidence: 0.5 },
        'black': { name: 'Power', icon: '🖤', baseConfidence: 0.7 }
      }
      
      const detectedEmotions = []
      
      colors.forEach(color => {
        const colorName = color.name.toLowerCase()
        for (const [key, emotion] of Object.entries(emotionMapping)) {
          if (colorName.includes(key)) {
            const confidence = emotion.baseConfidence * (color.percentage / 100)
            detectedEmotions.push({
              ...emotion,
              confidence: Math.min(confidence + Math.random() * 0.2, 1)
            })
          }
        }
      })
      
      // Add some default emotions if none detected
      if (detectedEmotions.length === 0) {
        detectedEmotions.push(
          { name: 'Creativity', icon: '🎨', confidence: 0.65 },
          { name: 'Inspiration', icon: '✨', confidence: 0.55 }
        )
      }
      
      return detectedEmotions
        .sort((a, b) => b.confidence - a.confidence)
        .slice(0, 4)
    }

    // Art matching
    const findArtMatches = async () => {
      artLoading.value = true
      
      try {
        // Simulate API call to art matching service
        await new Promise(resolve => setTimeout(resolve, 2500))
        
        // Mock art results
        const artworks = generateArtMatches(extractedColors.value)
        matchingArtworks.value = artworks
        
      } catch (error) {
        console.error('Error finding art matches:', error)
        showValidation('Error finding art matches. Please try again.')
      } finally {
        artLoading.value = false
      }
    }

    const generateArtMatches = (colors) => {
      const mockArtworks = [
        {
          id: 1,
          title: 'The Starry Night',
          artist: 'Vincent van Gogh',
          year: '1889',
          image: 'palette GIF/1.gif',
          matchScore: 85
        },
        {
          id: 2,
          title: 'Water Lilies',
          artist: 'Claude Monet',
          year: '1919',
          image: 'palette GIF/2.gif',
          matchScore: 78
        },
        {
          id: 3,
          title: 'The Great Wave',
          artist: 'Katsushika Hokusai',
          year: '1831',
          image: 'palette GIF/3.gif',
          matchScore: 72
        },
        {
          id: 4,
          title: 'Girl with a Pearl Earring',
          artist: 'Johannes Vermeer',
          year: '1665',
          image: 'palette GIF/4.gif',
          matchScore: 69
        }
      ]
      
      return mockArtworks.sort((a, b) => b.matchScore - a.matchScore)
    }

    const selectArtwork = (artwork) => {
      if (appState) {
        appState.selectedPaintings.value = [artwork]
      }
      showValidation(`Selected: ${artwork.title} by ${artwork.artist}`)
    }

    // Action handlers
    const downloadPalette = () => {
      const paletteData = {
        colors: extractedColors.value,
        emotions: detectedEmotions.value,
        timestamp: new Date().toISOString()
      }
      
      const blob = new Blob([JSON.stringify(paletteData, null, 2)], { 
        type: 'application/json' 
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'color-palette.json'
      a.click()
      URL.revokeObjectURL(url)
      
      showValidation('Color palette downloaded!')
    }

    const generateStory = () => {
      if (appState) {
        appState.selectedEmotion.value = detectedEmotions.value[0]?.name || null
        appState.selectedPaintings.value = matchingArtworks.value.slice(0, 1)
      }
      router.push('/story')
    }

    const viewGallery = () => {
      router.push('/gallery')
    }

    // Navigation
    const goBack = () => {
      router.push('/gradient')
    }

    const proceedToNext = () => {
      if (detectedEmotions.value.length === 0) {
        showValidation('Please analyze emotions first to continue')
        return
      }
      
      if (appState) {
        appState.selectedEmotion.value = detectedEmotions.value[0]?.name || null
      }
      router.push('/story')
    }

    return {
      extractedColors,
      selectedColors,
      detectedEmotions,
      matchingArtworks,
      emotionLoading,
      artLoading,
      getColorTemperature,
      getColorBrightness,
      toggleColorSelection,
      analyzeEmotions,
      findArtMatches,
      selectArtwork,
      downloadPalette,
      generateStory,
      viewGallery,
      goBack,
      proceedToNext
    }
  }
}
</script>

<style scoped>
.palette-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.palette-container {
  max-width: 1200px;
  margin: 0 auto;
  color: white;
}

.header-section {
  text-align: center;
  margin-bottom: 40px;
}

.page-title {
  font-family: 'Poppins', sans-serif;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.page-subtitle {
  font-family: 'Poppins', sans-serif;
  font-size: 1.1rem;
  font-weight: 300;
  opacity: 0.9;
}

/* Palette Section */
.palette-section {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 40px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.palette-header {
  text-align: center;
  margin-bottom: 30px;
}

.palette-header h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.palette-header p {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  opacity: 0.8;
}

.palette-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.palette-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  backdrop-filter: blur(5px);
  border: 2px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  cursor: pointer;
}

.palette-card:hover, .palette-card.selected {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.15);
  border-color: #FFD700;
}

.color-preview {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin: 0 auto 15px;
  border: 3px solid white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.color-info h4 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 5px;
}

.color-hex {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  opacity: 0.8;
  margin-bottom: 5px;
}

.color-percentage {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: #FFD700;
  margin-bottom: 10px;
}

.color-properties {
  display: flex;
  gap: 5px;
  justify-content: center;
  flex-wrap: wrap;
}

.property-tag {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 500;
}

/* Emotion Section */
.emotion-section {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 40px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.emotion-header {
  text-align: center;
  margin-bottom: 30px;
}

.emotion-header h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.emotion-header p {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  opacity: 0.8;
}

.emotion-loading, .emotion-placeholder {
  text-align: center;
  padding: 40px;
}

.emotion-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.emotion-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  backdrop-filter: blur(5px);
  border: 2px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.emotion-card.primary {
  border-color: #FFD700;
  background: rgba(255, 215, 0, 0.1);
}

.emotion-card:hover {
  transform: translateY(-3px);
}

.emotion-icon {
  font-size: 2rem;
  margin-bottom: 10px;
}

.emotion-card h4 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.confidence-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff6b6b, #FFD700);
  transition: width 0.5s ease;
}

.confidence-text {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  opacity: 0.8;
}

/* Art Section */
.art-section {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 40px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.art-header {
  text-align: center;
  margin-bottom: 30px;
}

.art-header h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.art-header p {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  opacity: 0.8;
}

.art-loading, .art-placeholder {
  text-align: center;
  padding: 40px;
}

.art-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.art-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  overflow: hidden;
  backdrop-filter: blur(5px);
  border: 2px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  cursor: pointer;
}

.art-card:hover {
  transform: translateY(-5px);
  border-color: #FFD700;
}

.art-image {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.art-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.art-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
}

.match-score {
  background: rgba(255, 215, 0, 0.9);
  color: #333;
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 600;
}

.art-info {
  padding: 15px;
}

.art-info h4 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 5px;
}

.artist {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  opacity: 0.8;
  margin-bottom: 5px;
}

.year {
  font-family: 'Poppins', sans-serif;
  font-size: 0.8rem;
  opacity: 0.7;
}

/* Loading Spinner */
.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid #FFD700;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Action Buttons */
.actions-section {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 40px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.analyze-btn, .find-art-btn, .download-btn, .story-btn, .gallery-btn {
  padding: 12px 24px;
  border-radius: 25px;
  border: none;
  cursor: pointer;
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.analyze-btn:hover, .find-art-btn:hover, .download-btn:hover, 
.story-btn:hover, .gallery-btn:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.3);
}

/* Navigation */
.navigation-section {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-top: 40px;
}

.back-btn, .continue-btn {
  padding: 15px 30px;
  border-radius: 25px;
  border: none;
  cursor: pointer;
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.back-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.continue-btn {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

.back-btn:hover, .continue-btn:hover {
  transform: translateY(-2px);
}

.continue-btn:hover {
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }
  
  .palette-grid, .emotion-grid, .art-grid {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 15px;
  }
  
  .palette-section, .emotion-section, .art-section, .actions-section {
    padding: 20px;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .navigation-section {
    flex-direction: column;
  }
  
  .back-btn, .continue-btn {
    width: 100%;
    padding: 12px 20px;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.8rem;
  }
  
  .palette-grid, .emotion-grid, .art-grid {
    grid-template-columns: 1fr;
  }
  
  .color-preview {
    width: 60px;
    height: 60px;
  }
  
  .art-image {
    height: 150px;
  }
}
</style> 