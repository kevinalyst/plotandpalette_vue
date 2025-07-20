<template>
  <div class="color-palette-page">
    <div class="color-palette-container">
      <!-- Color Chart Display -->
      <div class="color-chart-section">
        <canvas ref="colorChart" class="color-chart"></canvas>
      </div>
      
      <!-- Raw Colors Bar -->
      <div v-if="rawColors && rawColors.length > 0" class="raw-colors-section">
        <h3>Extracted Colors</h3>
        <div class="raw-colors-bar">
          <div 
            v-for="(color, index) in rawColors" 
            :key="index"
            class="color-segment"
            :style="{ backgroundColor: color }"
          ></div>
        </div>
      </div>
      
      <!-- Emotion Prediction Section -->
      <div v-if="emotionPrediction" class="emotion-section">
        <h2>Detected Emotions</h2>
        <p class="emotion-instruction">
          <span class="step-label">Step 2:</span> 
          Choose the emotion that resonates with you most
        </p>
        
        <div class="emotion-cards">
          <div 
            v-for="emotion in topEmotions" 
            :key="emotion.name"
            :class="['emotion-card', { 'selected': selectedEmotion === emotion.name }]"
            @click="selectEmotion(emotion.name, emotion.probability)"
          >
            <div class="emotion-name">{{ emotion.name }}</div>
            <div class="emotion-probability">{{ Math.round(emotion.probability * 100) }}%</div>
            <div class="emotion-bar">
              <div 
                class="emotion-fill" 
                :style="{ width: (emotion.probability * 100) + '%' }"
              ></div>
            </div>
          </div>
        </div>
        
        <button 
          v-if="selectedEmotion"
          class="continue-button"
          @click="proceedToGallery"
        >
          Continue to Gallery
        </button>
      </div>
      
      <!-- Actions -->
      <div class="actions">
        <button class="secondary-button" @click="recapture">
          Recapture Colors
        </button>
      </div>
    </div>
    
    <LoadingSpinner :show="loading" :message="loadingMessage" />
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

export default {
  name: 'ColorPalettePage',
  components: {
    LoadingSpinner
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    // Reactive data
    const colorChart = ref(null)
    const loading = ref(false)
    const loadingMessage = ref('')
    const selectedEmotion = ref('')
    const selectedProbability = ref(0)
    
    // Page data
    const pageData = ref({})
    const colourData = ref([])
    const rawColors = ref([])
    const emotionPrediction = ref(null)
    const topEmotions = ref([])
    
    // Methods
    const loadPageData = () => {
      try {
        if (route.query.data) {
          const data = JSON.parse(atob(route.query.data))
          pageData.value = data
          colourData.value = data.colourData || []
          rawColors.value = data.rawColors || []
          emotionPrediction.value = data.emotionPrediction
          
          if (emotionPrediction.value && emotionPrediction.value.emotions) {
            // Get top 6 emotions sorted by probability
            const sortedEmotions = Object.entries(emotionPrediction.value.emotions)
              .map(([name, probability]) => ({ name, probability }))
              .sort((a, b) => b.probability - a.probability)
              .slice(0, 6)
            
            topEmotions.value = sortedEmotions
          }
        } else {
          // No data, redirect to home
          router.push('/')
        }
      } catch (error) {
        console.error('Error loading page data:', error)
        router.push('/')
      }
    }
    
    const createColorChart = async () => {
      await nextTick()
      
      if (!colorChart.value || !colourData.value.length) return
      
      const canvas = colorChart.value
      const ctx = canvas.getContext('2d')
      
      // Set canvas size
      canvas.width = 800
      canvas.height = 400
      
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      // Draw color segments
      const totalWidth = canvas.width
      const segmentWidth = totalWidth / colourData.value.length
      
      colourData.value.forEach((colorInfo, index) => {
        const x = index * segmentWidth
        
        // Fill with color
        ctx.fillStyle = colorInfo.hex || colorInfo.color || '#000000'
        ctx.fillRect(x, 0, segmentWidth, canvas.height)
        
        // Add label if space allows
        if (segmentWidth > 60) {
          ctx.fillStyle = '#000000'
          ctx.font = '12px Poppins'
          ctx.textAlign = 'center'
          ctx.fillText(
            colorInfo.name || colorInfo.label || 'Color',
            x + segmentWidth / 2,
            canvas.height - 10
          )
        }
      })
    }
    
    const selectEmotion = (emotionName, probability) => {
      selectedEmotion.value = emotionName
      selectedProbability.value = probability
    }
    
    const proceedToGallery = async () => {
      if (!selectedEmotion.value) return
      
      loading.value = true
      loadingMessage.value = 'Saving your emotion selection...'
      
      try {
        // Save emotion selection to server
        const response = await fetch('/api/save-emotion', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: pageData.value.sessionId,
            palette_filename: pageData.value.filename,
            emotion: selectedEmotion.value,
            probability: selectedProbability.value,
            all_emotions: emotionPrediction.value.emotions
          })
        })
        
        if (!response.ok) {
          throw new Error('Failed to save emotion selection')
        }
        
        // Navigate to gallery with all data
        const galleryData = {
          ...pageData.value,
          selectedEmotion: selectedEmotion.value,
          selectedProbability: selectedProbability.value
        }
        
        router.push({
          name: 'GalleryPage',
          query: { data: btoa(JSON.stringify(galleryData)) }
        })
        
      } catch (error) {
        console.error('Error saving emotion:', error)
        loading.value = false
        // Still proceed to gallery even if saving fails
        const galleryData = {
          ...pageData.value,
          selectedEmotion: selectedEmotion.value,
          selectedProbability: selectedProbability.value
        }
        
        router.push({
          name: 'GalleryPage',
          query: { data: btoa(JSON.stringify(galleryData)) }
        })
      }
    }
    
    const recapture = () => {
      router.push('/gradient')
    }
    
    // Lifecycle
    onMounted(() => {
      loadPageData()
      createColorChart()
    })
    
    return {
      colorChart,
      loading,
      loadingMessage,
      selectedEmotion,
      colourData,
      rawColors,
      emotionPrediction,
      topEmotions,
      selectEmotion,
      proceedToGallery,
      recapture
    }
  }
}
</script>

<style scoped>
.color-palette-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.color-palette-container {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.color-chart-section {
  margin-bottom: 40px;
  text-align: center;
}

.color-chart {
  max-width: 100%;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.raw-colors-section {
  margin-bottom: 40px;
}

.raw-colors-section h3 {
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  color: #333;
  margin-bottom: 15px;
  text-align: center;
}

.raw-colors-bar {
  display: flex;
  height: 60px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.color-segment {
  flex: 1;
  min-width: 20px;
}

.emotion-section {
  text-align: center;
  margin-bottom: 40px;
}

.emotion-section h2 {
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  color: #333;
  margin-bottom: 10px;
  font-size: 28px;
}

.emotion-instruction {
  font-family: 'Poppins', sans-serif;
  color: #666;
  margin-bottom: 30px;
  font-size: 16px;
}

.step-label {
  font-weight: 600;
  color: #4ecdc4;
}

.emotion-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.emotion-card {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.emotion-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  border-color: #4ecdc4;
}

.emotion-card.selected {
  border-color: #4ecdc4;
  background: linear-gradient(135deg, #4ecdc4, #44a08d);
  color: white;
}

.emotion-name {
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  font-size: 18px;
  margin-bottom: 8px;
  text-transform: capitalize;
}

.emotion-probability {
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
  font-size: 16px;
  margin-bottom: 12px;
}

.emotion-bar {
  width: 100%;
  height: 8px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.emotion-card.selected .emotion-bar {
  background: rgba(255, 255, 255, 0.3);
}

.emotion-fill {
  height: 100%;
  background: #4ecdc4;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.emotion-card.selected .emotion-fill {
  background: white;
}

.continue-button {
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
  color: white;
  border: none;
  padding: 15px 40px;
  font-size: 18px;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.continue-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.actions {
  text-align: center;
  padding-top: 20px;
  border-top: 2px solid #f1f3f4;
}

.secondary-button {
  background: #6c757d;
  color: white;
  border: none;
  padding: 12px 30px;
  font-size: 16px;
  font-weight: 500;
  font-family: 'Poppins', sans-serif;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.secondary-button:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

/* Responsive design */
@media (max-width: 768px) {
  .color-palette-container {
    padding: 20px;
    margin: 10px;
  }
  
  .emotion-cards {
    grid-template-columns: 1fr;
  }
  
  .emotion-section h2 {
    font-size: 24px;
  }
  
  .continue-button {
    padding: 12px 30px;
    font-size: 16px;
  }
}
</style> 