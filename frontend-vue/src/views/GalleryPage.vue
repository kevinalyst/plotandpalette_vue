<template>
  <div class="gallery-page">
    <div class="gallery-container" v-if="allPaintings && allPaintings.length > 0">
      <!-- Step Progress Indicator -->
      <div class="progress-indicator">
        <div class="progress-step completed">1. Emotion Selected</div>
        <div :class="['progress-step', { completed: step2Complete }]">2. Choose 3 Paintings</div>
        <div :class="['progress-step', { completed: step3Complete }]">3. Select Character</div>
        <div :class="['progress-step', { completed: step4Complete }]">4. Create Story</div>
      </div>

      <!-- Painting Gallery -->
      <div class="gallery-section">
        <h3>Paintings for you</h3>
        <p class="gallery-subtitle">See the 10 paintings recommended from your captured colours</p>
        <p class="sub-instruction">These paintings are sourced from the WikiArt-Emotion Dataset.</p>
        
        <!-- Navigation controls for carousel view -->
        <div v-if="!showAllPaintings" class="gallery-navigation">
          <button @click="prevPaintings" class="nav-btn prev-btn">
            <img src="@/assets/images/left.png" alt="Previous" class="nav-btn-image" />
          </button>
          <button @click="nextPaintings" class="nav-btn next-btn">
            <img src="@/assets/images/right.png" alt="Next" class="nav-btn-image" />
          </button>
        </div>
        
        <div class="paintings-grid-container">
          <div class="paintings-grid" ref="paintingsGrid" v-if="allPaintings && allPaintings.length > 0">
            <div 
              v-for="(painting, index) in allPaintings" 
              :key="painting.url || index"
              class="painting-item"
              :data-number="index + 1"
              draggable="true"
              @dragstart="handleDragStart($event, painting)"
              @click="openPaintingModal(painting)"
            >
              <img :src="painting.url" :alt="painting.title" />
              <div class="painting-hover-info">
                <div class="hover-content">
                  <h4>{{ painting.title }}</h4>
                  <p>{{ painting.artist }}</p>
                  <p>{{ painting.year }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Horizontal scroll bar -->
        <div class="scroll-bar-container">
          <div class="scroll-bar" @click="handleScrollBarClick">
            <div class="scroll-thumb" ref="scrollThumb" :style="{ left: scrollThumbPosition + '%', width: scrollThumbWidth + '%' }"></div>
          </div>
        </div>
        
        <!-- Recapture Option -->
        <div class="gallery-recapture">
          <span class="recapture-text-left">I don't like any of these paintings. I want to</span>
          <button @click="recaptureGallery" class="recapture-btn">
            Re-capture
          </button>
          <span class="recapture-text-right">a palette.</span>
        </div>
      </div>

      <!-- Selected Paintings Drop Zone -->
      <div class="selection-area">
        <h2>Your Selected Paintings</h2>
        <p class="instruction">
          <span class="step-label">Step 3:</span> <br/>
          <span class="step-label-text">Which paintings spark your curiosity?</span> <br/>
          <span class="step-label-text">Pick three to craft a unique story...</span>
        </p>
        <p class="sub-instruction">Drag and drop paintings into the boxes</p>
        
        <div class="drop-zones">
          <div 
            v-for="i in 3" 
            :key="i"
            :class="['drop-zone', { 'has-painting': selectedPaintings[i-1] }]"
            @drop="handleDrop($event, i-1)"
            @dragover.prevent
            @dragenter.prevent
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
          <span class="step-label">Step 4:</span> <br/>
          <span class="step-label-text">Which character resonates with you?</span> <br/>
          <span class="step-label-text">Dive into their story...</span>
        </p>
        <p class="sub-instruction">Select the perspective that interests you the most</p>
                 <p class="sub-instruction">Hover your <img src="@/assets/images/cursor.png" alt="cursor" class="cursor-icon" /> over the cards to see each story's style</p>
        
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
            
          </div>
        </div>
      </div>

      <!-- Name Input Modal -->
      <div v-if="showNameInput" class="name-modal-overlay" @click="closeNameInput">
        <div class="name-modal" @click.stop>
          <h3>What shall we call your story's main character?</h3>
          <h3>Pick a name (different from your username)</h3>
          <input 
            v-model="nickname" 
            type="text" 
            placeholder="Enter a name..."
            class="name-input"
            maxlength="50"
            @keyup.enter="confirmName"
            ref="nameInputField"
          />
          <!-- <div class="name-modal-buttons">
            <button @click="closeNameInput" class="cancel-btn">Cancel</button>
            <button @click="confirmName" class="confirm-btn" :disabled="!nickname.trim()">Confirm</button>
          </div> -->
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
          {{ generatingStory ? 'Creating Your Story...' : 'All done!' }}
        </button>
      </div>
    </div>
    
    <LoadingSpinner :show="loading" :message="loadingMessage" :type="spinnerType" />
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
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
    const nickname = ref('')
    const hoveredCharacter = ref('')
    const showNameInput = ref(false)
    const showAllPaintings = ref(false)
    
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
      return step3Complete.value && nickname.value && nickname.value.trim().length > 0
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

    // Refs for scroll functionality
    const paintingsGrid = ref(null)
    const scrollThumb = ref(null)
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

    // Methods
    const loadPageData = () => {
      try {
        if (route.query.data) {
          const data = JSON.parse(unicodeSafeBase64Decode(route.query.data))
          pageData.value = data
          
          // Use detailedRecommendations from the backend which includes title, artist, year, url
          console.log('📊 Page data received:', data)
          console.log('🎨 DetailedRecommendations:', data.detailedRecommendations)
          console.log('🌐 Simple recommendations:', data.recommendations)
          
          if (data.detailedRecommendations && data.detailedRecommendations.length > 0) {
            allPaintings.value = data.detailedRecommendations
            recommendations.value = data.detailedRecommendations
            console.log('✅ Loaded paintings:', allPaintings.value.length)
          } else if (data.recommendations && data.recommendations.length > 0) {
            // Fallback: convert simple URL list to detailed format
            console.log('⚠️ Using fallback: converting URLs to painting objects')
            const paintingObjects = data.recommendations.map((url, index) => ({
              url: url,
              title: `Painting ${index + 1}`,
              artist: 'Unknown Artist', 
              year: 'Unknown Year'
            }))
            allPaintings.value = paintingObjects
            recommendations.value = paintingObjects
          } else {
            throw new Error('No painting recommendations received from backend')
          }
        } else {
          router.push('/')
        }
      } catch (error) {
        console.error('Error loading page data:', error)
        alert('Failed to load painting recommendations. Backend connection required.')
        router.push('/')
      }
    }

    const recaptureGallery = () => {
      router.push('/gradient')
    }

    const nextPaintings = () => {
      if (!paintingsGrid.value) return
      const scrollAmount = paintingsGrid.value.clientWidth * 0.8 // Scroll 80% of visible width
      const maxScroll = paintingsGrid.value.scrollWidth - paintingsGrid.value.clientWidth
      const newScrollPosition = Math.min(scrollPosition.value + scrollAmount, maxScroll)
      
      paintingsGrid.value.scrollTo({
        left: newScrollPosition,
        behavior: 'smooth'
      })
    }

    const prevPaintings = () => {
      if (!paintingsGrid.value) return
      const scrollAmount = paintingsGrid.value.clientWidth * 0.8 // Scroll 80% of visible width
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
    
    const handleScrollBarClick = (event) => {
      if (!paintingsGrid.value) return
      const scrollBar = event.currentTarget
      const rect = scrollBar.getBoundingClientRect()
      const clickX = event.clientX - rect.left
      const scrollBarWidth = rect.width
      const maxScroll = paintingsGrid.value.scrollWidth - paintingsGrid.value.clientWidth
      
      const targetScrollPosition = (clickX / scrollBarWidth) * maxScroll
      paintingsGrid.value.scrollTo({
        left: targetScrollPosition,
        behavior: 'smooth'
      })
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
      if (painting && painting.url) {
        selectedPaintingForModal.value = {
          url: painting.url,
          title: painting.title,
          artist: painting.artist,
          year: painting.year
        }
        showPaintingModal.value = true
      }
    }

    const closePaintingModal = () => {
      showPaintingModal.value = false
      selectedPaintingForModal.value = {}
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
      // Show name input modal when character is selected
      showNameInput.value = true
      // Focus name input after modal is shown
      setTimeout(() => {
        if (document.querySelector('.name-input')) {
          document.querySelector('.name-input').focus()
        }
      }, 100)
    }

    const showCharacterDescription = (characterId) => {
      hoveredCharacter.value = characterId
    }

    const hideCharacterDescription = () => {
      hoveredCharacter.value = ''
    }

    const closeNameInput = () => {
      showNameInput.value = false
      // Reset character selection if no name was entered
      if (!nickname.value.trim()) {
        selectedCharacter.value = ''
      }
    }

    const confirmName = () => {
      if (nickname.value.trim()) {
        showNameInput.value = false
      }
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
        console.log('- Nickname:', nickname.value)
        console.log('- Page data:', pageData.value)
      
      // Validate required data before making API calls
      const validPaintings = selectedPaintings.value.filter(p => p && p.url && p.title && p.artist && p.year)
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
      
              if (!nickname.value || !nickname.value.trim()) {
          alert('Error: Please enter a nickname for your story')
          return
        }
      
      generatingStory.value = true
      loading.value = true
      loadingMessage.value = 'Matisse\'s dancers are warming up!'
      spinnerType.value = 'dance'
      
      try {
        const sessionId = localStorage.getItem('sessionId')
        console.log('📋 Session ID:', sessionId)
        
        // First save the painting selection
        console.log('💾 Saving selection...')
        const selectionData = {
          selectedPaintings: validPaintings,
          character: selectedCharacter.value,
          nickname: nickname.value,
          emotion: pageData.value.selectedEmotion,
          probability: pageData.value.selectedProbability,
          sessionId: sessionId
        }
        console.log('💾 Selection data:', selectionData)
        
        await ApiService.saveSelection(selectionData)
        console.log('✅ Selection saved successfully')
        
        // Then generate the story
        console.log('📚 Generating story...')
        
        // Debug emotion data
        console.log('📚 Debug - pageData.value:', pageData.value)
        console.log('📚 Debug - selectedEmotion:', pageData.value.selectedEmotion)
        console.log('📚 Debug - selectedProbability:', pageData.value.selectedProbability)
        
        const storyData = {
          paintings: validPaintings,
          character: selectedCharacter.value,
          nickname: nickname.value,
          emotion: pageData.value.selectedEmotion || '',
          probability: pageData.value.selectedProbability || 0,
          sessionId: sessionId
        }
        console.log('📚 Story request data:', storyData)
        console.log('📚 Story request emotion debug:', {
          emotion: storyData.emotion,
          probability: storyData.probability,
          emotionType: typeof storyData.emotion,
          probabilityType: typeof storyData.probability
        })
        
        const storyResponse = await ApiService.generateStory(storyData)
        console.log('✅ Story generated successfully:', storyResponse)
        
        const storyPageData = {
          ...pageData.value,
          selectedPaintings: validPaintings,
          selectedCharacter: selectedCharacter.value,
          userName: nickname.value,
          story: storyResponse,
          sessionId: sessionId
        }
        
        router.push({
          name: 'StoryPage',
          query: { data: unicodeSafeBase64Encode(JSON.stringify(storyPageData)) }
        })
        
      } catch (error) {
        console.error('❌ Error generating story:', error)
        console.error('❌ Error details:', error.message, error.stack)
        loading.value = false
        generatingStory.value = false
        spinnerType.value = 'magic-cube'
        alert(`Failed to generate story: ${error.message}`)
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
      paintingsGrid,
      scrollThumb,
      scrollPosition,
      scrollThumbPosition,
      scrollThumbWidth,
      selectedPaintings,
      selectedCharacter,
      nickname,
      hoveredCharacter,
      showNameInput,
      characters,
      step2Complete,
      step3Complete,
      step4Complete,
      showAllPaintings,
      showPaintingModal,
      selectedPaintingForModal,
      recaptureGallery,
      nextPaintings,
      prevPaintings,
      initializeScrollHandler,
      updateScrollPosition,
      handleScrollBarClick,
      handleDragStart,
      handleDrop,
      openPaintingModal,
      closePaintingModal,
      selectPainting,
      removePainting,
      selectCharacter,
      showCharacterDescription,
      hideCharacterDescription,
      closeNameInput,
      confirmName,
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
  /* max-width: 1400px; */

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

.gallery-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  margin-bottom: 20px;
}

.nav-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  outline: none;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.nav-btn:focus {
  outline: none;
}

.nav-btn:active {
  outline: none;
  transform: scale(0.95);
}

.prev-btn {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
}

.next-btn {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
}

.nav-btn-image {
  width: 100%;
  height: 100%;
  object-fit: fill;
}

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
}

.scroll-thumb {
  height: 4px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 2px;
  position: absolute;
  top: 0;
  transition: left 0.1s ease;
  cursor: pointer;
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

/* Name Input Modal */
.name-modal-overlay {
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(40, 40, 40, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(5px);
  line-height: 1.5;
}

.name-modal {
  
  padding: 40px;
  
  width: 100%;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  transform: scale(0.9);
  animation: modalAppear 0.3s ease forwards;
}

@keyframes modalAppear {
  to {
    transform: scale(1);
  }
}

.name-modal h3 {
  font-family: 'Poppins', sans-serif;
  font-weight: 400;
  color: white;
  font-size: 18px;
}

.name-subtitle {
  font-family: 'Poppins', sans-serif;
  color: #ccc;
  margin-bottom: 15px;
  font-style: italic;
  font-weight: 250;
}

.name-instruction {
  font-family: 'Poppins', sans-serif;
  color: #ccc;
  margin-bottom: 30px;
  font-size: 14px;
}

.name-input {
  width: 100%;
  padding: 15px 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 25px;
  font-family: 'Poppins', sans-serif;
  font-size: 16px;
  text-align: center;
  margin-bottom: 30px;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  margin-top: 20px;
}

.name-input:focus {
  border-color: rgba(255, 255, 255, 0.6);
  outline: none;
  background: rgba(255, 255, 255, 0.15);
}

.name-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.name-modal-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.cancel-btn, .confirm-btn {
  padding: 12px 25px;
  border-radius: 25px;
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #ccc;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
}

.confirm-btn {
  background: rgba(255, 255, 255, 0.9);
  color: #333;
}

.confirm-btn:hover:not(:disabled) {
  background: white;
  transform: translateY(-2px);
}

.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
}

.painting-modal-image img {
  height: 600px;
  width: auto;
  max-width: 90vw;
  object-fit: contain;
  border-radius: 10px;
}

.name-section {
  margin-bottom: 40px;
  text-align: center;
}

.name-section h3 {
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.name-input {
  padding: 15px 20px;
  border: 2px solid #e9ecef;
  border-radius: 25px;
  font-family: 'Poppins', sans-serif;
  font-size: 16px;
  text-align: center;
  width: 300px;
  max-width: 100%;
  transition: border-color 0.3s ease;
}

.name-input:focus {
  /* border-color: #4ecdc4; */
  outline: none;
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