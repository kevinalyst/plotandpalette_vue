<template>
  <div class="gallery-page">
    <div class="gallery-container" v-if="allPaintings && allPaintings.length > 0">
      <!-- Step Progress Indicator -->
      <div class="progress-indicator">
        <div class="progress-step completed">{{ $t('gallery.step1') }}</div>
        <div :class="['progress-step', { completed: ste2Complete }]">{{ $t('gallery.step2') }}</div>
        <div :class="['progress-step', { completed: step3Complete }]">{{ $t('gallery.step3') }}</div>
        <div :class="['progress-step', { completed: step4Complete }]">{{ $t('gallery.step4') }}</div>
      </div>

      <!-- Painting Gallery -->
      <div class="gallery-section">
        <h3>{{ $t('gallery.title') }}</h3>
        <p class="gallery-subtitle">{{ $t('gallery.subtitle') }}</p>
        <div class="top-row-info">
          <p class="sub-instruction">{{ $t('gallery.sourceNote') }}</p>
          <div 
            class="previous-selection"
            @mouseenter="showPrevious = true"
            @mouseleave="showPrevious = false"
          >
            <span>{{ $t('gallery.hoverPrevious') }}</span>
            <img src="@/assets/images/hoverpalette.png" alt="Previous selection" class="previous-icon" />
            <div v-if="showPrevious" class="previous-popup">
              <div class="previous-title">{{ $t('gallery.previousPalette') }}</div>
              <div class="previous-image-wrapper">
                <img :src="previousCapturedUrl" alt="captured palette" class="previous-image" />
              </div>
              <div class="previous-emotion">{{ $t('gallery.previousEmotion') }} <span class="emotion-highlight">{{ previousEmotion ? $t(`emotions.${previousEmotion}`) : '—' }}</span></div>
            </div>
          </div>
        </div>
        
        <div class="paintings-grid-container">
          <!-- Integrated overlay navigation within the grid container -->
          <button 
            v-if="!showAllPaintings" 
            @click="prevPaintings" 
            class="grid-nav-btn grid-nav-left" 
            aria-label="Previous"
          >‹</button>
          
          <div class="paintings-grid" ref="paintingsGrid" v-if="allPaintings && allPaintings.length > 0">
            <div 
              v-for="(painting, index) in allPaintings" 
              :key="painting.url || index"
              class="painting-item"
              :data-number="index + 1"
            >
              <img 
                :src="painting.url" 
                :alt="painting.title"
                @error="handleImageError($event, painting)"
                @click="openPaintingModal(painting)"
                loading="lazy"
              />
              <div class="painting-hover-info">
                <div class="hover-content">
                  <h4>{{ painting.title }}</h4>
                  <p>{{ painting.artist }}</p>
                  <p>{{ painting.year }}</p>
                </div>
              </div>
              <button 
                :class="['painting-select-btn', { 'selected': isPaintingSelected(painting) }]"
                @click.stop="togglePaintingSelection(painting)"
              >
                {{ isPaintingSelected(painting) ? $t('gallery.unselect') : $t('gallery.select') }}
              </button>
            </div>
          </div>
          
          <button 
            v-if="!showAllPaintings" 
            @click="nextPaintings" 
            class="grid-nav-btn grid-nav-right" 
            aria-label="Next"
          >›</button>
        </div>
        
        <!-- Removed custom scroll bar -->
        
        <!-- Recapture Option -->
        <div class="gallery-recapture">
          <span class="recapture-text-left">{{ $t('gallery.reloadPrefix') }}</span>
          <button 
            @click="reloadRecommendations" 
            class="recapture-btn"
            :disabled="remainingReloads <= 0"
          >
            {{ $t('gallery.reloadButton') }}
            <span :class="['reload-counter', { zero: remainingReloads === 0 }]">{{ remainingReloads }}/3</span>
          </button>
          <span class="recapture-text-right">{{ $t('gallery.reloadSuffix') }}</span>
        </div>
      </div>

      <!-- Selected Paintings Drop Zone -->
      <div class="selection-area">
        <h2>{{ $t('gallery.selectedPaintings') }}</h2>
        <p class="instruction">
          <span class="step-label">{{ $t('gallery.step3Label') }}</span> <br/>
          <span class="step-label-text">{{ $t('gallery.step3Text1') }}</span> <br/>
          <span class="step-label-text">{{ $t('gallery.step3Text2') }}</span>
        </p>
        <p class="sub-instruction">{{ $t('gallery.clickInstruction') }}</p>
        
        <div class="drop-zones">
          <div 
            v-for="i in 3" 
            :key="i"
            :class="['drop-zone', { 'has-painting': selectedPaintings[i-1] }]"
          >
            <div v-if="selectedPaintings[i-1]" class="selected-painting">
              <img :src="selectedPaintings[i-1].url" :alt="selectedPaintings[i-1].title" />
              <button @click="removePainting(i-1)" class="remove-btn">×</button>
            </div>
            <div v-else class="drop-placeholder">
              <img src="@/assets/images/drop.png" alt="Drop painting here" class="drop-placeholder-image" />
            </div>
          </div>
        </div>
      </div>

      
      
      <!-- Character Selection -->
      <div v-if="step2Complete" class="selection-area">
        <p class="instruction">
          <span class="step-label">{{ $t('gallery.step4Label') }}</span> <br/>
          <span class="step-label-text">{{ $t('gallery.step4Text1') }}</span> <br/>
          <span class="step-label-text">{{ $t('gallery.step4Text2') }}</span>
        </p>
        <p class="sub-instruction">{{ $t('gallery.selectPerspective') }}</p>
                 <p class="sub-instruction">{{ $t('gallery.hoverCards') }}</p>
        
        <div class="character-cards" v-if="characters && characters.length > 0">
          <div 
            v-for="character in characters" 
            :key="character.id"
            :class="['character-card', { 'selected': selectedCharacter === character.id }]"
            @click="selectCharacter(character.id)"
            @mouseenter="showCharacterDescription(character.id)"
            @mouseleave="hideCharacterDescription"
          >
            <img :src="character.image" :alt="character.name" v-if="hoveredCharacter !== character.id"/>
            <img :src="character.image_b" :alt="character.name" v-if="hoveredCharacter === character.id"/>
            <!-- <div class="exit-btn" v-if="selectedCharacter === character.id" @click="closeCharacter(character.id)">x</div> -->
            
            <!-- Text overlay -->
            <div class="character-card-text">
              <div v-if="hoveredCharacter !== character.id" class="character-title">
                {{ $t(`characters.${character.id}.title`) }}
              </div>
              <div v-else class="character-description">
                {{ $t(`characters.${character.id}.description`) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Painting Preview Modal -->
      <div v-if="showPaintingModal" class="painting-modal-overlay" @click="closePaintingModal">
        <div class="painting-modal" @click.stop>
          <button @click="closePaintingModal" class="painting-modal-close">
            <img src="@/assets/images/closebutton.png" alt="Close" />
          </button>
          <div class="painting-modal-content">
            <div class="painting-modal-image">
              <img :src="selectedPaintingForModal.url" :alt="selectedPaintingForModal.title" />
            </div>
            <div class="painting-modal-meta">
              <a 
                v-if="selectedPaintingForModal.page"
                :href="selectedPaintingForModal.page"
                target="_blank"
                rel="noopener noreferrer"
                class="check-source-link"
              >{{ $t('gallery.seeOriginalSource') }}</a>
            </div>
          </div>
        </div>
      </div>

      <!-- All Done Button -->
      <div v-if="step3Complete" class="story-section">
        <button 
          :class="['all-done-btn', { 'interactive': step4Complete }]"
          @click="generateStory"
          :disabled="!step4Complete || generatingStory"
        >
          {{ generatingStory ? $t('gallery.creatingStory') : $t('gallery.allDone') }}
        </button>
      </div>
    </div>
    
    <LoadingSpinner :show="loading" :message="loadingMessage" :type="spinnerType" />
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ApiService from '@/services/api.js'

export default {
  name: 'GalleryPage',
  components: {
    LoadingSpinner
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const { t } = useI18n()
    
    // Reactive data
    const loading = ref(false)
    const loadingMessage = ref('')
    const spinnerType = ref('magic-cube')
    const generatingStory = ref(false)
    
    // Page data
    const pageData = ref({})
    const recommendations = ref([])
    const selectedPaintings = ref([])
    const selectedCharacter = ref('')
    const hoveredCharacter = ref('')
    const showAllPaintings = ref(false)
    const emotionFromPalette = ref('')
    const rawColorsFromPalette = ref([])
    const capturedFilename = ref('')
    const reloadCount = ref(0)
    const remainingReloads = ref(3)
    
    // Painting modal state
    const showPaintingModal = ref(false)
    const selectedPaintingForModal = ref({})
    
    // Step completion tracking
    const step2Complete = computed(() => {
      return selectedPaintings.value && selectedPaintings.value.filter(p => p !== null && p !== undefined).length === 3
    })
    const step3Complete = computed(() => {
      return step2Complete.value && selectedCharacter.value
    })
    const step4Complete = computed(() => {
      return step3Complete.value // Character selection is final step
    })
    
    // Character options
    const characters = ref([
      {
        id: 'historian',
        name: 'Historian\'s Chronicle',
        image: new URL('@/assets/images/style1-a.png', import.meta.url).href,
        image_b: new URL('@/assets/images/style1-b.png', import.meta.url).href
      },
      {
        id: 'poet',
        name: 'The Poet\'s Dream', 
        image: new URL('@/assets/images/style2-a.png', import.meta.url).href,
        image_b: new URL('@/assets/images/style2-b.png', import.meta.url).href
      },
      {
        id: 'detective',
        name: 'The Detective\'s Case',
        image: new URL('@/assets/images/style3-a.png', import.meta.url).href,
        image_b: new URL('@/assets/images/style3-b.png', import.meta.url).href
      },
      {
        id: 'critic',
        name: 'The Critic\'s Analysis',
        image: new URL('@/assets/images/style4-a.png', import.meta.url).href,
        image_b: new URL('@/assets/images/style4-b.png', import.meta.url).href
      },
      {
        id: 'time_traveller',
        name: 'The Time Traveller\'s Report',
        image: new URL('@/assets/images/style5-a.png', import.meta.url).href,
        image_b: new URL('@/assets/images/style5-b.png', import.meta.url).href
      }
    ])
    
    // Drag and drop
    const draggedPainting = ref(null)
    
    // Gallery data - will be populated from backend recommendations
    const allPaintings = ref([])

    // Previous selection hover state
    const showPrevious = ref(false)
    const previousCapturedUrl = ref('')
    const previousEmotion = ref('')

    // Refs for scroll functionality
    const paintingsGrid = ref(null)
    const scrollPosition = ref(0)
    
    // Computed properties for scroll thumb
    const scrollThumbPosition = computed(() => {
      if (!paintingsGrid.value) return 0
      const maxScroll = paintingsGrid.value.scrollWidth - paintingsGrid.value.clientWidth
      if (maxScroll <= 0) return 0
      return (scrollPosition.value / maxScroll) * 100
    })
    
    const scrollThumbWidth = computed(() => {
      if (!paintingsGrid.value) return 100
      const visibleRatio = paintingsGrid.value.clientWidth / paintingsGrid.value.scrollWidth
      return Math.max(10, visibleRatio * 100) // Minimum 10% width
    })

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

    // Normalize various raw color formats to backend-expected [{r,g,b,percentage}] x 5
    const normalizeToBackendRawColors = (rawColorsInput) => {
      try {
        if (!rawColorsInput) return []

        // Already in backend format
        if (Array.isArray(rawColorsInput) && rawColorsInput.length === 5 &&
            rawColorsInput.every(c => typeof c === 'object' && ('bgr' in c || 'hsv' in c || 'lab' in c))) {
          return rawColorsInput
        }

        // Legacy minimal RGB format
        if (Array.isArray(rawColorsInput) && rawColorsInput.length === 5 &&
            rawColorsInput.every(c => typeof c === 'object' && 'r' in c && 'g' in c && 'b' in c)) {
          return rawColorsInput
        }

        // Helper: hex to rgb
        const hexToRgb = (hex) => {
          const clean = hex.startsWith('#') ? hex.slice(1) : hex
          const bigint = parseInt(clean, 16)
          if (Number.isNaN(bigint)) return { r: 0, g: 0, b: 0 }
          if (clean.length === 3) {
            const r = parseInt(clean[0] + clean[0], 16)
            const g = parseInt(clean[1] + clean[1], 16)
            const b = parseInt(clean[2] + clean[2], 16)
            return { r, g, b }
          }
          const r = (bigint >> 16) & 255
          const g = (bigint >> 8) & 255
          const b = bigint & 255
          return { r, g, b }
        }

        // Dictionary format: {"#aabbcc": 0.12, ...}
        if (!Array.isArray(rawColorsInput) && typeof rawColorsInput === 'object') {
          const entries = Object.entries(rawColorsInput).slice(0, 5)
          return entries.map(([hex, percentage]) => ({
            ...hexToRgb(hex),
            percentage: typeof percentage === 'number' ? percentage : (1 / entries.length)
          }))
        }

        if (Array.isArray(rawColorsInput)) {
          const list = rawColorsInput.slice(0, 5)
          return list.map((item) => {
            if (typeof item === 'string') {
              const { r, g, b } = hexToRgb(item)
              return { r, g, b, percentage: 1 / list.length }
            }
            if (item && typeof item === 'object') {
              if ('hex' in item) {
                const { r, g, b } = hexToRgb(item.hex)
                return { r, g, b, percentage: typeof item.percentage === 'number' ? item.percentage : (1 / list.length) }
              }
              if ('color' in item) {
                const { r, g, b } = hexToRgb(item.color)
                return { r, g, b, percentage: typeof item.percentage === 'number' ? item.percentage : (1 / list.length) }
              }
              if ('r' in item && 'g' in item && 'b' in item) {
                return { r: item.r, g: item.g, b: item.b, percentage: typeof item.percentage === 'number' ? item.percentage : (1 / list.length) }
              }
            }
            // Fallback
            return { r: 0, g: 0, b: 0, percentage: 1 / list.length }
          })
        }

        return []
      } catch (e) {
        console.error('Failed to normalize raw colors:', e)
        return []
      }
    }


    // Methods
    const loadPageData = async () => {
      try {
        if (route.query.data) {
          const data = JSON.parse(unicodeSafeBase64Decode(route.query.data))
          pageData.value = data
          // Prepare previous selection data (from ColorPalettePage payload)
          const filename = data.filename || (data?.pageData?.filename)
          const cacheBuster = Date.now()
          const possibleUrls = [
            `/api/uploads/${filename}?v=${cacheBuster}`,
            `/uploads/${filename}?v=${cacheBuster}`,
            `./uploads/${filename}?v=${cacheBuster}`,
            `${window.location.origin}/uploads/${filename}?v=${cacheBuster}`,
            data.capturedImageUrl
          ].filter(Boolean)
           if (filename) {
            previousCapturedUrl.value = possibleUrls[0]
          } else if (data.capturedImageUrl) {
            previousCapturedUrl.value = data.capturedImageUrl
          }
          previousEmotion.value = (data.selectedEmotion || data?.emotionPrediction?.emotion || '').toString()

           // store for reloads – prefer backend-ready format if present
           emotionFromPalette.value = data.selectedEmotion || data?.emotionPrediction?.emotion || ''
           if (Array.isArray(data.rawColors) && data.rawColors.length === 5 && typeof data.rawColors[0] === 'object' && ('bgr' in data.rawColors[0] || 'hsv' in data.rawColors[0] || 'lab' in data.rawColors[0])) {
             // Use enriched colors from backend as-is
             rawColorsFromPalette.value = data.rawColors
           } else if (Array.isArray(data.rawColorsForRecommendation) && data.rawColorsForRecommendation.length === 5) {
             rawColorsFromPalette.value = data.rawColorsForRecommendation
           } else if (data.rawColors) {
             rawColorsFromPalette.value = normalizeToBackendRawColors(data.rawColors)
           }
           capturedFilename.value = filename || ''
          
          // Use detailedRecommendations from the backend which includes title, artist, year, url
          console.log('📊 Page data received:', data)
          console.log('🎨 DetailedRecommendations:', data.detailedRecommendations)
          console.log('🌐 Simple recommendations:', data.recommendations)
          
          if (data.detailedRecommendations && data.detailedRecommendations.length > 0) {
            // Use URLs directly - they already point to /api/assets/paintings/
            const processedPaintings = data.detailedRecommendations.map(painting => ({
              ...painting,
              url: painting.url // Use direct URL, no proxy needed
            }))
            allPaintings.value = processedPaintings
            recommendations.value = processedPaintings
            console.log('✅ Loaded paintings with direct URLs:', allPaintings.value.length)
          } else if (data.recommendations && data.recommendations.length > 0) {
            // Fallback: convert simple URL list to detailed format
            console.log('⚠️ Using fallback: converting URLs to painting objects')
            const paintingObjects = data.recommendations.map((url, index) => ({
              url: url, // Use direct URL, no proxy needed
              title: `Painting ${index + 1}`,
              artist: 'Unknown Artist', 
              year: 'Unknown Year'
            }))
            allPaintings.value = paintingObjects
            recommendations.value = paintingObjects
          } else {
            console.log('⚠️  No recommendations in navigation data, will try database fetch');
            // Don't throw error - continue to database fetch below
          }
        } else {
          router.push('/')
        }
        
        // Fetch fresh recommendations from dedicated table
        const sessionId = localStorage.getItem('sessionId');
        if (sessionId) {
          try {
            console.log('📡 Fetching fresh recommendations for session:', sessionId);
            
            const response = await ApiService.request(`/recommendations/${sessionId}`);
            
            if (response.success && response.data && response.data.recommendations) {
              // Use URLs directly - they already point to /api/assets/paintings/
              const processedPaintings = response.data.recommendations.map(painting => ({
                ...painting,
                url: painting.url // Use direct URL, no proxy needed
              }));
              
              allPaintings.value = processedPaintings;
              recommendations.value = processedPaintings;
              
              console.log('✅ Loaded', processedPaintings.length, 'fresh recommendations from database');
            } else {
              console.log('📦 No recommendations in database yet');
              // If no data from navigation and no data from database, show error
              if (!allPaintings.value || allPaintings.value.length === 0) {
                throw new Error('No painting recommendations available yet. Please wait for the analysis to complete.');
              }
            }
          } catch (error) {
            console.warn('⚠️  Could not fetch recommendations from database:', error);
            // If no data from navigation and database fetch failed, show error
            if (!allPaintings.value || allPaintings.value.length === 0) {
              throw new Error('No painting recommendations available. Backend connection required.');
            }
          }
        }
      } catch (error) {
        console.error('Error loading page data:', error)
        alert('Failed to load painting recommendations. Backend connection required.')
        router.push('/')
      }
    }

    const recaptureGallery = () => {}

    const reloadRecommendations = async () => {
      if (remainingReloads.value <= 0) return
      try {
        loading.value = true
        loadingMessage.value = t('loading.refreshingRecommendations')
        spinnerType.value = 'keyboard'

        // Re-run recommendations using the same raw color statistics
        let rawColorsPayload = []
        if (rawColorsFromPalette.value && rawColorsFromPalette.value.length === 5) {
          rawColorsPayload = rawColorsFromPalette.value
        } else if (pageData.value) {
          if (Array.isArray(pageData.value.rawColorsForRecommendation) && pageData.value.rawColorsForRecommendation.length === 5) {
            rawColorsPayload = pageData.value.rawColorsForRecommendation
          } else if (pageData.value.rawColors) {
            rawColorsPayload = normalizeToBackendRawColors(pageData.value.rawColors)
          }
        }

        if (!rawColorsPayload || rawColorsPayload.length !== 5) {
          console.error('❌ Unable to reload: missing 5 raw colors payload')
          loading.value = false
          spinnerType.value = 'magic-cube'
          return
        }

        // Create RELOAD_RECOMMENDATIONS job with excludeIds
        const sessionId = localStorage.getItem('sessionId')
        const excludeIds = allPaintings.value.map(p => p.id).filter(Boolean)
        
        console.log('🔄 Creating reload job with', excludeIds.length, 'IDs to exclude')
        
        const job = await ApiService.createJob({
          type: 'RELOAD_RECOMMENDATIONS',
          session_id: sessionId,
          input_data: {
            rawColors: rawColorsPayload,
            emotion: emotionFromPalette.value || pageData.value.selectedEmotion || 'neutral',
            excludeIds: excludeIds
          }
        })
        
        console.log('✅ Reload job created:', job.data.job_id)
        
        // Poll for new recommendations (max 30 seconds, 1 second interval)
        const result = await ApiService.pollJob(job.data.job_id, 30, 1000)
        
        // Transform result to expected format
        const res = result && result.detailedRecommendations 
          ? { success: true, detailedRecommendations: result.detailedRecommendations }
          : { success: false }
        
        if (res && res.success && res.detailedRecommendations && res.detailedRecommendations.length > 0) {
          const processedPaintings = res.detailedRecommendations.map(painting => ({
            ...painting,
            url: painting.url // Use direct URL, no proxy needed
          }))
          // Do not clear selectedPaintings; only replace the pool
          allPaintings.value = processedPaintings
          recommendations.value = processedPaintings
        } else if (res && res.recommendations && res.recommendations.length > 0) {
          const paintingObjects = res.recommendations.map((url, index) => ({
            url: url, // Use direct URL, no proxy needed
            title: `Painting ${index + 1}`,
            artist: 'Unknown Artist',
            year: 'Unknown Year'
          }))
          allPaintings.value = paintingObjects
          recommendations.value = paintingObjects
        } else {
          console.warn('⚠️ Reload returned no recommendations')
        }

        reloadCount.value += 1
        remainingReloads.value = Math.max(0, 3 - reloadCount.value)
      } catch (e) {
        console.error('❌ Failed to reload recommendations:', e)
      } finally {
        loading.value = false
        spinnerType.value = 'magic-cube'
      }
    }

    const nextPaintings = () => {
      if (!paintingsGrid.value) return
      // Move by exactly one painting width (assumes consistent card width + gap)
      const card = paintingsGrid.value.querySelector('.painting-item')
      const scrollAmount = card ? (card.clientWidth + 20) : paintingsGrid.value.clientWidth * 0.8
      const maxScroll = paintingsGrid.value.scrollWidth - paintingsGrid.value.clientWidth
      const newScrollPosition = Math.min(scrollPosition.value + scrollAmount, maxScroll)
      
      paintingsGrid.value.scrollTo({
        left: newScrollPosition,
        behavior: 'smooth'
      })
    }

    const prevPaintings = () => {
      if (!paintingsGrid.value) return
      const card = paintingsGrid.value.querySelector('.painting-item')
      const scrollAmount = card ? (card.clientWidth + 20) : paintingsGrid.value.clientWidth * 0.8
      const newScrollPosition = Math.max(scrollPosition.value - scrollAmount, 0)
      
      paintingsGrid.value.scrollTo({
        left: newScrollPosition,
        behavior: 'smooth'
      })
    }
    
    const updateScrollPosition = () => {
      if (paintingsGrid.value) {
        scrollPosition.value = paintingsGrid.value.scrollLeft
      }
    }
    
    const initializeScrollHandler = () => {
      if (paintingsGrid.value) {
        paintingsGrid.value.addEventListener('scroll', updateScrollPosition)
        // Initialize scroll position
        updateScrollPosition()
      }
    }
    
    
    const handleDragStart = (event, painting) => {
      draggedPainting.value = painting
      event.dataTransfer.effectAllowed = 'copy'
    }
    
        const handleDrop = (event, slotIndex) => {
      event.preventDefault()
      
      if (draggedPainting.value && selectedPaintings.value && !selectedPaintings.value[slotIndex]) {
        // Check if painting is already selected in another slot
        const existingIndex = selectedPaintings.value.findIndex(p => 
          p && p.url === draggedPainting.value.url
        )
        
        if (existingIndex === -1) {
          selectedPaintings.value[slotIndex] = draggedPainting.value
        }
      }
      
      draggedPainting.value = null
    }

    const openPaintingModal = (painting) => {
      if (painting && (painting.url || painting.originalUrl)) {
        selectedPaintingForModal.value = {
          url: painting.url || painting.originalUrl,
          title: painting.title,
          artist: painting.artist,
          page: painting.page || painting.source || ''
        }
        showPaintingModal.value = true
      }
    }

    const closePaintingModal = () => {
      showPaintingModal.value = false
      selectedPaintingForModal.value = {}
    }

    // Check if a painting is currently selected
    const isPaintingSelected = (painting) => {
      if (!painting || !selectedPaintings.value) return false
      return selectedPaintings.value.some(p => p && p.url === painting.url)
    }
    
    // Toggle painting selection (Select/Unselect)
    const togglePaintingSelection = (painting) => {
      if (!painting || !selectedPaintings.value) return
      
      // Check if already selected
      const selectedIndex = selectedPaintings.value.findIndex(p => p && p.url === painting.url)
      
      if (selectedIndex !== -1) {
        // Unselect: remove from array
        selectedPaintings.value[selectedIndex] = null
        console.log('🗑️ Unselected painting:', painting.title)
      } else {
        // Select: find first empty slot
        const emptySlot = selectedPaintings.value.findIndex(slot => !slot)
        
        if (emptySlot !== -1) {
          selectedPaintings.value[emptySlot] = painting
          console.log('✅ Selected painting:', painting.title, 'in slot', emptySlot + 1)
        } else {
          console.warn('⚠️ Cannot select more than 3 paintings')
        }
      }
    }

    const selectPainting = (painting) => {
      if (!selectedPaintings.value || !painting) return
      
      // Find first empty slot
      const emptySlot = selectedPaintings.value.findIndex(slot => !slot)
      
      if (emptySlot !== -1) {
        // Check if painting is already selected
        const alreadySelected = selectedPaintings.value.some(p => 
          p && p.url === painting.url
        )
        
        if (!alreadySelected) {
          selectedPaintings.value[emptySlot] = painting
        }
      }
    }

    const removePainting = (index) => {
      if (selectedPaintings.value && selectedPaintings.value[index]) {
        selectedPaintings.value[index] = null
      }
    }
    
    const selectCharacter = (characterId) => {
      selectedCharacter.value = characterId
      // No modal needed - character selection is final
    }

    const showCharacterDescription = (characterId) => {
      hoveredCharacter.value = characterId
    }

    const hideCharacterDescription = () => {
      hoveredCharacter.value = ''
    }
    
    const handleImageError = (event, painting) => {
      console.warn(`Failed to load image for painting: ${painting.title}`, painting.url)
      // Set a placeholder image or hide the image
      event.target.style.display = 'none'
      // Optionally, you could set a placeholder image:
      // event.target.src = '/assets/images/placeholder.png'
    }
    
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
    
    const generateStory = async () => {
      if (!step4Complete.value) return
      
      console.log('🚀 Generating story with selections:')
      console.log('- Paintings:', selectedPaintings.value.filter(p => p))
      console.log('- Character:', selectedCharacter.value)
      console.log('- Page data:', pageData.value)
      
      // Validate required data before making API calls
      const validPaintings = selectedPaintings.value
        .filter(p => p && (p.url || p.originalUrl) && p.title && p.artist)
        .map(p => ({
          ...p,
          url: p.originalUrl || p.url // Use original URL for backend processing
        }))
      console.log('- Valid paintings count:', validPaintings.length)
      console.log('- Valid paintings:', validPaintings)
      
      if (validPaintings.length !== 3) {
        alert(`Error: Need exactly 3 valid paintings, but found ${validPaintings.length}`)
        return
      }
      
      if (!selectedCharacter.value) {
        alert('Error: No character selected')
        return
      }
      
      generatingStory.value = true
      loading.value = true
      loadingMessage.value = t('loading.dancersWarmingUp')
      spinnerType.value = 'dance'
      
      try {
        const sessionId = localStorage.getItem('sessionId')
        console.log('📋 Session ID:', sessionId)
        
        // First save the painting selection
        console.log('💾 Saving selection...')
        const selectionData = {
          selectedPaintings: validPaintings,
          character: selectedCharacter.value,
          emotion: pageData.value.selectedEmotion,
          probability: pageData.value.selectedProbability,
          sessionId: sessionId
        }
        console.log('💾 Selection data:', selectionData)
        
        await ApiService.saveSelection(selectionData)
        console.log('✅ Selection saved successfully')
        
        // Create story generation job (backend will query database for selection details)
        console.log('📚 Creating story generation job...')
        
        const job = await ApiService.createJob({
          type: 'STORY_GENERATION',
          session_id: sessionId,
          input_data: {
            // Backend will enrich this with database data
            sessionId: sessionId
          }
        })
        
        const jobId = job.data.job_id
        console.log('✅ Job created:', jobId)
        
        // Poll for completion (max 2 minutes: 60 attempts x 2 seconds)
        console.log('⏳ Polling for story generation completion...')
        const result = await ApiService.pollJob(jobId, 60, 2000)
        
        console.log('✅ Story generation completed, result:', result)
        console.log('📖 Result type:', typeof result)
        console.log('📖 Result keys:', result ? Object.keys(result) : 'null')
        
        // Extract story with robust fallback handling
        let storyData = null
        
        // Handle various possible formats
        if (result && typeof result === 'object') {
          if (result.story) {
            // Format: { story: { title, paragraph_1, ... } }
            storyData = result.story
            console.log('✅ Extracted story from result.story')
          } else if (result.title && result.paragraph_1) {
            // Format: { title, paragraph_1, ... } (story object directly)
            storyData = result
            console.log('✅ Using result directly as story (has title and paragraphs)')
          } else {
            console.error('❌ Unexpected result format:', result)
            throw new Error('Story data has unexpected format')
          }
        } else if (typeof result === 'string') {
          // Handle case where result might be a JSON string
          try {
            const parsed = JSON.parse(result)
            storyData = parsed.story || parsed
            console.log('✅ Parsed story from string')
          } catch (e) {
            console.error('❌ Failed to parse result string:', e)
            throw new Error('Failed to parse story data')
          }
        } else {
          console.error('❌ Invalid result type:', typeof result, result)
          throw new Error('Story generation returned invalid data')
        }
        
        // Validate story has required fields
        if (!storyData || !storyData.title || !storyData.paragraph_1) {
          console.error('❌ Story missing required fields:', storyData)
          throw new Error('Story data is incomplete (missing title or paragraphs)')
        }
        
        console.log('✅ Story validated successfully:', {
          title: storyData.title,
          hasParagraph1: !!storyData.paragraph_1,
          hasParagraph2: !!storyData.paragraph_2,
          hasParagraph3: !!storyData.paragraph_3
        })
        
        // Navigate to StoryPage with result
        const storyPageData = {
          ...pageData.value,
          selectedPaintings: validPaintings,
          selectedCharacter: selectedCharacter.value,
          story: storyData,
          sessionId: sessionId
        }
        
        router.push({
          name: 'StoryPage',
          query: { data: unicodeSafeBase64Encode(JSON.stringify(storyPageData)) }
        })
        
      } catch (error) {
        console.error('❌ Error generating story:', error)
        console.error('❌ Error details:', error.message, error.stack)
        alert(`Failed to generate story: ${error.message}`)
      } finally {
        loading.value = false
        generatingStory.value = false
        spinnerType.value = 'magic-cube'
      }
    }
    
    // Lifecycle
    onMounted(() => {
      loadPageData()
      // Initialize selectedPaintings as array of nulls
      selectedPaintings.value = [null, null, null]
      // Initialize scroll handler after DOM is ready
      setTimeout(initializeScrollHandler, 100)
    })
    
    return {
      loading,
      loadingMessage,
      spinnerType,
      generatingStory,
      recommendations,
      allPaintings,
      showPrevious,
      previousCapturedUrl,
      previousEmotion,
      paintingsGrid,
      scrollPosition,
      scrollThumbPosition,
      scrollThumbWidth,
      selectedPaintings,
      selectedCharacter,
      hoveredCharacter,
      characters,
      step2Complete,
      step3Complete,
      step4Complete,
      showAllPaintings,
      showPaintingModal,
      selectedPaintingForModal,
      recaptureGallery,
      reloadRecommendations,
      remainingReloads,
      nextPaintings,
      prevPaintings,
      initializeScrollHandler,
      updateScrollPosition,
      isPaintingSelected,
      togglePaintingSelection,
      openPaintingModal,
      closePaintingModal,
      selectPainting,
      removePainting,
      selectCharacter,
      showCharacterDescription,
      hideCharacterDescription,
      handleImageError,
      generateStory
    }
  }
}
</script>

<style scoped>
.gallery-page {
  min-height: 100vh;
  background: #000000;
  padding: 20px;
  color: white;
}

.gallery-container {
  width: 100%;
  overflow: hidden;
  margin: 0 auto;
  padding: 40px;
}

.progress-indicator {
  display: none;
}

.selection-area {
  background-color: rgba(40, 40, 40, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 40px;
  border-radius: 30px;
  margin: 60px 0;
  text-align: center;
}

.selection-area h2 {
  display: none;
}

.instruction {
  font-family: 'Poppins', sans-serif;
  color: #ccc;
  margin-bottom: 20px;
  font-size: 16px;
  font-weight: 250;
  line-height: 1.5;
}

.step-label {
  font-size: 18px;
  font-weight: 600;
  color: white;
}

.step-label-text {
  font-size: 18px;
  font-weight: 400;
  color: white;
}

.sub-instruction {
  font-family: 'Poppins', sans-serif;
  color: #ccc;
  font-size: 16px;
  font-weight: 250;
  font-style: italic;
  text-align: center;
}

.top-row-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.previous-selection {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #ccc;
  font-family: 'Poppins', sans-serif;
  font-size: 16px;
  font-style: italic;
  position: relative;
}

.previous-icon {
  width: 40px;
  height: 40px;
}

.previous-icon-emoji {
  font-size: 22px;
}

.previous-popup {
  position: absolute;
  right: 0;
  top: 32px;
  width: min(560px, 80vw);
  background: rgba(0, 0, 0, 0.6);
  border: 1px solid rgba(255,255,255,0.2);
  backdrop-filter: blur(8px);
  border-radius: 10px;
  padding: 16px;
  z-index: 20;
}

.previous-title, .previous-emotion {
  color: #fff;
  font-family: 'Poppins', sans-serif;
  font-size: 18px;
  font-weight: 400;
}

.previous-image-wrapper {
  margin: 10px 0 12px 0;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid rgba(255,255,255,0.2);
}

.previous-image {
  width: 100%;
  height: 260px;
  object-fit: cover;
  display: block;
}

.emotion-highlight {
  font-style: italic;
}

.drop-zones {
  display: flex;
  justify-content: center;
  gap: 30px;
  flex-wrap: wrap;
}

.drop-zone {
  width: 200px;
  height: 200px;
  border: 2px dashed rgba(255, 255, 255, 0.4);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  position: relative;
  background: rgba(255, 255, 255, 0.05);
  margin-top: 20px;
}

.drop-zone:hover {
  border-color: rgba(255, 255, 255, 0.6);
}

.drop-zone.has-painting {
  border: 2px solid rgba(255, 255, 255, 0.6);
  background: transparent;
}

.selected-painting {
  position: relative;
  width: 100%;
  height: 100%;
}

.selected-painting img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 6px;
}

.remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 20px;
  height: 20px;
  background: #ff4444;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drop-placeholder {
  color: rgba(255, 255, 255, 0.6);
  font-family: 'Poppins', sans-serif;
  text-align: center;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drop-placeholder-image {
  max-width: 80%;
  max-height: 80%;
  object-fit: contain;
  opacity: 0.6;
}

.cursor-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
  vertical-align: middle;
  margin: 0 2px;
}

.gallery-section {

  margin-bottom: 40px;
}

.gallery-section h3 {
  font-family: 'Poppins', sans-serif;
  font-weight: 250;
  color: white;
  font-size: 40px;
  margin-bottom: 10px;
  text-align: center;
}

.gallery-subtitle {
  font-family: 'Poppins', sans-serif;
  color: #ccc;
  text-align: center;
  margin-bottom: 40px;
  font-size: 20px;
  font-weight: 300
}

.gallery-navigation-dock {
  position: relative;
  display: flex;
  justify-content: center;
  gap: 12px;
  padding: 10px 14px;
  background: rgba(20, 20, 20, 0.45);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 14px;
  backdrop-filter: blur(10px);
  margin: 10px auto 0;
}

.dock-nav-btn {
  background: rgba(255,255,255,0.15);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.25);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  user-select: none;
}

.dock-nav-btn:hover { background: rgba(255,255,255,0.25); }

.gallery-recapture {
  text-align: center;
  margin-top: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.recapture-text-left,
.recapture-text-right {
  font-family: 'Poppins', sans-serif;
  color: white;
  font-size: 16px;
  font-weight: 400;
}

.recapture-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 16px;
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.recapture-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

.reload-counter {
  padding: 2px 8px;
  margin-left: 8px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.2);
  color: inherit;
  font-weight: 600;
}
.reload-counter.zero {
  background: rgba(255, 80, 80, 0.2);
  color: #ff5050;
}

.paintings-grid-container {
  width: 100%;
  overflow: hidden;
  position: relative;
  margin: 20px 0;
}

.paintings-grid {
  display: flex;
  gap: 20px;
  padding: 20px 0;
  overflow-x: auto;
  overflow-y: hidden;
  scroll-behavior: smooth;
  /* Hide scrollbar */
  -ms-overflow-style: none;  /* Internet Explorer 10+ */
  scrollbar-width: none;  /* Firefox */
}

.paintings-grid::-webkit-scrollbar {
  display: none;  /* Safari and Chrome */
}

/* Integrated grid navigation buttons */
.grid-nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.25);
  background: rgba(20,20,20,0.45);
  color: #fff;
  font-size: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  backdrop-filter: blur(8px);
  z-index: 5;
  transition: background 0.2s ease, transform 0.2s ease;
}
.grid-nav-btn:hover { background: rgba(255,255,255,0.25); transform: translateY(-50%) scale(1.05); }
.grid-nav-left { left: 6px; }
.grid-nav-right { right: 6px; }

.scroll-bar-container {
  width: 100%;
  max-width: 800px;
  margin: 20px auto;
  padding: 0 20px;
}

.scroll-bar {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  position: relative;
  cursor: pointer;
  user-select: none;
}

.scroll-thumb {
  height: 4px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 2px;
  position: absolute;
  top: 0;
  transition: left 0.1s ease;
  cursor: pointer;
  touch-action: none; /* ensure pointer events deliver movement */
}

.scroll-thumb.dragging {
  background: rgba(255, 255, 255, 0.85);
}

.painting-item {
  width: 400px;
  height: 300px;
  border-radius: 15px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  flex-shrink: 0;
  border: 3px solid transparent;
}

.painting-item:hover {
  transform: translateY(-3px);
  border-color: rgba(255, 255, 255, 0.3);
}

.painting-item::before {
  content: attr(data-number);
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Poppins', sans-serif;
  font-weight: 200;
  font-size: 15px;
  z-index: 2;
}

.painting-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.painting-item img:hover {
  transform: scale(1.05);
}

/* Select/Unselect button on painting cards */
.painting-select-btn {
  position: absolute;
  bottom: 15px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(128, 128, 128, 0.8);
  color: white;
  border: none;
  border-radius: 20px;
  padding: 8px 20px;
  font-family: 'Poppins', sans-serif;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  z-index: 3;
  transition: all 0.3s ease;
  opacity: 0;
}

.painting-item:hover .painting-select-btn {
  opacity: 1;
}

.painting-select-btn:hover {
  background: rgba(150, 150, 150, 0.9);
  transform: translateX(-50%) translateY(-2px);
}

.painting-select-btn.selected {
  background: rgba(80, 80, 80, 0.9);
  opacity: 1;
}

.painting-select-btn.selected:hover {
  background: rgba(100, 100, 100, 0.95);
}

.painting-hover-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.9));
  color: white;
  opacity: 0;
  transition: opacity 0.3s ease;
  padding: 20px 15px 15px;
  z-index: 1;
}

.painting-item:hover .painting-hover-info {
  opacity: 1;
}

.hover-content h4 {
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  margin-bottom: 5px;
  color: white;
  font-size: 20px;
  line-height: 1.2;
}

.hover-content p {
  font-family: 'Poppins', sans-serif;
  color: rgba(255, 255, 255, 0.9);
  font-size: 15px;
  margin: 2px 0;
}

.character-section {
  background-color: rgba(40, 40, 40, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 40px;
  line-height: 1;
  border-radius: 30px;
  margin-bottom: 40px;
  text-align: center;
}

.character-section h3 {
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  color: white;
  font-size: 18px;
  text-align: center;
}

.character-subtitle {
  font-family: 'Poppins', sans-serif;
  color: #ffffff;
  text-align: center;
  font-size: 18px;
  font-weight: 400;
}

.hover-instruction {
  font-family: 'Poppins', sans-serif;
  color: #ccc;
  text-align: center;
  font-size: 16px;
  margin-bottom: 40px;
}

.character-cards {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.character-card {
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 25px;
  margin-top: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  position: relative;
  min-height: 200px;
  width: 200px;
}

.character-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.15);
}

.character-card.selected {
  border-color: #fffefe;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  box-shadow: 0 0 16px 4px rgba(255,255,255,0.7), 0 0 32px 8px rgba(255,255,255,0.3);
}

.character-card.selected::after {
  
  color: white;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.exit-btn{
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  background: #ff4444;
  border: 2px solid white;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.character-card img {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  object-fit: cover;
}

/* Character card text overlay */
.character-card-text {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  text-align: center;
  pointer-events: none;
  z-index: 2;
}

.character-title,
.character-description {
  font-family: 'Poppins', sans-serif;
  font-size: 14px;
  color: white;
  line-height: 1.4;
  word-wrap: break-word;
}

.character-card h4 {
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
  margin-bottom: 10px;
  color: white;
  font-size: 14px;
}

.character-description-hover {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 15px;
  border-radius: 0 0 12px 12px;
  z-index: 1000;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.character-description-hover p {
  font-family: 'Poppins', sans-serif;
  font-size: 13px;
  line-height: 1.4;
  margin: 0;
  color: white;
}

/* Painting Preview Modal */
.painting-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
  backdrop-filter: blur(5px);
}

.painting-modal {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  background: rgba(40, 40, 40, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: modalAppear 0.3s ease forwards;
  overflow: hidden;
}

.painting-modal-close {
  position: absolute;
  top: 15px;
  right: 15px;
  background: transparent;
  border: none;
  cursor: pointer;
  z-index: 3001;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.painting-modal-close:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.1);
}

.painting-modal-close img {
  width: 20px;
  height: 20px;
  object-fit: contain;
}

.painting-modal-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  overflow: hidden;
}

.painting-modal-image {
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  margin-bottom: 10px;
}

.painting-modal-image img {
  height: 600px;
  width: auto;
  max-width: 90vw;
  object-fit: contain;
  border-radius: 10px;
}

.check-source-link {
  font-family: 'Poppins', sans-serif;
  color: #9dd1ff;
  text-decoration: underline;
  text-underline-offset: 3px;
  text-decoration-thickness: 1.5px;
  cursor: pointer;
}
.check-source-link:hover {
  color: #cfe7ff;
  text-decoration-thickness: 2px;
}

.story-section {
  text-align: center;
}

.all-done-btn {
  background: #666;
  color: #999;
  border: none;
  padding: 15px 40px;
  font-size: 18px;
  font-weight: 400;
  font-family: 'Poppins', sans-serif;
  border-radius: 30px;
  cursor: not-allowed;
  transition: all 0.3s ease;
  margin-top: 40px;
}

.all-done-btn.interactive {
  background: #888;
  color: white;
  cursor: pointer;
}

.all-done-btn.interactive:hover:not(:disabled) {
  background: #999;
  transform: translateY(-2px);
}

.all-done-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

/* Global button focus disable */
button:focus {
  outline: none !important;
}

/* Responsive design */
@media (max-width: 768px) {
  .gallery-container {
    padding: 20px;
    margin: 10px;
  }
  
  .drop-zones {
    flex-direction: column;
    align-items: center;
  }
  
  .progress-indicator {
    flex-direction: column;
    align-items: center;
  }
  
  .character-cards {
    grid-template-columns: 1fr;
  }
  
  .paintings-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
  
  .generate-story-btn {
    padding: 15px 30px;
    font-size: 18px;
  }
  
  .painting-modal {
    max-width: 95vw;
    max-height: 95vh;
    padding: 15px;
  }
  
  .painting-modal-image img {
    height: 400px;
    max-width: 95vw;
  }
}
</style>
