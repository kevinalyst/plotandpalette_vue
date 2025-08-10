<template>
  <div class="story-page">
    <!-- Story Title Section -->
    <div class="storytittle">
      <h1>{{ storyData.story?.story_title || 'Your Story' }}</h1>
    </div>
    
    <div class="story-container">
      <!-- Previous selection (same interaction/style as GalleryPage) -->
      <div class="top-row-info">
        <div 
          class="previous-selection"
          @mouseenter="showPrevious = true"
          @mouseleave="showPrevious = false"
        >
          <span>Hover to see your previous selection:</span>
          <img src="@/assets/images/hoverpalette.png" alt="Previous selection" class="previous-icon" />
          <div v-if="showPrevious" class="previous-popup">
            <div class="previous-title">Your captured palette:</div>
            <div class="previous-image-wrapper">
              <img :src="previousCapturedUrl" alt="captured palette" class="previous-image" />
            </div>
            <div class="previous-emotion">Your selected emotion: <span class="emotion-highlight">{{ previousEmotion || '—' }}</span></div>
          </div>
        </div>
      </div>
      <!-- Story Sequence with Paintings and Corresponding Story Parts -->
      <div class="story-sequence">
        
        <!-- Painting 1 and Story Part 1 -->
        <div class="painting-story-section" v-if="storyData.selectedPaintings && storyData.selectedPaintings[0]">
          <div class="painting-display">
            <img :src="getProxiedImageUrl(storyData.selectedPaintings[0]?.url || storyData.selectedPaintings[0]?.originalUrl)"
                 :alt="storyData.selectedPaintings[0]?.title"
                 @click="openPaintingModal(storyData.selectedPaintings[0])" />
            <div class="painting-info">
              <h3>{{ storyData.selectedPaintings[0]?.title }}</h3>
              <p>{{ storyData.selectedPaintings[0]?.artist }}, {{ storyData.selectedPaintings[0]?.year }}</p>
            </div>
          </div>
          <div class="story-text-section">
            <div class="story-text">
              {{ storyData.story?.story_part_1 || 'Story part 1 will appear here...' }}
            </div>
          </div>
        </div>

        <!-- Painting 2 and Story Part 2 -->
        <div class="painting-story-section" v-if="storyData.selectedPaintings && storyData.selectedPaintings[1]">
          <div class="painting-display">
            <img :src="getProxiedImageUrl(storyData.selectedPaintings[1]?.url || storyData.selectedPaintings[1]?.originalUrl)"
                 :alt="storyData.selectedPaintings[1]?.title"
                 @click="openPaintingModal(storyData.selectedPaintings[1])" />
            <div class="painting-info">
              <h3>{{ storyData.selectedPaintings[1]?.title }}</h3>
              <p>{{ storyData.selectedPaintings[1]?.artist }}, {{ storyData.selectedPaintings[1]?.year }}</p>
            </div>
          </div>
          <div class="story-text-section">
            <div class="story-text">
              {{ storyData.story?.story_part_2 || 'Story part 2 will appear here...' }}
            </div>
          </div>
        </div>

        <!-- Painting 3 and Story Part 3 -->
        <div class="painting-story-section" v-if="storyData.selectedPaintings && storyData.selectedPaintings[2]">
          <div class="painting-display">
            <img :src="getProxiedImageUrl(storyData.selectedPaintings[2]?.url || storyData.selectedPaintings[2]?.originalUrl)"
                 :alt="storyData.selectedPaintings[2]?.title"
                 @click="openPaintingModal(storyData.selectedPaintings[2])" />
            <div class="painting-info">
              <h3>{{ storyData.selectedPaintings[2]?.title }}</h3>
              <p>{{ storyData.selectedPaintings[2]?.artist }}, {{ storyData.selectedPaintings[2]?.year }}</p>
            </div>
          </div>
          <div class="story-text-section">
            <div class="story-text">
              {{ storyData.story?.story_part_3 || 'Story part 3 will appear here...' }}
            </div>
          </div>
        </div>

      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <button @click="downloadStory" class="action-btn download-btn">
          Download my story
        </button>
        <button @click="regenerateStory" class="action-btn secondary-btn">
          Re-generate story
        </button>
        <button @click="recapturepalette" class="action-btn secondary-btn">
          Re-capture palette
        </button>
        <button @click="leaveFeedback" class="action-btn feedback-btn">
          Leave us feedback!
          <img src="@/assets/images/heart.png" alt="heart" class="feedback-heart-icon" />
        </button>
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
              >See the original source</a>
            </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'StoryPage',
  components: {
    
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    // Reactive data
    const loading = ref(false)
    const loadingMessage = ref('')
    
    // Story data
    const storyData = ref({})
    
    // Previous selection hover state (aligned with GalleryPage)
    const showPrevious = ref(false)
    const previousCapturedUrl = ref('')
    const previousEmotion = ref('')
    
    // Helper to proxy external images (aligned with GalleryPage)
    const getProxiedImageUrl = (originalUrl) => {
      if (!originalUrl) return ''
      if (originalUrl.startsWith('/api/proxy-image')) return originalUrl
      return `/api/proxy-image?url=${encodeURIComponent(originalUrl)}`
    }
    
    // Painting modal state
    const showPaintingModal = ref(false)
    const selectedPaintingForModal = ref({})

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
          storyData.value = data
          // Prepare previous selection display (align with GalleryPage)
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
          
        } else {
          router.push('/')
        }
      } catch (error) {
        console.error('Error loading story data:', error)
        router.push('/')
      }
    }



    const downloadStory = async () => {
      try {
        loading.value = true
        loadingMessage.value = 'Preparing your story download...'

        // Import html2canvas dynamically
        const html2canvas = await import('html2canvas')
        
        // Get elements
        const storytitle = document.querySelector('.storytittle')
        const storyContainer = document.querySelector('.story-container')
        const actionButtons = document.querySelector('.action-buttons')
        
        if (!storytitle || !storyContainer) {
          throw new Error('Required story elements not found')
        }

        // Temporarily hide action buttons
        if (actionButtons) {
          actionButtons.style.display = 'none'
        }

        // Create a temporary container that includes both storytitle and story content
        const tempContainer = document.createElement('div')
        tempContainer.style.position = 'absolute'
        tempContainer.style.top = '0'
        tempContainer.style.left = '0'
        tempContainer.style.width = '100%'
        tempContainer.style.background = '#000000'
        tempContainer.style.zIndex = '-1000'
        
        // Clone and append storytitle
        const storytitleClone = storytitle.cloneNode(true)
        storytitleClone.style.position = 'relative'
        storytitleClone.style.top = 'auto'
        storytitleClone.style.left = 'auto'
        storytitleClone.style.width = '100%'
        tempContainer.appendChild(storytitleClone)
        
        // Clone and append story content (without action buttons)
        const contentClone = storyContainer.cloneNode(true)
        contentClone.style.marginTop = '20px' // Reduce spacing since storytitle is now relative
        
        // Remove action buttons from the clone if they exist
        const clonedActionButtons = contentClone.querySelector('.action-buttons')
        if (clonedActionButtons) {
          clonedActionButtons.remove()
        }
        
        tempContainer.appendChild(contentClone)
        document.body.appendChild(tempContainer)

        // Generate canvas from the temporary container
        const canvas = await html2canvas.default(tempContainer, {
          backgroundColor: '#000000',
          useCORS: true,
          allowTaint: true,
          scale: 2, // Higher quality
          scrollX: 0,
          scrollY: 0,
          width: tempContainer.scrollWidth,
          height: tempContainer.scrollHeight
        })

        // Clean up
        document.body.removeChild(tempContainer)
        
        // Restore action buttons
        if (actionButtons) {
          actionButtons.style.display = 'flex'
        }

        // Convert canvas to blob and download
        canvas.toBlob((blob) => {
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `my-story-${Date.now()}.jpeg`
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          URL.revokeObjectURL(url)
          loading.value = false
        }, 'image/jpeg', 0.9)
      } catch (error) {
        console.error('Error downloading story:', error)
        loading.value = false
        
        // Ensure action buttons are restored even if there's an error
        const actionButtons = document.querySelector('.action-buttons')
        if (actionButtons) {
          actionButtons.style.display = 'flex'
        }
        
        alert('Failed to download story. Please try again.')
      }
    }

    const recapturepalette = () => {
      // Go back to gradient palette page
      router.push({ name: 'GradientPalette' })
    }

    const leaveFeedback = () => {
      // Navigate to feedback questionnaire page
      router.push({ name: 'FeedbackPage' })
    }

    const openPaintingModal = (painting) => {
      selectedPaintingForModal.value = painting
      showPaintingModal.value = true
    }

    const closePaintingModal = () => {
      showPaintingModal.value = false
      selectedPaintingForModal.value = {}
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

    const regenerateStory = () => {
      // Reset selections and go back to gallery page
      const galleryData = {
        ...storyData.value,
        selectedPaintings: [null, null, null],
        selectedCharacter: null,
        userName: storyData.value.userName,
        sessionId: storyData.value.sessionId
      }
      
      router.push({
        name: 'GalleryPage',
        query: { data: unicodeSafeBase64Encode(JSON.stringify(galleryData)) }
      })
    }
    
    // Lifecycle
    onMounted(async () => {
      // Ensure scroll to top with multiple methods for reliability
      const scrollToTop = () => {
        // Method 1: Standard window scroll
        window.scrollTo({
          top: 0,
          left: 0,
          behavior: 'instant'
        })
        
        // Method 2: Document element scroll (fallback)
        if (document.documentElement) {
          document.documentElement.scrollTop = 0
        }
        
        // Method 3: Body scroll (additional fallback)
        if (document.body) {
          document.body.scrollTop = 0
        }
      }
      
      // Immediate scroll
      scrollToTop()
      
      // Wait for DOM to be fully rendered, then scroll again
      await nextTick()
      scrollToTop()
      
      // Additional scroll after a small delay to ensure it takes effect
      setTimeout(scrollToTop, 50)
      
      loadPageData()
    })
    
    return {
      loading,
      loadingMessage,
      storyData,
      showPrevious,
      previousCapturedUrl,
      previousEmotion,
      getProxiedImageUrl,
      downloadStory,
      regenerateStory,
      recapturepalette,
      leaveFeedback,
      showPaintingModal,
      selectedPaintingForModal,
      openPaintingModal,
      closePaintingModal
    }
  }
}
</script>

<style scoped>
/* Ensure page starts at top */
html, body {
  scroll-behavior: auto !important;
}

.story-page {
  min-height: 100vh;
  background: #000000;
  padding: 0;
  color: white;
  position: relative;
}

.storytittle {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  background: #000000;
  z-index: 1000;
  padding: 20px 0;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.storytittle h1 {
  font-family: 'Poppins', sans-serif;
  font-size: 40px;
  font-weight: 250;
  color: white;
  margin: 0;
}

.story-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 40px;
  margin-top: 100px; /* Account for fixed storytittle section */
}

.story-sequence {
  display: flex;
  flex-direction: column;
  gap: 80px;
}

.painting-story-section {
  display: flex;
  gap: 40px;
  align-items: flex-start;
  flex-wrap: wrap;
  padding: 40px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.painting-story-section:last-child {
  border-bottom: none;
}

.painting-display {
  text-align: center;
  max-width: 350px;
  width: 100%;
  flex-shrink: 0;
}

.painting-display img {
  width: 100%;
  max-height: 350px;
  object-fit: contain;
  border-radius: 15px;
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.painting-display img:hover {
  transform: scale(1.02);
}

.painting-info {
  text-align: center;
  margin-bottom: 20px;
}

.painting-info h3 {
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  color: white;
  font-size: 24px;
  margin-bottom: 10px;
}

.painting-info p {
  font-family: 'Poppins', sans-serif;
  color: #ccc;
  font-size: 16px;
  font-style: italic;
}

.story-text-section {
  flex: 1;
  min-width: 300px; /* Ensure text section has a minimum width */
}

.story-text {
  font-family: 'Poppins', sans-serif;
  font-size: 18px;
  line-height: 1.8;
  color: white;
  text-align: left;
  white-space: pre-line;
  margin-bottom: 30px;
}

.fallback-story p {
  font-family: 'Poppins', sans-serif;
  font-size: 18px;
  line-height: 1.8;
  color: #ccc;
  text-align: center;
  font-style: italic;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 80px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 15px 30px;
  border: none;
  border-radius: 50px;
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 180px;
  text-align: center;
}

.download-btn {
  background: #28a745;
  color: white;
}

.download-btn:hover {
  background: #218838;
  transform: translateY(-2px);
}

.secondary-btn {
  background: #6c757d;
  color: white;
  border: 2px solid transparent;
}

.secondary-btn:hover {
  background: #5a6268;
  transform: translateY(-2px);
}

.feedback-btn {
  background: #8b7d8b;
  color: white;
  border: 2px solid #a8849a;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.feedback-btn:hover {
  background: #9d8a9d;
  border-color: #b8949a;
  transform: translateY(-2px);
}

.feedback-heart-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
  opacity: 0.9;
}

/* Global button focus disable */
button:focus {
  outline: none !important;
}

/* Painting Modal Styles */
.painting-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000; /* Ensure it's above all other content */
}

.painting-modal {
  background: #1a1a1a;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  max-width: 800px;
  width: 90%;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  overflow: hidden;
  padding: 20px;
}

.painting-modal-close {
  position: absolute;
  top: 20px;
  right: 20px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 10px;
  z-index: 10;
  transition: all 0.3s ease;
}

.painting-modal-close:hover {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  transform: scale(1.1);
}

.painting-modal-close img {
  width: 30px;
  height: 30px;
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
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.painting-modal-image img {
  height: 600px;
  width: auto;
  max-width: 90vw;
  object-fit: contain;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

/* Responsive design */
@media (max-width: 768px) {
  .storytittle {
    padding: 15px 0;
  }
  
  .storytittle h1 {
    font-size: 28px;
  }
  
  .story-container {
    padding: 40px 20px;
    margin-top: 75px; /* Adjusted for smaller storytittle on mobile */
  }
  
  .story-sequence {
    gap: 40px;
  }

  .painting-story-section {
    flex-direction: column;
    align-items: center;
    gap: 30px;
    padding: 30px 0;
  }
  
  .painting-display {
    max-width: 280px;
  }
  
  .painting-info h3 {
    font-size: 20px;
  }
  
  .painting-info p {
    font-size: 14px;
  }
  
  .story-text-section {
    width: 100%;
  }
  
  .story-text {
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: 25px;
  }

  .action-buttons {
    flex-direction: column;
    align-items: center;
    gap: 15px;
  }

  .action-btn {
    width: 100%;
    max-width: 280px;
  }

  .painting-modal {
    width: 95%;
    max-height: 90%;
    padding: 15px;
  }

  .painting-modal-image img {
    height: 400px;
    max-width: 95vw;
  }
}
</style> 