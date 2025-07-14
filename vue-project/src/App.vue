<template>
  <div id="app">
    <!-- Homepage Section -->
    <div id="homepage" class="homepage">
      <button id="logo-refresh-btn" class="logo-refresh-button" @click="refreshPage">
        <img src="image/logo.png" alt="Logo" class="logo-image">
      </button>
      <div class="homepage-content">
        <div class="colourbar-container">
          <img src="image/colourbar.png" alt="Colour Bar" class="colourbar-image">
        </div>
        <div class="paintings-container">
          <img src="image/paintings.png" alt="Paintings" class="paintings-image">
        </div>
        <div class="homepage-controls">
          <button id="start-btn" class="start-button" @click="startJourney">Start the journey!</button>
        </div>
      </div>
    </div>

    <!-- Gradient Palette Section -->
    <div id="gradient-container" class="gradient-container" ref="gradientContainer">
      <img 
        id="animated-gif" 
        class="animated-gif-element" 
        :src="currentGif" 
        alt="Animated Palette" 
        :style="{ display: isAnimating ? 'block' : 'none' }"
      >
      <div id="capture-prompt" class="capture-prompt" :class="{ hidden: !showCapturePrompt, animating: promptAnimating }">
        <div class="prompt-text">
          <span class="prompt-step">Step 1:</span> Which palette catches your eye?<br/>Take your time to view and feel...
        </div>
      </div>
      <div class="controls">
        <button 
          id="stop-btn" 
          class="stop-button" 
          @click="captureFrame"
          :disabled="isCapturing"
          :style="{ opacity: showCaptureButton ? '1' : '0', visibility: showCaptureButton ? 'visible' : 'hidden' }"
        >
          {{ isCapturing ? 'Processing...' : 'Capture' }}
        </button>
      </div>

      <!-- Result Modal -->
      <div id="result-modal" class="modal" :class="{ hidden: !showResultModal, visible: showResultModal }">
        <div class="modal-content">
          <h3>Your Palette Created!</h3>
          <p id="result-url">{{ resultUrl }}</p>
          <div class="modal-buttons">
            <button id="copy-btn" class="modal-btn" @click="copyUrl">Copy URL</button>
            <button id="restart-btn" class="modal-btn" @click="restart">Create Another</button>
            <button id="close-modal" class="modal-btn secondary" @click="closeModal">Close</button>
          </div>
        </div>
      </div>

      <!-- Loading Modal -->
      <div id="loading" class="loading" :class="{ hidden: !isLoading, visible: isLoading }">
        <div class="magic-cube-animation"></div>
        <p class="loading-analysis-text">{{ loadingMessage }}</p>
      </div>
    </div>

    <!-- Other Vue Components (Color Palette Page, Gallery, Story Interface) -->
    <ColorPalettePage 
      v-if="showColorPalettePage"
      :colourData="currentColourData"
      :rawColors="currentRawColors"
      :emotionPrediction="currentEmotionPrediction"
      :capturedFilename="currentFilename"
      @continue="handleContinueToGallery"
      @recapture="handleRecapture"
      @emotion-selected="handleEmotionSelected"
    />

    <GalleryPage
      v-if="showGalleryPage"
      :recommendations="currentRecommendations"
      :detailedRecommendations="currentDetailedRecommendations"
      @paintings-selected="handlePaintingsSelected"
      @character-selected="handleCharacterSelected"
      @story-generate="handleStoryGenerate"
    />

    <StoryPage
      v-if="showStoryPage"
      :storyData="currentStory"
      @create-another="handleCreateAnother"
      @recapture="handleRecapture"
      @share="handleShare"
    />

    <!-- Global Loading States -->
    <LoadingModal v-if="globalLoading" :message="globalLoadingMessage" />
    <ValidationMessage v-if="validationMessage" :message="validationMessage" @close="validationMessage = ''" />
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import ColorPalettePage from './views/ColorPalettePage.vue'
import GalleryPage from './views/GalleryPage.vue'
import StoryPage from './views/StoryPage.vue'
import LoadingModal from './components/LoadingModal.vue'
import ValidationMessage from './components/ValidationMessage.vue'

export default {
  name: 'App',
  components: {
    ColorPalettePage,
    GalleryPage,
    StoryPage,
    LoadingModal,
    ValidationMessage
  },
  setup() {
    // Core app state
    const isAnimating = ref(true)
    const isCapturing = ref(false)
    const showCapturePrompt = ref(false)
    const showCaptureButton = ref(false)
    const promptAnimating = ref(false)
    const currentGif = ref('')
    
    // Modal states
    const showResultModal = ref(false)
    const showColorPalettePage = ref(false)
    const showGalleryPage = ref(false)
    const showStoryPage = ref(false)
    const resultUrl = ref('')
    
    // Loading states
    const isLoading = ref(false)
    const loadingMessage = ref('Your palette is being analysed. Please hold on a moment...')
    const globalLoading = ref(false)
    const globalLoadingMessage = ref('')
    const validationMessage = ref('')
    
    // Data states
    const currentFilename = ref('')
    const currentColourData = ref(null)
    const currentRawColors = ref([])
    const currentEmotionPrediction = ref(null)
    const currentRecommendations = ref([])
    const currentDetailedRecommendations = ref([])
    const currentStory = ref(null)
    const selectedEmotion = ref(null)
    const selectedPaintings = ref([])
    const selectedCharacter = ref(null)
    const userName = ref('')
    
    // GIF cycling
    const allGifs = Array.from({length: 50}, (_, i) => `palette GIF/${i + 1}.gif`)
    const currentGifOrder = ref([])
    const currentGifIndex = ref(0)
    let gifCyclingInterval = null
    let capturePromptTimeout = null
    
    // Initialize GIF cycling
    const generateRandomGifOrder = () => {
      currentGifOrder.value = [...allGifs].sort(() => Math.random() - 0.5)
      currentGifIndex.value = 0
    }
    
    const switchToNextGif = () => {
      if (currentGifOrder.value.length === 0) {
        generateRandomGifOrder()
      }
      
      currentGif.value = currentGifOrder.value[currentGifIndex.value]
      currentGifIndex.value = (currentGifIndex.value + 1) % currentGifOrder.value.length
      
      if (currentGifIndex.value === 0) {
        generateRandomGifOrder()
      }
    }
    
    const startGifCycling = () => {
      generateRandomGifOrder()
      switchToNextGif()
      
      gifCyclingInterval = setInterval(() => {
        if (isAnimating.value) {
          switchToNextGif()
        }
      }, 4000)
    }
    
    const stopGifCycling = () => {
      if (gifCyclingInterval) {
        clearInterval(gifCyclingInterval)
        gifCyclingInterval = null
      }
    }
    
    // App lifecycle methods
    const refreshPage = () => {
      window.location.reload()
    }
    
    const startJourney = () => {
      // Enable scrolling
      document.body.classList.remove('no-scroll')
      document.body.classList.add('allow-scroll')
      
      // Scroll to gradient container
      const gradientContainer = document.getElementById('gradient-container')
      if (gradientContainer) {
        gradientContainer.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
      
      // Start animations
      startGifCycling()
      
      // Show capture prompt after delay
      capturePromptTimeout = setTimeout(() => {
        showCapturePrompt.value = true
        promptAnimating.value = true
        showCaptureButton.value = true
      }, 1000)
    }
    
    const captureFrame = async () => {
      if (!isAnimating.value) return
      
      isCapturing.value = true
      showCapturePrompt.value = false
      promptAnimating.value = false
      
      try {
        // Stop GIF cycling and freeze current frame
        stopGifCycling()
        isAnimating.value = false
        
        // Show loading
        isLoading.value = true
        loadingMessage.value = 'Your palette is being analysed. Please hold on a moment...'
        
        // Capture current frame using html2canvas
        const gradientContainer = document.getElementById('gradient-container')
        const canvas = await html2canvas(gradientContainer, {
          width: gradientContainer.offsetWidth,
          height: gradientContainer.offsetHeight,
          scale: 1,
          useCORS: true,
          allowTaint: true,
          backgroundColor: null,
          logging: false,
          foreignObjectRendering: false
        })
        
        // Convert to blob and upload
        const blob = await new Promise(resolve => {
          canvas.toBlob(resolve, 'image/png', 0.9)
        })
        
        const formData = new FormData()
        formData.append('image', blob, 'gradient-palette.png')
        formData.append('colours', JSON.stringify([]))
        
        const response = await fetch('/api/save-palette', {
          method: 'POST',
          body: formData
        })
        
        if (!response.ok) {
          throw new Error(`Server error: ${response.status}`)
        }
        
        const result = await response.json()
        currentFilename.value = result.filename
        
        // Get recommendations
        await getRecommendations(result.filename)
        
      } catch (error) {
        console.error('Capture error:', error)
        validationMessage.value = 'Failed to capture image. Please try again.'
        // Reset states on error
        isAnimating.value = true
        isCapturing.value = false
        startGifCycling()
      }
    }
    
    const getRecommendations = async (filename) => {
      try {
        const response = await fetch('/api/get-recommendations', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ filename })
        })
        
        if (!response.ok) {
          throw new Error(`Failed to get recommendations: ${response.status}`)
        }
        
        const result = await response.json()
        
        currentRecommendations.value = result.recommendations
        currentColourData.value = result.colourData
        currentRawColors.value = result.rawColors || []
        currentDetailedRecommendations.value = result.detailedRecommendations || []
        currentEmotionPrediction.value = result.emotionPrediction
        
        isLoading.value = false
        showColorPalettePage.value = true
        
      } catch (error) {
        console.error('Error getting recommendations:', error)
        isLoading.value = false
        validationMessage.value = 'Failed to get painting recommendations. Please try again.'
      }
    }
    
    // Event handlers
    const handleEmotionSelected = (emotion) => {
      selectedEmotion.value = emotion
      
      // Send emotion to server
      if (currentFilename.value) {
        fetch('/api/save-emotion', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            emotion: emotion.emotion,
            probability: emotion.probability,
            filename: currentFilename.value,
            sessionId: 'vue-session-' + Date.now()
          })
        }).catch(error => console.error('Error saving emotion:', error))
      }
    }
    
    const handleContinueToGallery = () => {
      showColorPalettePage.value = false
      showGalleryPage.value = true
    }
    
    const handlePaintingsSelected = (paintings) => {
      selectedPaintings.value = paintings
    }
    
    const handleCharacterSelected = (character) => {
      selectedCharacter.value = character
    }
    
    const handleStoryGenerate = async (storyRequest) => {
      try {
        globalLoading.value = true
        globalLoadingMessage.value = 'Your story is creating. Please hold on a moment...'
        
        const response = await fetch('/api/generate-story', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            paintings: storyRequest.paintings,
            narrative_style: storyRequest.narrative_style,
            user_name: storyRequest.user_name,
            emotion: selectedEmotion.value?.emotion,
            emotion_probability: selectedEmotion.value?.probability
          })
        })
        
        if (!response.ok) {
          throw new Error(`Story generation failed: ${response.status}`)
        }
        
        const result = await response.json()
        
        if (result.success) {
          currentStory.value = result
          globalLoading.value = false
          showGalleryPage.value = false
          showStoryPage.value = true
        } else {
          throw new Error(result.error)
        }
        
      } catch (error) {
        console.error('Story generation error:', error)
        globalLoading.value = false
        validationMessage.value = 'Failed to generate story. Please try again.'
      }
    }
    
    const handleCreateAnother = () => {
      showStoryPage.value = false
      showGalleryPage.value = true
      // Reset selections but keep paintings
      selectedPaintings.value = []
      selectedCharacter.value = null
      userName.value = ''
    }
    
    const handleRecapture = () => {
      // Reset all states and return to gradient page
      showColorPalettePage.value = false
      showGalleryPage.value = false
      showStoryPage.value = false
      isAnimating.value = true
      isCapturing.value = false
      showCapturePrompt.value = false
      showCaptureButton.value = false
      selectedEmotion.value = null
      selectedPaintings.value = []
      selectedCharacter.value = null
      userName.value = ''
      
      // Restart GIF cycling
      startGifCycling()
      
      // Start capture prompt animation
      setTimeout(() => {
        showCapturePrompt.value = true
        promptAnimating.value = true
        showCaptureButton.value = true
      }, 1000)
    }
    
    const handleShare = () => {
      // Implement share functionality
      validationMessage.value = 'Share functionality coming soon!'
    }
    
    // Modal handlers
    const copyUrl = async () => {
      try {
        await navigator.clipboard.writeText(resultUrl.value)
        validationMessage.value = 'URL copied to clipboard!'
      } catch (error) {
        validationMessage.value = 'Failed to copy URL'
      }
    }
    
    const restart = () => {
      showResultModal.value = false
      handleRecapture()
    }
    
    const closeModal = () => {
      showResultModal.value = false
    }
    
    // Lifecycle
    onMounted(() => {
      // Prevent scrolling initially
      document.body.classList.add('no-scroll')
    })
    
    onUnmounted(() => {
      stopGifCycling()
      if (capturePromptTimeout) {
        clearTimeout(capturePromptTimeout)
      }
    })
    
    return {
      // States
      isAnimating,
      isCapturing,
      showCapturePrompt,
      showCaptureButton,
      promptAnimating,
      currentGif,
      showResultModal,
      showColorPalettePage,
      showGalleryPage,
      showStoryPage,
      resultUrl,
      isLoading,
      loadingMessage,
      globalLoading,
      globalLoadingMessage,
      validationMessage,
      currentFilename,
      currentColourData,
      currentRawColors,
      currentEmotionPrediction,
      currentRecommendations,
      currentDetailedRecommendations,
      currentStory,
      selectedEmotion,
      selectedPaintings,
      selectedCharacter,
      userName,
      
      // Methods
      refreshPage,
      startJourney,
      captureFrame,
      handleEmotionSelected,
      handleContinueToGallery,
      handlePaintingsSelected,
      handleCharacterSelected,
      handleStoryGenerate,
      handleCreateAnother,
      handleRecapture,
      handleShare,
      copyUrl,
      restart,
      closeModal
    }
  }
}
</script>

<style>
/* Import the exact same styles as the main server */
@import url('./assets/styles/main.css');

/* Additional Vue-specific styles if needed */
#app {
  width: 100%;
  height: 100%;
}
</style> 