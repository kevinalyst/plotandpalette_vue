<template>
  <div class="gradient-container">
    <img 
      ref="animatedGif"
      :src="currentGifSrc" 
      class="animated-gif-element" 
      :style="{ display: gifVisible ? 'block' : 'none' }"
      alt="Animated Palette"
    />
    
    <div 
      :class="['capture-prompt', { 'hidden': !showCapturePrompt }]"
    >
      <div class="prompt-text">
        <span class="prompt-step">Step 1:</span> Which palette catches your eye?<br/>
        Take your time to view and feel...
      </div>
    </div>
    
    <div class="controls">
      <button 
        class="stop-button" 
        @click="capturePalette"
        :disabled="isCapturing"
      >
        {{ isCapturing ? 'Capturing...' : 'Capture' }}
      </button>
    </div>
    
    <Modal
      :show="showModal"
      :title="modalTitle"
      :message="modalMessage"
      :buttons="modalButtons"
    />
    
    <LoadingSpinner
      :show="showLoading"
      :message="loadingMessage"
    />
  </div>
</template>

<script>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import Modal from '@/components/Modal.vue'

export default {
  name: 'GradientPalette',
  components: {
    LoadingSpinner,
    Modal
  },
  setup() {
    const router = useRouter()
    
    // Reactive data
    const currentGifSrc = ref('')
    const gifVisible = ref(false)
    const showCapturePrompt = ref(false)
    const isCapturing = ref(false)
    const showModal = ref(false)
    const showLoading = ref(false)
    const loadingMessage = ref('Your palette is being analysed. Please hold on a moment...')
    
    // Modal data
    const modalTitle = ref('')
    const modalMessage = ref('')
    const modalButtons = ref([])
    
    // GIF cycling properties - use palette GIF folder
    const allGifs = Array.from({length: 50}, (_, i) => require(`@/assets/images/palette GIF/${i + 1}.gif`))
    const currentGifOrder = ref([])
    const currentGifIndex = ref(0)
    const gifCyclingInterval = ref(null)
    const promptAnimationInterval = ref(null)
    
    // Session data
    const sessionId = ref('')
    
    // Methods
    const generateSessionId = () => {
      return Date.now() + '-' + Math.random().toString(36).substr(2, 9)
    }
    
    const generateRandomGifOrder = () => {
      const shuffled = [...allGifs].sort(() => Math.random() - 0.5)
      currentGifOrder.value = shuffled
      currentGifIndex.value = 0
    }
    
    const switchToNextGif = () => {
      if (currentGifOrder.value.length === 0) {
        generateRandomGifOrder()
      }
      
      currentGifSrc.value = currentGifOrder.value[currentGifIndex.value]
      currentGifIndex.value = (currentGifIndex.value + 1) % currentGifOrder.value.length
      
      if (currentGifIndex.value === 0) {
        generateRandomGifOrder()
      }
    }
    
    const startGifCycling = () => {
      generateRandomGifOrder()
      switchToNextGif()
      gifVisible.value = true
      
      // Start cycling
      gifCyclingInterval.value = setInterval(() => {
        switchToNextGif()
      }, 3000) // Change every 3 seconds
      
      // Show capture prompt after delay
      setTimeout(() => {
        showCapturePrompt.value = true
        startCapturePromptAnimation()
      }, 2000)
    }
    
    const stopGifCycling = () => {
      if (gifCyclingInterval.value) {
        clearInterval(gifCyclingInterval.value)
        gifCyclingInterval.value = null
      }
      stopCapturePromptAnimation()
    }
    
    const startCapturePromptAnimation = () => {
      const promptElement = document.querySelector('.capture-prompt')
      if (promptElement) {
        promptAnimationInterval.value = setInterval(() => {
          promptElement.style.animation = 'none'
          setTimeout(() => {
            promptElement.style.animation = 'pulse 2s ease-in-out infinite'
          }, 10)
        }, 4000)
      }
    }
    
    const stopCapturePromptAnimation = () => {
      if (promptAnimationInterval.value) {
        clearInterval(promptAnimationInterval.value)
        promptAnimationInterval.value = null
      }
    }
    
    const capturePalette = async () => {
      if (isCapturing.value) return
      
      isCapturing.value = true
      showCapturePrompt.value = false
      showLoading.value = true
      stopGifCycling()
      
      try {
        // Create canvas from current GIF
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')
        const img = new Image()
        
        await new Promise((resolve, reject) => {
          img.onload = () => {
            canvas.width = img.width
            canvas.height = img.height
            ctx.drawImage(img, 0, 0)
            resolve()
          }
          img.onerror = reject
          img.src = currentGifSrc.value
        })
        
        // Convert canvas to blob
        const blob = await new Promise((resolve) => {
          canvas.toBlob(resolve, 'image/png', 0.9)
        })
        
        // Upload to server (following original flow)
        const formData = new FormData()
        formData.append('image', blob, 'palette-capture.png')
        formData.append('colours', JSON.stringify([]))
        
        const uploadResponse = await fetch('/api/save-palette', {
          method: 'POST',
          body: formData
        })
        
        if (!uploadResponse.ok) {
          throw new Error('Failed to upload palette')
        }
        
        const uploadResult = await uploadResponse.json()
        const filename = uploadResult.filename
        
        // Get recommendations with emotion analysis
        const recResponse = await fetch('/api/get-recommendations', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            filename: filename,
            session_id: sessionId.value
          })
        })
        
        if (!recResponse.ok) {
          throw new Error('Failed to get recommendations')
        }
        
        const result = await recResponse.json()
        
        // Store data for next page
        const pageData = {
          filename: filename,
          colourData: result.colourData,
          rawColors: result.rawColors,
          emotionPrediction: result.emotionPrediction,
          recommendations: result.recommendations,
          sessionId: sessionId.value
        }
        
        // Navigate to color palette page with data
        router.push({
          name: 'ColorPalettePage',
          query: { data: btoa(JSON.stringify(pageData)) }
        })
        
      } catch (error) {
        console.error('Error capturing palette:', error)
        showLoading.value = false
        showModal.value = true
        modalTitle.value = 'Error'
        modalMessage.value = 'Failed to analyze palette. Please try again.'
        modalButtons.value = [
          {
            text: 'Try Again',
            action: () => {
              showModal.value = false
              isCapturing.value = false
              showCapturePrompt.value = true
              startGifCycling()
            }
          }
        ]
      }
    }
    
    // Lifecycle
    onMounted(() => {
      sessionId.value = generateSessionId()
      startGifCycling()
    })
    
    onBeforeUnmount(() => {
      stopGifCycling()
    })
    
    return {
      currentGifSrc,
      gifVisible,
      showCapturePrompt,
      isCapturing,
      showModal,
      showLoading,
      loadingMessage,
      modalTitle,
      modalMessage,
      modalButtons,
      capturePalette
    }
  }
}
</script>

<style scoped>
.gradient-container {
  position: relative;
  width: 100vw;
  height: 100vh;
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.animated-gif-element {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 1;
}

.capture-prompt {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 20px 30px;
  border-radius: 12px;
  text-align: center;
  z-index: 10;
  animation: pulse 2s ease-in-out infinite;
  max-width: 400px;
  backdrop-filter: blur(10px);
}

.capture-prompt.hidden {
  display: none;
}

.prompt-text {
  font-family: 'Poppins', sans-serif;
  font-size: 18px;
  line-height: 1.6;
}

.prompt-step {
  font-weight: 600;
  color: #4ecdc4;
}

.controls {
  position: absolute;
  bottom: 50px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.stop-button {
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
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.stop-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
  background: linear-gradient(45deg, #ff5252, #26a69a);
}

.stop-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.8;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1.05);
  }
}

/* Responsive design */
@media (max-width: 768px) {
  .capture-prompt {
    max-width: 300px;
    padding: 15px 20px;
  }
  
  .prompt-text {
    font-size: 16px;
  }
  
  .stop-button {
    padding: 12px 30px;
    font-size: 16px;
  }
  
  .controls {
    bottom: 30px;
  }
}
</style> 