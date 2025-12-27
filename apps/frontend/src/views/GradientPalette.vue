<template>
  <div class="gradient-container">
    <img 
      ref="animatedGif"
      :src="currentGifSrc" 
      class="animated-gif-element" 
      :key="currentGifSrc"
      :style="{ display: gifVisible ? 'block' : 'none' }"
      crossorigin="anonymous"
      alt="Animated Palette"
    />
    
    <!-- Thumbnail Gallery (Dock-like) -->
    <div class="palette-gallery">
      <button class="gallery-nav left" @click="scrollGallery('left')">‹</button>
      <div class="thumbnails" ref="thumbnailScroller">
        <img
          v-for="(thumb, idx) in allThumbnails"
          :key="idx"
          :src="thumb"
          class="thumbnail"
          :class="{ active: idx === selectedIndex }"
          @click="selectGif(idx)"
          loading="lazy"
          decoding="async"
          alt="palette thumbnail"
        />
        <!-- Upload tile as the last item in the scroller -->
        <label class="thumbnail upload-tile">
          <input
            type="file"
            accept="image/png,image/jpeg"
            @change="handleFileUpload"
          />
          <img v-if="!isUploading" :src="dropIcon" alt="Upload palette" class="upload-icon" />
          <span class="upload-label" v-else>Uploading...</span>
        </label>
      </div>
      <button class="gallery-nav right" @click="scrollGallery('right')">›</button>
    </div>

    <div 
      :class="['capture-prompt', { 'animate-fade': animatePrompt, 'hidden': !showCapturePrompt }]"
    >
      <div class="prompt-text">
        <div><span class="prompt-step">{{ $t('gradient.step1') }}</span> <p>{{ $t('gradient.promptQuestion') }}</p></div>
        <p>{{ $t('gradient.promptInstruction') }}</p>
      </div>
    </div>
    
    <div class="controls">
      <button 
        class="stop-button" 
        @click="capturePalette"
        :disabled="isCapturing"
      >
        {{ isCapturing ? $t('gradient.capturing') : $t('gradient.capture') }}
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
import { ref, reactive, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import Modal from '@/components/Modal.vue'
import ApiService from '@/services/api.js'
import html2canvas from 'html2canvas'
import dropIcon from '@/assets/images/upload.png'
// Removed random cycling; we provide a simple clickable gallery instead

// Statically import preview JPGs so they are always available and fast
import preview1 from '@/assets/images/palette GIF/palette_preview/1.jpg'
import preview2 from '@/assets/images/palette GIF/palette_preview/2.jpg'
import preview3 from '@/assets/images/palette GIF/palette_preview/3.jpg'
import preview4 from '@/assets/images/palette GIF/palette_preview/4.jpg'
import preview5 from '@/assets/images/palette GIF/palette_preview/5.jpg'
import preview6 from '@/assets/images/palette GIF/palette_preview/6.jpg'
import preview7 from '@/assets/images/palette GIF/palette_preview/7.jpg'
import preview8 from '@/assets/images/palette GIF/palette_preview/8.jpg'
import preview9 from '@/assets/images/palette GIF/palette_preview/9.jpg'
import preview10 from '@/assets/images/palette GIF/palette_preview/10.jpg'
import preview11 from '@/assets/images/palette GIF/palette_preview/11.jpg'
import preview12 from '@/assets/images/palette GIF/palette_preview/12.jpg'
import preview13 from '@/assets/images/palette GIF/palette_preview/13.jpg'
import preview14 from '@/assets/images/palette GIF/palette_preview/14.jpg'
import preview15 from '@/assets/images/palette GIF/palette_preview/15.jpg'
import preview16 from '@/assets/images/palette GIF/palette_preview/16.jpg'
import preview17 from '@/assets/images/palette GIF/palette_preview/17.jpg'
import preview18 from '@/assets/images/palette GIF/palette_preview/18.jpg'
import preview19 from '@/assets/images/palette GIF/palette_preview/19.jpg'
import preview20 from '@/assets/images/palette GIF/palette_preview/20.jpg'

export default {
  name: 'GradientPalette',
  components: {
    LoadingSpinner,
    Modal
  },
  setup() {
    const router = useRouter()
    const { t } = useI18n()
    
    // Reactive data
    const currentGifSrc = ref('')
    const gifVisible = ref(false)
    const showCapturePrompt = ref(false)
    const animatePrompt = ref(false)
    const isCapturing = ref(false)
    const showModal = ref(false)
    const showLoading = ref(false)
    const loadingMessage = ref(t('gradient.loadingMessage'))
    
    // Modal data
    const modalTitle = ref('')
    const modalMessage = ref('')
    const modalButtons = ref([])
    
    // Gallery GIFs
    const galleryGifs = ref(Array(20).fill(null))
    const thumbnailSrcs = ref([
      preview1, preview2, preview3, preview4, preview5,
      preview6, preview7, preview8, preview9, preview10,
      preview11, preview12, preview13, preview14, preview15,
      preview16, preview17, preview18, preview19, preview20
    ])
    const selectedIndex = ref(0)
    const thumbnailScroller = ref(null)
    const uploadedItems = ref([]) // { thumbUrl, displayUrl, filename }
    const isUploading = ref(false)
    
    // Static icon for upload tile
    

    const allThumbnails = computed(() => [
      ...thumbnailSrcs.value,
      ...uploadedItems.value.map(u => u.thumbUrl)
    ])
    
    // Animation properties
    const animationTimeout = ref(null)
    
    // GIF element reference for frame capture
    const animatedGif = ref(null)
    
    // Load 20 GIFs from R2 via API endpoint
    const gifLoaders = Array.from({ length: 20 }, (_, i) => () => {
      if (!galleryGifs.value[i]) {
        // Use R2 bucket URLs via our API endpoint
        galleryGifs.value[i] = `/api/assets/palettes/${i + 1}.gif`
      }
      return galleryGifs.value[i]
    })

    const loadGifs = async () => {
      try {
        // Load only the first GIF initially
        const firstUrl = await gifLoaders[0]()
        selectedIndex.value = 0
        currentGifSrc.value = firstUrl
        gifVisible.value = true
      } catch (e) {
        console.error('Failed to load initial GIF:', e)
      }
    }
    
    // Methods
    const selectGif = async (index) => {
      const baseCount = thumbnailSrcs.value.length
      const total = baseCount + uploadedItems.value.length
      if (index < 0 || index >= total) return
      selectedIndex.value = index

      if (index < baseCount) {
        // Built-in GIFs
        const next = await gifLoaders[index]()
        if (currentGifSrc.value !== next) {
          currentGifSrc.value = next
        } else {
          currentGifSrc.value = `${next}?t=${Date.now()}`
        }
      } else {
        // User-uploaded static image
        const uIndex = index - baseCount
        const item = uploadedItems.value[uIndex]
        if (item) {
          currentGifSrc.value = item.displayUrl
        }
      }
    }

    const scrollGallery = (direction) => {
      const scroller = thumbnailScroller.value
      if (!scroller) return
      const amount = Math.round(scroller.clientWidth * 0.8)
      scroller.scrollBy({ left: direction === 'left' ? -amount : amount, behavior: 'smooth' })
    }

    const handleFileUpload = async (event) => {
      try {
        const file = event.target.files && event.target.files[0]
        if (!file) return
        // Validate type
        const valid = ['image/png', 'image/jpeg']
        if (!valid.includes(file.type)) {
          showModal.value = true
          modalTitle.value = 'Invalid file type'
          modalMessage.value = 'Please upload a PNG or JPEG image.'
          modalButtons.value = [{ text: 'OK', action: () => { showModal.value = false } }]
          return
        }
        // Optional: size guard (<=10MB)
        if (file.size > 10 * 1024 * 1024) {
          showModal.value = true
          modalTitle.value = 'File too large'
          modalMessage.value = 'Please upload an image up to 10 MB.'
          modalButtons.value = [{ text: 'OK', action: () => { showModal.value = false } }]
          return
        }

        isUploading.value = true

        const form = new FormData()
        form.append('image', file)

        const resp = await ApiService.savePalette(form)
        // Prefer proxied URL for same-origin loading in dev/prod
        const filename = resp && (resp.filename || (resp.metadata && resp.metadata.filename))
        let displayUrl = resp && resp.url
        if (filename) {
          displayUrl = `/api/uploads/${filename}`
        }

        // Use returned URL for thumbnail; fallback to object URL
        const objectUrl = URL.createObjectURL(file)
        const thumbUrl = objectUrl || displayUrl

        uploadedItems.value.push({ thumbUrl, displayUrl, filename })

        // Select the newly uploaded item
        const baseCount = thumbnailSrcs.value.length
        selectedIndex.value = baseCount + uploadedItems.value.length - 1
        currentGifSrc.value = displayUrl
        gifVisible.value = true

        // Clear the file input so the same file can be re-selected if desired
        if (event.target) event.target.value = ''
      } catch (e) {
        console.error('Upload failed', e)
        showModal.value = true
        modalTitle.value = 'Upload failed'
        modalMessage.value = e && e.message ? e.message : 'Unable to upload image.'
        modalButtons.value = [{ text: 'OK', action: () => { showModal.value = false } }]
      } finally {
        isUploading.value = false
      }
    }

    // Generate tiny SVG data URI placeholders so thumbnails are instant and light
    const generateGradientPlaceholder = (index) => {
      const hueA = (index * 37) % 360
      const hueB = (hueA + 140) % 360
      const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='160' height='90'>` +
                  `<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>` +
                  `<stop offset='0%' stop-color='hsl(${hueA},70%,55%)'/>` +
                  `<stop offset='100%' stop-color='hsl(${hueB},70%,40%)'/></linearGradient></defs>` +
                  `<rect width='100%' height='100%' fill='url(#g)'/></svg>`
      return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`
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
          console.log('📸 Starting clean page capture with html2canvas...')
          console.log('🎯 Current GIF being displayed:', currentGifSrc.value)
          
          // Use html2canvas to capture the entire page with optimized settings
          html2canvas(document.body, {
            useCORS: true,
            allowTaint: true,
            backgroundColor: '#000000',
            width: window.innerWidth,
            height: window.innerHeight,
            scrollX: 0,
            scrollY: 0,
            scale: 1,
            logging: false, // Disable logging for cleaner capture
            removeContainer: true, // Remove html2canvas container after capture
            ignoreElements: function(element) {
              // Ignore any remaining UI elements that might interfere
              return element.classList.contains('loading-spinner') ||
                     element.classList.contains('modal') ||
                     element.classList.contains('capture-prompt') ||
                     element.classList.contains('controls') ||
                     element.classList.contains('palette-gallery')
            }
          }).then(canvas => {
            try {
              // Convert to base64 data URL with high quality
              const frameData = canvas.toDataURL('image/png', 0.95)
              
              console.log('🖼️ Clean page captured successfully:', {
                gifDisplayed: currentGifSrc.value,
                canvasWidth: canvas.width,
                canvasHeight: canvas.height,
                dataLength: frameData.length,
                hasImageData: frameData.length > 1000 // Basic check for non-empty image
              })
              
              resolve(frameData)
            } catch (error) {
              console.error('❌ Error converting canvas to data URL:', error)
              reject(error)
            }
          }).catch(error => {
            console.error('❌ html2canvas capture failed:', error)
            reject(error)
          })
          
        } catch (error) {
          console.error('❌ Error in captureCurrentFrame:', error)
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
      
      try {
        // STEP 1: Get session ID from localStorage
        const sessionId = localStorage.getItem('sessionId')
        if (!sessionId) {
          throw new Error('No session ID found. Please start from home page.')
        }
        
        // STEP 2: Get palette number (1-20 for built-in, or index for uploaded)
        const paletteNo = selectedIndex.value + 1
        console.log('📊 Palette number:', paletteNo)
        
        // STEP 3: Hide UI elements for clean capture
        console.log('🎭 Hiding UI elements for clean capture...')
        const controlsElement = document.querySelector('.controls')
        const capturePrompt = document.querySelector('.capture-prompt')
        const galleryElement = document.querySelector('.palette-gallery')
        
        // Temporarily hide UI elements
        if (controlsElement) controlsElement.style.display = 'none'
        if (capturePrompt) capturePrompt.style.display = 'none'
        if (galleryElement) galleryElement.style.display = 'none'
        
        // Wait a moment for DOM to update
        await new Promise(resolve => setTimeout(resolve, 100))
        
        // STEP 4: Capture the screenshot
        console.log('📷 Capturing screenshot...')
        const screenshot = await captureCurrentFrame()
        console.log('✅ Screenshot captured successfully')
        
        // STEP 5: Restore UI elements and show loading
        if (controlsElement) controlsElement.style.display = 'block'
        if (capturePrompt) capturePrompt.style.display = 'block'
        if (galleryElement) galleryElement.style.display = 'flex'
        
        // Show loading spinner  
        showLoading.value = true
        // Note: loadingMessage uses i18n in setup() default, but we can't use $t in setup
        // The LoadingSpinner component handles translation
        
        // STEP 6: Upload screenshot to R2 first
        console.log('☁️ Uploading screenshot to R2...')
        const uploadResponse = await ApiService.request('/uploads/screenshot', {
          method: 'POST',
          body: JSON.stringify({
            screenshot: screenshot,
            session_id: sessionId,
            palette_no: paletteNo
          })
        })
        
        const screenshotKey = uploadResponse.data.key
        console.log('✅ Screenshot uploaded to R2:', screenshotKey)
        
        // Update loading message (static for now, or we can emit events)
        // loadingMessage will show the default from setup
        
        // STEP 7: Send job to n8n via /api/jobs endpoint with R2 key
        console.log('📡 Creating PALETTE_ANALYSIS job...')
        const jobResponse = await ApiService.request('/jobs', {
          method: 'POST',
          body: JSON.stringify({
            type: 'PALETTE_ANALYSIS',
            session_id: sessionId,
            input_data: {
              palette_no: paletteNo,
              screenshot_key: screenshotKey
            }
          })
        })
        
        console.log('✅ Job created:', jobResponse)
        const jobId = jobResponse.data.job_id
        
        // STEP 7: Poll for job completion
        console.log('⏳ Polling for job completion...')
        const pollInterval = 2000 // 2 seconds
        const maxAttempts = 60 // 2 minutes max
        let attempts = 0
        
        const checkJobStatus = async () => {
          attempts++
          
          if (attempts > maxAttempts) {
            throw new Error('Job timeout: Analysis took too long')
          }
          
          const statusResponse = await ApiService.request(`/jobs/${jobId}`)
          const status = statusResponse.data.status
          
          console.log(`🔍 Job status (attempt ${attempts}):`, status)
          
          if (status === 'COMPLETED') {
            console.log('✅ Job completed successfully!')
            console.log('📦 Full status response:', statusResponse)
            console.log('📦 Status response data:', statusResponse.data)
            
            const result = statusResponse.data.result_data
            
            // SAFETY CHECK: Ensure result_data exists before navigation
            if (!result) {
              console.error('❌ Job completed but result_data is missing!', {
                statusResponse: statusResponse,
                jobData: statusResponse.data,
                hasResultData: 'result_data' in statusResponse.data,
                resultDataValue: statusResponse.data.result_data
              })
              throw new Error('Job completed but result_data is missing from API response. Please check the backend logs.')
            }
            
            console.log('✅ result_data found:', result)
            
            // Helper function for Unicode-safe base64 encoding
            const unicodeSafeBase64Encode = (str) => {
              try {
                return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g, (match, p1) => {
                  return String.fromCharCode('0x' + p1)
                }))
              } catch (error) {
                console.error('Error encoding string:', error)
                // eslint-disable-next-line no-control-regex
                const cleanStr = str.replace(/[^\u0000-\u007F]/g, "")
                return btoa(cleanStr)
              }
            }
            
            // Navigate to color palette page with the result
            router.push({
              name: 'ColorPalettePage',
              query: { data: unicodeSafeBase64Encode(JSON.stringify(result)) }
            })
            
          } else if (status === 'FAILED') {
            throw new Error(statusResponse.data.error_message || 'Job failed')
          } else {
            // Still QUEUED or RUNNING, check again
            setTimeout(checkJobStatus, pollInterval)
          }
        }
        
        // Start polling
        await checkJobStatus()
        
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
            }
          }
        ]
      }
    }
    
    // Lifecycle
    onMounted(async () => {
      console.log('🎬 GradientPalette mounted')
      await loadGifs()
      // Show capture prompt after a short delay
      setTimeout(() => {
        showCapturePrompt.value = true
        startCapturePromptAnimation()
      }, 500)
    })
    
    onBeforeUnmount(() => {
      // Nothing to cleanup currently
    })
    
    return {
      currentGifSrc,
      gifVisible,
      showCapturePrompt,
      animatePrompt,
      isCapturing,
      isUploading,
      showModal,
      showLoading,
      loadingMessage,
      modalTitle,
      modalMessage,
      modalButtons,
      animatedGif,
      capturePalette,
      // gallery
      galleryGifs,
      thumbnailSrcs,
      allThumbnails,
      selectedIndex,
      thumbnailScroller,
      selectGif,
      scrollGallery,
      uploadedItems,
      handleFileUpload,
      dropIcon
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

/* Bottom gallery */
.palette-gallery {
  position: absolute;
  bottom: 18px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: rgba(20, 20, 20, 0.45);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 14px;
  backdrop-filter: blur(10px);
  z-index: 12;
}

.thumbnails {
  display: flex;
  overflow-x: auto;
  max-width: 70vw;
  gap: 10px;
  scrollbar-width: none; /* Firefox */
}
.thumbnails::-webkit-scrollbar { display: none; }

.thumbnail {
  width: 75px;
  height: 45px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.25);
  cursor: pointer;
  opacity: 0.9;
  transition: transform 0.2s ease, opacity 0.2s ease, box-shadow 0.2s ease;
  flex: 0 0 auto; /* Prevent shrinking in flex scroller */
}
.thumbnail:hover { transform: scale(1.06); opacity: 1; }
.thumbnail.active { box-shadow: 0 0 0 2px #ffffff; opacity: 1; }

/* Upload tile */
.upload-tile {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  position: relative;
  width: 75px; /* Ensure same as .thumbnail explicitly */
  height: 45px;
  background: rgba(255,255,255,0.08);
  border-style: dashed;
  border-width: 2px;
  border-color: rgba(255,255,255,0.35);
  flex: 0 0 auto; /* Do not let flexbox collapse it */
}
.upload-icon {
  width: 60%;
  height: 60%;
  object-fit: contain;
  filter: drop-shadow(0 1px 1px rgba(0,0,0,0.25));
}
.upload-tile input[type="file"] {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0; /* Explicit to avoid shorthand issues */
  opacity: 0;
  cursor: pointer;
}
.upload-label {
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.gallery-nav {
  background: rgba(255,255,255,0.15);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.25);
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  user-select: none;
}
.gallery-nav:hover { background: rgba(255,255,255,0.25); }

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
  bottom: 120px; /* moved up to make room for gallery */
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

/* Capture utility class */
.capturing .controls,
.capturing .capture-prompt,
.capturing .loading-spinner,
.capturing .modal {
  display: none !important;
}

/* Responsive design */
@media (max-width: 768px) {
  .palette-gallery { bottom: 12px; padding: 8px 10px; }
  .thumbnail { width: 64px; height: 36px; }
  .gallery-nav { width: 26px; height: 26px; }
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
    bottom: 100px;
  }
}
</style>
