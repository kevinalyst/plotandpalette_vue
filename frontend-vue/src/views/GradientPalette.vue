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
      :class="['capture-prompt', { 'animate-fade': animatePrompt, 'hidden': !showCapturePrompt }]"
    >
      <div class="prompt-text">
        <div><span class="prompt-step">Step 1:</span> <p>Which palette catches your eye?</p></div>
        <p>Take your time to view and feel...</p>
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
import ApiService from '@/services/api.js'

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
    const animatePrompt = ref(false)
    const isCapturing = ref(false)
    const showModal = ref(false)
    const showLoading = ref(false)
    const loadingMessage = ref('Faster than Van Gogh\'s brush!')
    
    // Modal data
    const modalTitle = ref('')
    const modalMessage = ref('')
    const modalButtons = ref([])
    
    // GIF cycling properties - use palette GIF folder
    const allGifs = []
    
    // Animation properties
    const animationTimeout = ref(null)
    
    // GIF element reference for frame capture
    const animatedGif = ref(null)
    
    // Import GIFs with proper Vite asset handling
    const importGifs = async () => {
      try {
        console.log('📁 Loading GIFs...')
        
        // Method 1: Try dynamic imports
        for (let i = 1; i <= 50; i++) {
          try {
            const gifModule = await import(`@/assets/images/palette GIF/${i}.gif`)
            allGifs.push(gifModule.default || gifModule)
          } catch (error) {
            // Fallback to direct URL construction
            allGifs.push(new URL(`@/assets/images/palette GIF/${i}.gif`, import.meta.url).href)
          }
        }
        
        console.log(`✅ Loaded ${allGifs.length} GIFs successfully`)
        console.log('🔍 First few GIF URLs:', allGifs.slice(0, 3))
      } catch (error) {
        console.error('❌ Error loading GIFs:', error)
        
        // Emergency fallback - use simpler paths
        for (let i = 1; i <= 10; i++) {
          allGifs.push(`/src/assets/images/palette GIF/${i}.gif`)
        }
        console.log('⚠️ Using emergency fallback with 10 GIFs')
      }
    }
    const currentGifOrder = ref([])
    const currentGifIndex = ref(0)
    const gifCyclingInterval = ref(null)
    
    // Methods
    
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
      }, 1000)
    }
    
    const stopGifCycling = () => {
      if (gifCyclingInterval.value) {
        clearInterval(gifCyclingInterval.value)
        gifCyclingInterval.value = null
      }
      stopCapturePromptAnimation()
    }
    
    const startCapturePromptAnimation = () => {
      // Start the animation after 2 seconds
      animationTimeout.value = setTimeout(() => {
        animatePrompt.value = true
      }, 2000)
    }
    
    const stopCapturePromptAnimation = () => {
      if (animationTimeout.value) {
        clearTimeout(animationTimeout.value)
        animationTimeout.value = null
      }
      animatePrompt.value = false
    }
    
    const captureCurrentFrame = () => {
      return new Promise((resolve, reject) => {
        try {
          const gifElement = animatedGif.value
          if (!gifElement) {
            reject(new Error('GIF element not found'))
            return
          }
          
          // Create a canvas to capture the current frame
          const canvas = document.createElement('canvas')
          const ctx = canvas.getContext('2d')
          
          // Set canvas size to match the GIF
          canvas.width = gifElement.naturalWidth || gifElement.width || 600
          canvas.height = gifElement.naturalHeight || gifElement.height || 400
          
          // Draw the current frame to canvas
          ctx.drawImage(gifElement, 0, 0, canvas.width, canvas.height)
          
          // Convert to base64 data URL
          const frameData = canvas.toDataURL('image/png', 0.95)
          
          console.log('🖼️ Frame captured:', {
            width: canvas.width,
            height: canvas.height,
            dataLength: frameData.length
          })
          
          resolve(frameData)
        } catch (error) {
          console.error('❌ Error capturing frame:', error)
          reject(error)
        }
      })
    }
    
    const capturePalette = async () => {
      console.log('🎯 Capture button clicked')
      
      if (isCapturing.value) {
        console.log('⏳ Already capturing, ignoring click')
        return
      }
      
      console.log('🚀 Starting palette capture...')
      isCapturing.value = true
      showCapturePrompt.value = false
      showLoading.value = true
      
      // Stop GIF cycling and freeze at current frame
      stopGifCycling()
      
      try {
        // Create new session ID when capture is clicked
        console.log('🆕 Creating new session for capture...')
        const username = localStorage.getItem('username')
        
        const sessionResponse = await ApiService.request('/create-session', {
          method: 'POST',
          body: JSON.stringify({ 
            username: username
          })
        })
        
        const sessionId = sessionResponse.sessionId
        console.log('✅ New session created:', sessionId)
        
        // Store the new session ID
        localStorage.setItem('sessionId', sessionId)
        
        // Helper function for Unicode-safe base64 encoding
        const unicodeSafeBase64Encode = (str) => {
          try {
            // First encode the string as UTF-8, then encode to base64
            return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g, (match, p1) => {
              return String.fromCharCode('0x' + p1)
            }))
          } catch (error) {
            console.error('Error encoding string:', error)
            // Fallback: remove problematic characters and try again
            // eslint-disable-next-line no-control-regex
            const cleanStr = str.replace(/[^\u0000-\u007F]/g, "")
            return btoa(cleanStr)
          }
        }

        const currentGifSrc = allGifs[currentGifIndex.value] || '1.gif'
        console.log('📷 Capturing current frame...')
        
        const capturedFrame = await captureCurrentFrame()
        console.log('📡 Sending capture request to backend...')
        
        const response = await ApiService.request('/capture-palette', {
          method: 'POST',
          body: JSON.stringify({
            gifName: currentGifSrc,
            frameData: capturedFrame,
            sessionId: sessionId
          })
        })
        
        console.log('✅ Palette captured successfully:', response)
        
        // Navigate to color palette page with the response data
        router.push({
          name: 'ColorPalettePage',
          query: { data: unicodeSafeBase64Encode(JSON.stringify(response)) }
        })
        
      } catch (error) {
        console.error('❌ Error in palette capture:', error)
        showLoading.value = false
        isCapturing.value = false
        showModal.value = true
        modalTitle.value = 'Capture Failed'
        modalMessage.value = `Failed to capture palette: ${error.message}`
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
    onMounted(async () => {
      console.log('🎬 GradientPalette mounted')
      await importGifs()
      
      // Wait a bit for GIFs to load before starting cycling
      setTimeout(startGifCycling, 100)
    })
    
    onBeforeUnmount(() => {
      stopGifCycling()
    })
    
    return {
      currentGifSrc,
      gifVisible,
      showCapturePrompt,
      animatePrompt,
      isCapturing,
      showModal,
      showLoading,
      loadingMessage,
      modalTitle,
      modalMessage,
      modalButtons,
      animatedGif,
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
  font-family: 'Poppins',regular;
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
  top: 15%;
  left: 50%;
  transform: translate(-50%, -50%);
  
  color: white;
  padding: 20px 30px;
  border-radius: 12px;
  text-align: center;
  z-index: 10;
  max-width: 400px;
  backdrop-filter: blur(10px);
}

.capture-prompt.hidden {
  display: none;
}

.prompt-text {
  display: flex;
  flex-direction: column;
  align-items: left;
  justify-content: start;
  font-family: 'Poppins', sans-serif;
  font-size: 18px;
  line-height: 1.6;
  font-weight: 400;
}

.prompt-step {
  font-weight: 600;
  
}

.controls {
  position: absolute;
  bottom: 50px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.stop-button {
  background: rgba(232, 232, 224, 0.15);
  color: #2C2C2C;
  border: 2px solid #C0C0B8;
  padding: 15px 40px;
  font-size: 18px;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stop-button:hover:not(:disabled) {
  background: #DDD9D1;
  border-color: #B0B0A8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stop-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  background: #F0F0E8;
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

/* Capture prompt fade animation */
.capture-prompt.animate-fade {
  animation: capturePromptFade 9s infinite;
}

@keyframes capturePromptFade {
  0% {
    opacity: 0;
  }
  15% {
    opacity: 1;
  }
  30% {
    opacity: 1;
  }
  45% {
    opacity: 1;
  }
  60% {
    opacity: 1;
  }
  75% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}

/* Global button focus disable */
button:focus {
  outline: none !important;
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