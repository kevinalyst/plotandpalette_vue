<template>
  <div class="color-palette-page">
    <div class="gallery-container">
      <h1 class="gallery-title">{{ $t('colorPalette.title') }}</h1>
      <p class="gallery-subtitle">{{ $t('colorPalette.subtitle') }}</p>
      
      <!-- Show loading state initially -->
      <div v-if="loading" style="text-align: center; padding: 40px; color: white;">
        <p>{{ $t('colorPalette.loadingAnalysis') }}</p>
      </div>
      
      <!-- Palette Analysis Container -->
      <div class="palette-analysis-container">
        <!-- Captured Image Section -->
        <div class="captured-image-section">
          <h3 class="captured-image-title">{{ $t('colorPalette.capturedPalette') }}</h3>
          <div v-if="!capturedImageUrl" class="no-colors-message">
            <p>{{ $t('colorPalette.loadingImage') }}</p>
          </div>
          <img 
            v-else
            :src="capturedImageUrl" 
            class="captured-palette-image" 
            alt="Your captured gradient palette"
            @error="handleImageError"
            @load="handleImageLoad"
          />
        </div>
        
        <!-- Spacing -->
        <div style="height: 40px;"></div>
        
        <!-- Raw Colors Section -->
        <div class="raw-colors-section">
          <h3 class="raw-colors-title">{{ $t('colorPalette.colorsExtracted') }}</h3>
          <div class="chart-container">
            <div v-if="rawColors && rawColors.length > 0" class="color-bar raw-color-bar">
              <div 
                v-for="(color, index) in rawColors" 
                :key="index"
                class="color-segment"
                :style="{ 
                  backgroundColor: getColorFromRawColor(color),
                  width: `${getRawColorPercentage(color) * 100}%`
                }"
                :title="`Color ${index + 1}: ${getColorFromRawColor(color)} (${Math.round(getRawColorPercentage(color) * 100)}%)`"
              ></div>
            </div>
            <div v-else class="no-colors-message">
              <p>{{ $t('colorPalette.noColorsData') }}</p>
            </div>
          </div>
        </div>
        <!-- Spacing -->
        <div style="height: 40px;"></div>
        </div>
        
      
      <!-- Emotion Selection Section -->
      <div v-if="emotionPrediction && showEmotionSelection" class="emotion-container">
        <div class="emotion-title-section">
          <div class="emotion-step-title">{{ $t('colorPalette.step2Label') }}</div>
          <div class="emotion-main-title">{{ $t('colorPalette.emotionQuestion') }}</div>
          <div class="emotion-main-title">{{ $t('colorPalette.emotionInstruction') }}</div>
        </div>
        
        <div class="emotion-cards-container">
          <div 
            v-for="emotion in displayedEmotions" 
            :key="emotion.name"
            :class="['emotion-card', { 'emotion-card-selected': selectedEmotion === emotion.name }]"
            @click="selectEmotion(emotion.name, emotion.intensity)"
          >
            <div class="emotion-card-name">{{ emotion.name }}</div>
            <div class="emotion-card-image-container">
              <img 
                v-if="getEmotionImageSrc(emotion.name)"
                :src="getEmotionImageSrc(emotion.name)"
                :alt="emotion.name"
                class="emotion-card-image"
              />
              <div 
                v-else
                class="emotion-card-placeholder"
                :style="{ 
                  background: `linear-gradient(135deg, ${getEmotionColor(emotion.name)}, ${getEmotionColor(emotion.name)}88)`
                }"
              >
                {{ emotion.name }}
              </div>
            </div>
            <div class="emotion-card-stars">
              <span 
                v-for="star in 3" 
                :key="star"
                class="star"
                :class="{ 'star-filled': star <= getIntensityStars(emotion.intensity) }"
              >
                ★
              </span>
            </div>
            <div class="emotion-card-intensity-label">{{ emotion.intensity }} {{ $t('colorPalette.intensitySuffix') }}</div>
          </div>
        </div>
        
        <button 
          class="more-feelings-btn"
          @click="shuffleEmotions"
          :disabled="emotionResetCount >= 3"
          :class="{ 'disabled': emotionResetCount >= 3 }"
        >
          <span>{{ $t('colorPalette.moreEmotions') }}</span>
          <span :class="['reload-counter', { zero: remainingReloads === 0 }]">{{ remainingReloads }}/3</span>
        </button>
        
        <!-- Emotion Explanation -->
        <div class="emotion-explanation">
          <h4>{{ $t('colorPalette.emotionExplanationTitle') }}</h4>
          <p>{{ $t('colorPalette.emotionExplanationText') }}</p>
        </div>
      </div>
      
      <!-- Actions -->
      <div class="color-palette-controls">
        <button class="btn-primary" @click="recapture">{{ $t('colorPalette.recapture') }}</button>
        <button 
          :class="['btn-secondary', { 'disabled': !selectedEmotion }]"
          :disabled="!selectedEmotion"
          @click="proceedToGallery"
        >
          {{ selectedEmotion ? $t('colorPalette.continue') : $t('colorPalette.chooseEmotion') }}
        </button>
      </div>
    </div>
    
    <LoadingSpinner :show="loading" :message="loadingMessage" :type="spinnerType" />
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ApiService from '@/services/api.js'

// Static imports for emotion card images - ensures they're included in build
import angerImg from '@/assets/images/emotion_cards/anger.jpg'
import anticipationImg from '@/assets/images/emotion_cards/anticipation.jpg'
import arroganceImg from '@/assets/images/emotion_cards/arrogance.jpg'
import disagreeablenessImg from '@/assets/images/emotion_cards/disagreeableness.jpg'
import disgustImg from '@/assets/images/emotion_cards/disgust.jpg'
import fearImg from '@/assets/images/emotion_cards/fear.jpg'
import gratitudeImg from '@/assets/images/emotion_cards/gratitude.jpg'
import happinessImg from '@/assets/images/emotion_cards/happiness.jpg'
import humilityImg from '@/assets/images/emotion_cards/humility.jpg'
import loveImg from '@/assets/images/emotion_cards/love.jpg'
import optimismImg from '@/assets/images/emotion_cards/optimism.jpg'
import pessimismImg from '@/assets/images/emotion_cards/pessimism.jpg'
import sadnessImg from '@/assets/images/emotion_cards/sadness.jpg'
import surpriseImg from '@/assets/images/emotion_cards/surprise.jpg'
import trustImg from '@/assets/images/emotion_cards/trust.jpg'

export default {
  name: 'ColorPalettePage',
  components: {
    LoadingSpinner
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    // Reactive data
    const loading = ref(false)
    const loadingMessage = ref('')
    const spinnerType = ref('magic-cube')
    const selectedEmotion = ref('')
    const selectedIntensity = ref('')
    const emotionResetCount = ref(0)
    const remainingReloads = ref(3)
    const showEmotionSelection = ref(false)
    
    // Helper function for Unicode-safe base64 decoding
    const unicodeSafeBase64Decode = (str) => {
      try {
        // Decode from base64, then decode from UTF-8
        return decodeURIComponent(atob(str).split('').map(function(c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
        }).join(''))
      } catch (error) {
        console.error('Error decoding string:', error)
        // Fallback to regular atob
        return atob(str)
      }
    }

    // Page data
    const pageData = ref({})
    const colourData = ref([])
    const rawColors = ref([])
    const emotionPrediction = ref(null)
    const topEmotions = ref([])
    const displayedEmotions = ref([])
    const capturedImageUrl = ref('')
    const imageFallbackUrls = ref([])
    
    // Methods
    const loadPageData = async () => {
      try {
        console.log('🔍 Loading page data...')
        console.log('📊 Route query:', route.query)
        console.log('🌐 Current origin:', window.location.origin)
        console.log('📍 Current pathname:', window.location.pathname)
        
        let data = null
        
        // First try: Get data from route query (navigation from previous page)
        if (route.query.data) {
          try {
            console.log('📦 Raw query data length:', route.query.data.length)
            data = JSON.parse(unicodeSafeBase64Decode(route.query.data))
            console.log('✅ Successfully loaded data from route query')
          } catch (error) {
            console.error('❌ Failed to parse route query data:', error)
          }
        }
        
        // Second try: Get data from backend API using session ID
        if (!data) {
          console.log('🔄 No route data found, fetching from backend API...')
          
          const sessionId = localStorage.getItem('sessionId')
          if (!sessionId) {
            console.error('❌ No session ID found in localStorage')
            router.push('/')
            return
          }
          
          console.log('📡 Fetching palette data for session:', sessionId)
          
          // Show loading state while fetching from API
          loading.value = true
          loadingMessage.value = 'Loading your palette analysis...'
          
          try {
            const response = await ApiService.getSessionPalette(sessionId)
            
            if (response.success) {
              data = response
              console.log('✅ Successfully loaded data from backend API')
            } else {
              console.error('❌ Backend API returned error:', response.error)
              router.push('/')
              return
            }
          } catch (error) {
            console.error('❌ Failed to fetch data from backend API:', error)
            router.push('/')
            return
          } finally {
            // Hide loading state
            loading.value = false
          }
        }
        
        // Process the data (same logic for both sources)
        if (!data) {
          console.error('❌ No data available from any source')
          router.push('/')
          return
        }
        
        console.log('📦 Final data to process:', data)
        console.log('📊 Data keys:', Object.keys(data))
        console.log('🎨 Raw colourData:', data.colourData)
        console.log('🌈 Raw rawColors:', data.rawColors)
        console.log('📁 Filename:', data.filename)
        
        pageData.value = data
        colourData.value = data.colourData || []
        
        // Process raw colors to handle different formats
        const processedRawColors = processRawColors(data.rawColors)
        rawColors.value = processedRawColors
        
        // Process colour data for display
        if (data.colourData && typeof data.colourData === 'object') {
          const processedColourData = Object.entries(data.colourData)
            .filter(([name, percentage]) => percentage > 0)
            .map(([name, percentage]) => ({
              name: name,
              percentage: percentage,
              hex: getBasicColorHex(name),
              color: getBasicColorHex(name)
            }))
            .sort((a, b) => b.percentage - a.percentage)
          
          colourData.value = processedColourData
        }
        
        emotionPrediction.value = data.emotionPrediction
        
        // Set up captured image URL with better error handling
        if (data.filename) {
          // Try multiple URL formats (prefer public assets path)
          const cacheBuster = Date.now()
          const possibleUrls = [
            // Public assets endpoint (no auth required)
            `/api/assets/${data.filename}?v=${cacheBuster}`,
            // Direct paths served by frontend (if proxy not used)
            `/uploads/${data.filename}?v=${cacheBuster}`,
            `./uploads/${data.filename}?v=${cacheBuster}`,
            `${window.location.origin}/uploads/${data.filename}?v=${cacheBuster}`,
            // Production/static fallbacks
            `/static/uploads/${data.filename}?v=${cacheBuster}`,
            `./static/uploads/${data.filename}?v=${cacheBuster}`,
            `${window.location.origin}/static/uploads/${data.filename}?v=${cacheBuster}`,
            data.capturedImageUrl // any direct URL provided by backend
          ].filter(Boolean)
          
          // Try the first URL and keep fallbacks for retry on error
          capturedImageUrl.value = possibleUrls[0]
          imageFallbackUrls.value = possibleUrls.slice(1)
          console.log('🖼️ Setting captured image URL:', capturedImageUrl.value)
          console.log('🔄 Available alternative URLs:', imageFallbackUrls.value)
        } else {
          console.warn('⚠️ No filename provided in data')
        }
        
        console.log('🎨 colourData:', colourData.value)
        console.log('🌈 rawColors (original):', data.rawColors)
        console.log('🌈 rawColors (processed):', rawColors.value)
        console.log('😊 emotionPrediction:', emotionPrediction.value)
        console.log('🖼️ capturedImageUrl:', capturedImageUrl.value)
        
        // Validate raw colors data
        if (!rawColors.value || rawColors.value.length === 0) {
          console.warn('⚠️ No raw colors data available')
        } else {
          console.log('✅ Raw colors data loaded successfully')
        }
        
        if (emotionPrediction.value && emotionPrediction.value.all_intensities) {
          // Get all emotions sorted by intensity (high > medium > low)
          const intensityOrder = { 'high': 3, 'medium': 2, 'low': 1 };
          const sortedEmotions = Object.entries(emotionPrediction.value.all_intensities)
            .map(([name, intensity]) => ({ name, intensity }))
            .sort((a, b) => (intensityOrder[b.intensity] || 0) - (intensityOrder[a.intensity] || 0))
          
          topEmotions.value = sortedEmotions
          
          // Select initial 3 emotions from different categories
          displayedEmotions.value = selectRandomEmotions(sortedEmotions)
          
          // Show emotion selection after a brief delay to show color analysis first
          setTimeout(() => {
            showEmotionSelection.value = true
          }, 1500)
          
          console.log('🎭 Emotion data processed:', {
            totalEmotions: sortedEmotions.length,
            topEmotion: sortedEmotions[0],
            displayedEmotions: displayedEmotions.value
          })
        } else {
          console.warn('❌ No emotion prediction data found:', emotionPrediction.value)
        }
        
      } catch (error) {
        console.error('❌ Error loading page data:', error)
        router.push('/')
      }
    }
    
    const selectEmotion = (emotionName, intensity) => {
      selectedEmotion.value = emotionName
      selectedIntensity.value = intensity
    }
    
    const proceedToGallery = async () => {
      if (!selectedEmotion.value) return
      
      console.log('🚀 Proceeding to gallery with emotion:', selectedEmotion.value)
      
      loading.value = true
      loadingMessage.value = 'Unlike Mondrian, we love curves...'
      spinnerType.value = 'keyboard'
      
      try {
        // Save emotion selection to backend
        const sessionId = localStorage.getItem('sessionId')
        await ApiService.saveEmotion({
          emotion: selectedEmotion.value,
          intensity: selectedIntensity.value,
          sessionId: sessionId
        })
        
        console.log('✅ Emotion saved successfully')
        
        // Wait 1 second before polling for recommendations
        loadingMessage.value = 'Curating your paintings...'
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Poll for painting recommendations (max 10 attempts, 1 second apart)
        loadingMessage.value = 'Preparing your gallery...'
        let recommendations = null
        const maxAttempts = 10
        
        for (let attempt = 1; attempt <= maxAttempts; attempt++) {
          console.log(`📡 Polling for recommendations (attempt ${attempt}/${maxAttempts})...`)
          
          try {
            const response = await ApiService.request(`/recommendations/${sessionId}`)
            
            if (response.success && response.data && response.data.recommendations) {
              recommendations = response.data.recommendations
              console.log('✅ Recommendations received:', recommendations.length, 'paintings')
              break
            } else {
              console.log('⏳ Recommendations not ready yet, retrying...')
            }
          } catch (error) {
            console.warn(`⚠️  Attempt ${attempt} failed:`, error.message)
          }
          
          // Wait 1 second before next attempt (unless it's the last attempt)
          if (attempt < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 1000))
          }
        }
        
        // Prepare gallery data with selected emotion and recommendations
        const galleryData = {
          ...pageData.value,
          selectedEmotion: selectedEmotion.value,
          selectedIntensity: selectedIntensity.value,
          sessionId: sessionId
        }
        
        // Add recommendations if available
        if (recommendations && recommendations.length > 0) {
          galleryData.detailedRecommendations = recommendations
          console.log('✅ Added', recommendations.length, 'recommendations to gallery data')
        } else {
          console.warn('⚠️  No recommendations received after polling, GalleryPage will fallback to database fetch')
        }
        
        console.log('📦 Gallery data prepared:', galleryData)
        console.log('📦 Emotion data debug:', {
          selectedEmotion: selectedEmotion.value,
          selectedIntensity: selectedIntensity.value,
          emotionType: typeof selectedEmotion.value,
          intensityType: typeof selectedIntensity.value,
          hasRecommendations: !!galleryData.detailedRecommendations
        })
        
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
        
        // Navigate to gallery page
        router.push({
          name: 'GalleryPage',
          query: { data: unicodeSafeBase64Encode(JSON.stringify(galleryData)) }
        })
        
        console.log('✅ Navigation to gallery completed')
        
      } catch (error) {
        console.error('❌ Error saving emotion or navigating:', error)
        loading.value = false
        spinnerType.value = 'magic-cube'
        alert('Failed to save emotion. Please try again.')
      }
    }
    
    const recapture = () => {
      router.push('/gradient')
    }
    
    const selectRandomEmotions = (allEmotions) => {
      // Define emotion categories (simplified version)
      const emotionCategories = {
        negative: ['anger', 'disgust', 'fear', 'sadness'],
        neutral: ['surprise', 'anticipation'],
        positive: ['happiness', 'trust', 'gratitude', 'love', 'optimism']
      }
      
      const selected = []
      const categories = ['negative', 'neutral', 'positive']
      
      categories.forEach(category => {
        const categoryEmotions = allEmotions.filter(emotion => 
          emotionCategories[category].includes(emotion.name.toLowerCase())
        )
        
        if (categoryEmotions.length > 0) {
          const randomIndex = Math.floor(Math.random() * categoryEmotions.length)
          selected.push(categoryEmotions[randomIndex])
        }
      })
      
      // If we don't have 3 emotions, fill with top emotions
      while (selected.length < 3 && selected.length < allEmotions.length) {
        const remaining = allEmotions.filter(emotion => 
          !selected.some(s => s.name === emotion.name)
        )
        if (remaining.length > 0) {
          selected.push(remaining[0])
        }
      }
      
      return selected.slice(0, 3)
    }
    
    const shuffleEmotions = () => {
      if (emotionResetCount.value < 3) {
        emotionResetCount.value++
        remainingReloads.value = Math.max(0, 3 - emotionResetCount.value)
        displayedEmotions.value = selectRandomEmotions(topEmotions.value)
        
        // Reset selection when shuffling
        selectedEmotion.value = ''
        selectedIntensity.value = ''
      }
    }
    
    const getIntensityStars = (intensity) => {
      const starMap = {
        'high': 3,
        'medium': 2,
        'low': 1
      }
      return starMap[intensity] || 0
    }
    
    const getEmotionColor = (emotionName) => {
      const emotionColors = {
        anger: '#ff4757',
        disgust: '#5f27cd',
        fear: '#2f3542',
        sadness: '#3742fa',
        surprise: '#ff9ff3',
        happiness: '#ffa502',
        trust: '#2ed573',
        anticipation: '#ff6b6b',
        gratitude: '#ff7675',
        love: '#fd79a8',
        optimism: '#fdcb6e',
        arrogance: '#6c5ce7',
        pessimism: '#636e72',
        humility: '#00b894',
        disagreeableness: '#e84393'
      }
      return emotionColors[emotionName.toLowerCase()] || '#ffffff'
    }
    
    const getBasicColorHex = (colorName) => {
      const basicColorMap = {
        'black': '#000000',
        'blue': '#0066cc',
        'brown': '#8b4513',
        'green': '#008000',
        'grey': '#808080',
        'orange': '#ff8800',
        'pink': '#ff69b4', 
        'purple': '#800080',
        'red': '#ff0000',
        'turquoise': '#40e0d0',
        'white': '#ffffff',
        'yellow': '#ffff00'
      }
      return basicColorMap[colorName.toLowerCase()] || '#cccccc'
    }
    
    const processRawColors = (rawColorsData) => {
      console.log('🎨 Processing raw colors:', rawColorsData)
      
      // Handle new dictionary format: {'#8b54b5': 0.1027, '#ffc0cb': 0.2515, ...}
      if (rawColorsData && typeof rawColorsData === 'object' && !Array.isArray(rawColorsData)) {
        console.log('✅ New dictionary format detected')
        const processed = Object.entries(rawColorsData).map(([hexColor, percentage]) => {
          const cleanHex = hexColor.startsWith('#') ? hexColor : `#${hexColor}`
          console.log(`✅ Dictionary format: ${cleanHex} -> ${(percentage * 100).toFixed(2)}%`)
          return {
            hex: cleanHex,
            percentage: percentage
          }
        })
        console.log('🎨 Final processed colors (dictionary):', processed)
        console.log('📊 Color percentages:', processed.map(c => `${c.hex}: ${(c.percentage * 100).toFixed(2)}%`))
        return processed
      }
      
      // Legacy array format handling for backwards compatibility
      if (!rawColorsData || !Array.isArray(rawColorsData)) {
        console.log('❌ No valid raw colors data')
        return []
      }
      
      if (rawColorsData.length === 0) {
        console.log('⚠️ Raw colors array is empty!')
        return []
      }
      
      // Helper function to convert RGB to hex
      const rgbToHex = (r, g, b) => {
        const toHex = (c) => {
          const hex = Math.round(Math.max(0, Math.min(255, c))).toString(16)
          return hex.length === 1 ? '0' + hex : hex
        }
        return `#${toHex(r)}${toHex(g)}${toHex(b)}`
      }
      
      const processed = rawColorsData.map((color, index) => {
        console.log(`🔍 Processing color ${index + 1}:`, color)
        
        // Handle different color formats
        if (typeof color === 'string') {
          // Already a hex string
          const hexColor = color.startsWith('#') ? color : `#${color}`
          console.log(`✅ String format -> ${hexColor}`)
          return {
            hex: hexColor,
            percentage: 1.0 / rawColorsData.length // Equal distribution for strings
          }
        } else if (color && typeof color === 'object') {
          
          // RGB format like {r: 235, g: 164, b: 253, percentage: 0.187}
          if (typeof color.r === 'number' && typeof color.g === 'number' && typeof color.b === 'number') {
            const hexColor = rgbToHex(color.r, color.g, color.b)
            const percentage = typeof color.percentage === 'number' ? color.percentage : 1.0 / rawColorsData.length
            console.log(`✅ RGB format {r: ${color.r}, g: ${color.g}, b: ${color.b}} -> ${hexColor} (${(percentage * 100).toFixed(2)}%)`)
            return {
              hex: hexColor,
              percentage: percentage
            }
          }
          
          // Hex object format like {hex: '#ff0000', percentage: 0.25}
          else if (color.hex) {
            const hexColor = color.hex.startsWith('#') ? color.hex : `#${color.hex}`
            const percentage = typeof color.percentage === 'number' ? color.percentage : 1.0 / rawColorsData.length
            console.log(`✅ Hex object format -> ${hexColor} (${(percentage * 100).toFixed(2)}%)`)
            return {
              hex: hexColor,
              percentage: percentage
            }
          }
          
          // Color object format like {color: '#ff0000', percentage: 0.25}  
          else if (color.color) {
            const hexColor = color.color.startsWith('#') ? color.color : `#${color.color}`
            const percentage = typeof color.percentage === 'number' ? color.percentage : 1.0 / rawColorsData.length
            console.log(`✅ Color object format -> ${hexColor} (${(percentage * 100).toFixed(2)}%)`)
            return {
              hex: hexColor,
              percentage: percentage
            }
          }
        }
        
        console.warn('⚠️ Unknown color format:', color)
        return {
          hex: '#000000',
          percentage: 1.0 / rawColorsData.length
        } // fallback
      }).filter(Boolean)
      
      console.log('🎨 Final processed colors:', processed)
      console.log('📊 Color percentages:', processed.map(c => `${c.hex}: ${(c.percentage * 100).toFixed(2)}%`))
      return processed
    }
    
    const getColorFromRawColor = (colorData) => {
      // Handle new object format with hex property
      if (colorData && typeof colorData === 'object' && colorData.hex) {
        return colorData.hex
      }
      
      // Legacy string format
      if (typeof colorData === 'string') {
        return colorData.startsWith('#') ? colorData : `#${colorData}`
      } 
      
      // Legacy object formats
      else if (colorData && typeof colorData === 'object') {
        if (colorData.color) {
          return colorData.color.startsWith('#') ? colorData.color : `#${colorData.color}`
        } else if (typeof colorData.r === 'number' && typeof colorData.g === 'number' && typeof colorData.b === 'number') {
          return `rgb(${colorData.r}, ${colorData.g}, ${colorData.b})`
        }
      }
      
      console.warn('⚠️ Unable to extract color from:', colorData)
      return '#000000' // fallback
    }
    
    const getRawColorPercentage = (colorData) => {
      // Handle new object format with percentage property
      if (colorData && typeof colorData === 'object' && typeof colorData.percentage === 'number') {
        return colorData.percentage
      }
      
      // Fallback: equal distribution
      const total = rawColors.value.length
      if (total > 0) {
        return 1.0 / total
      }
      
      console.warn('⚠️ Unable to determine percentage for color:', colorData)
      return 0
    }
    
    const getEmotionImageSrc = (emotionName) => {
      // Map emotion names to statically imported images
      const emotionImageMap = {
        'anger': angerImg,
        'anticipation': anticipationImg,
        'arrogance': arroganceImg,
        'disagreeableness': disagreeablenessImg,
        'disgust': disgustImg,
        'fear': fearImg,
        'gratitude': gratitudeImg,
        'happiness': happinessImg,
        'humility': humilityImg,
        'love': loveImg,
        'optimism': optimismImg,
        'pessimism': pessimismImg,
        'sadness': sadnessImg,
        'surprise': surpriseImg,
        'trust': trustImg
      }
      
      const imageName = emotionName.toLowerCase()
      const imagePath = emotionImageMap[imageName]
      
      if (imagePath) {
        console.log(`🖼️ Loading emotion image for ${emotionName}: ${imagePath}`)
        return imagePath
      }
      
      console.warn(`⚠️ No emotion image found for: ${emotionName}`)
      return null
    }
    
    const handleImageError = () => {
      console.error('❌ Captured palette image failed to load:', capturedImageUrl.value)
      // Attempt next fallback URL if available
      if (imageFallbackUrls.value && imageFallbackUrls.value.length > 0) {
        const nextUrl = imageFallbackUrls.value.shift()
        console.log('🔁 Retrying with fallback URL:', nextUrl)
        capturedImageUrl.value = nextUrl
      }
    }
    
    const handleImageLoad = () => {
      console.log('✅ Captured palette image loaded successfully:', capturedImageUrl.value)
    }
    
    // Lifecycle
    onMounted(() => {
      console.log('🎬 ColorPalettePage mounted!')
      loadPageData()
      console.log('📊 Initial state:', {
        hasRouteData: !!route.query.data,
        colourDataLength: colourData.value?.length,
        rawColorsLength: rawColors.value?.length
      })
    })
    
    return {
      loading,
      loadingMessage,
      spinnerType,
      selectedEmotion,
      selectedIntensity,
      colourData,
      rawColors,
      emotionPrediction,
      topEmotions,
      displayedEmotions,
      capturedImageUrl,
      showEmotionSelection,
      emotionResetCount,
      remainingReloads,
      selectEmotion,
      proceedToGallery,
      recapture,
      shuffleEmotions,
      getEmotionColor,
      getEmotionImageSrc,
      getColorFromRawColor,
      getRawColorPercentage,
      getIntensityStars,
      pageData,
      handleImageError,
      handleImageLoad
    }
  }
}
</script>

<style scoped>


.color-palette-page {
  display: block;
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
}

.gallery-container {
  max-width: 1000px;
  margin: 0 auto;
  color: white;
  text-align: center;
}

.gallery-title {
  font-size: 40px;
  margin-bottom: 10px;
  font-weight: 250;
  letter-spacing: 1px;
  font-family: 'Poppins', sans-serif;
}

.gallery-subtitle {
  font-size: 20px;
  color: #ccc;
  margin-bottom: 40px;
  font-weight: 300;
  font-family: 'Poppins', sans-serif;
}

.palette-analysis-container {
  background: rgba(40, 40, 40, 0.9);
  border-radius: 20px;
  padding: 40px;
  margin: 40px 0;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.captured-image-section {
  margin-bottom: 40px;
}

.captured-image-title {
  font-size: 25px;
  margin-bottom: 20px;
  color: #fff;
  font-weight: 400;
  font-family: 'Poppins', sans-serif;
}

.captured-palette-image {
  width: 100%;
  height: 450px;
  object-fit: cover;
  border-radius: 15px;
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.raw-colors-section,
.mapped-colors-section {
  margin: 40px 0;
}

.raw-colors-title,
.mapped-colors-title {
  font-size: 20px;
  margin-bottom: 20px;
  color: #fff;
  font-weight: 450;
  font-family: 'Poppins', sans-serif;
}

.basic-colours-hover {
  text-decoration: underline;
  cursor: help;
  position: relative;
  display: inline-block;
}

.tooltip {
  visibility: hidden;
  opacity: 0;
  position: absolute;
  bottom: 125%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.5);
  padding: 10px;
  z-index: 1000;
  transition: opacity 0.3s ease, visibility 0.3s ease;
  backdrop-filter: blur(5px);
}

.basic-colours-hover:hover .tooltip {
  visibility: visible;
  opacity: 1;
}

.tooltip-image {
  width: 400px;
  height: auto;
  border-radius: 6px;
  display: block;
}

/* Arrow for tooltip */
.tooltip::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 8px solid transparent;
  border-top-color: rgba(0, 0, 0, 0.85);
}

.chart-container {
  margin: 20px 0;
}

.color-bar {
  height: 60px;
  border-radius: 30px;
  overflow: hidden;
  display: flex;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.color-segment {
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.color-segment:hover {
  transform: scaleY(1.1);
  z-index: 10;
}

.colour-legend {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 20px;
  margin-top: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 15px;
  border-radius: 20px;
  backdrop-filter: blur(5px);
}

.legend-color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 8px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.legend-text {
  font-size: 0.9rem;
  color: #fff;
}

.color-explanation {
  margin-top: 40px;
  text-align: left;
  background: rgba(0, 0, 0, 0.3);
  padding: 20px;
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.color-explanation h4 {
  color: #ffffff;
  margin-bottom: 10px;
  font-size: 1.1rem;
  font-weight: 500;
}

.color-explanation p {
  color: #ccc;
  line-height: 1.6;
  font-size: 0.95rem;
}

.emotion-container {
  margin: 60px 0;
  background: rgba(40, 40, 40, 0.9);
  border-radius: 20px;
  padding: 40px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.emotion-title-section {
  line-height: 1.5;
}

.emotion-step-title {
  font-family: 'Poppins', sans-serif;
  font-size: 18px;
  color: #ffffff;
  font-weight: 600;
}

.emotion-main-title {
  font-family: 'Poppins', sans-serif;
  font-size: 18px;
  color: #fff;
  font-weight: 400;
  line-height: 1.5;
}

.emotion-cards-container {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin: 40px 0;
  flex-wrap: nowrap;
  align-items: stretch;
}

.emotion-card {
  background: rgba(60, 60, 60, 0.8);
  border: 2px solid transparent;
  border-radius: 20px;
  padding: 20px;
  width: 300px;
  height: 400px;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.emotion-card:hover {
  transform: translateY(-5px);
  background: rgba(70, 70, 70, 0.9);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.emotion-card-selected {
  border-color: #ffffff;
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 0 20px rgba(78, 205, 196, 0.3);
}

.emotion-card-name {
  font-size: 1.2rem;
  color: #fff;
  font-weight: 500;
  margin-bottom: 15px;
  text-transform: capitalize;
  font-family: 'Poppins', sans-serif;
}

.emotion-card-image-container {
  width: 100%;
  height: 250px;
  margin: 15px 0;
  border-radius: 10px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.3);
}

.emotion-card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.emotion-card:hover .emotion-card-image {
  transform: scale(1.05);
}

.emotion-card-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
  color: white;
  text-transform: capitalize;
  border-radius: 10px;
}

.no-colors-message {
  text-align: center;
  padding: 20px;
  color: #ccc;
  font-style: italic;
}

.emotion-card-stars {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin: 15px 0;
  font-size: 2rem;
}

.star {
  color: #444;
  transition: all 0.3s ease;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.star-filled {
  color: #ffa502;
  text-shadow: 0 0 10px rgba(255, 165, 2, 0.5);
}

.emotion-card-intensity-label {
  font-size: 0.9rem;
  color: #ccc;
  font-weight: 400;
  font-family: 'Poppins', sans-serif;
  text-transform: capitalize;
  margin-top: 5px;
}

.more-feelings-btn {
  background: rgba(232, 232, 224, 0.87);
  color: rgb(14, 14, 14);
  border: none;
  outline: none;
  padding: 12px 30px;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 500;
  font-family: 'Poppins', sans-serif;
  cursor: pointer;
  transition: all 0.3s ease;
  margin: 20px 0;
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.more-feelings-btn:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(115, 115, 115, 0.4);
}

.more-feelings-btn:focus {
  outline: none;
}

.more-feelings-btn:active {
  outline: none;
  transform: translateY(0px);
}

.more-feelings-btn.disabled {
  background: #666;
  cursor: not-allowed;
  opacity: 0.6;
}

.more-feelings-btn:hover:not(.disabled) {
  background: linear-gradient(45deg, #1e1e1e, #1e1e1e);
  box-shadow: 0 5px 15px rgba(100, 101, 101, 0.4);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.reload-counter {
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(255,255,255,0.2);
  color: inherit;
  font-weight: 600;
}
.reload-counter.zero {
  background: rgba(255, 80, 80, 0.2);
  color: #ff5050;
}

.emotion-explanation {
  margin-top: 40px;
  text-align: left;
  background: rgba(0, 0, 0, 0.3);
  padding: 20px;
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.emotion-explanation h4 {
  color: #ffffff;
  margin-bottom: 10px;
  font-size: 1.1rem;
  font-weight: 500;
}

.emotion-explanation p {
  color: #ccc;
  line-height: 1.6;
  font-size: 0.95rem;
}

.color-palette-controls {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
  flex-wrap: wrap;
}

.btn-primary,
.btn-secondary {
  padding: 15px 35px;
  border: none;
  border-radius: 30px;
  font-size: 1.1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Poppins', sans-serif;
  min-width: 150px;
}

.btn-primary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.btn-primary:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.btn-secondary {
  background: linear-gradient(45deg, #ffffff, #ffffff);
  color: black;
  
}

.btn-secondary:hover:not(.disabled) {
  background: linear-gradient(45deg, #1e1e1e, #1e1e1e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(100, 101, 101, 0.4);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary.disabled {
  background: #666;
  cursor: not-allowed;
  opacity: 0.6;
}

/* Global button focus disable */
button:focus {
  outline: none !important;
}

/* Responsive design */
@media (max-width: 768px) {
  .gallery-title {
    font-size: 2rem;
  }
  
  .palette-analysis-container,
  .emotion-container {
    padding: 20px;
    margin: 20px 0;
  }
  
  .emotion-cards-container {
    flex-direction: column;
    align-items: center;
  }
  
  .emotion-card {
    width: 250px;
  }
  
  .color-palette-controls {
    flex-direction: column;
    align-items: center;
  }
}
</style>
