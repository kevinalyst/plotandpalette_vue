<template>
  <div class="story-page">
    <div class="story-container">
      <!-- Story Header -->
      <div class="story-header">
        <h1>Your Personalized Story</h1>
        <div class="story-meta">
          <span>Created for {{ storyData.userName || 'You' }}</span>
          <span>•</span>
          <span>Emotion: {{ storyData.selectedEmotion }}</span>
          <span>•</span>
          <span>Style: {{ getCharacterName(storyData.selectedCharacter) }}</span>
        </div>
      </div>

      <!-- Selected Paintings Display -->
      <div class="paintings-showcase">
        <h3>Your Chosen Paintings</h3>
        <div class="paintings-row">
          <div 
            v-for="(painting, index) in storyData.selectedPaintings" 
            :key="index"
            class="painting-showcase"
          >
            <img :src="painting.url" :alt="painting.title" />
            <div class="painting-details">
              <h4>{{ painting.title }}</h4>
              <p>{{ painting.artist }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Story Content -->
      <div class="story-content">
        <div class="story-text">
          <div v-html="formattedStory"></div>
        </div>
      </div>

      <!-- Story Stats -->
      <div class="story-stats">
        <div class="stat">
          <span class="stat-number">{{ wordCount }}</span>
          <span class="stat-label">Words</span>
        </div>
        <div class="stat">
          <span class="stat-number">{{ Math.ceil(wordCount / 200) }}</span>
          <span class="stat-label">Min Read</span>
        </div>
        <div class="stat">
          <span class="stat-number">{{ storyData.selectedPaintings?.length || 0 }}</span>
          <span class="stat-label">Paintings</span>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="story-actions">
        <button @click="shareStory" class="action-btn primary">
          Share Story
        </button>
        <button @click="copyStoryLink" class="action-btn secondary">
          Copy Link
        </button>
        <button @click="createAnotherStory" class="action-btn secondary">
          Create Another
        </button>
        <button @click="backToHome" class="action-btn tertiary">
          Start Over
        </button>
      </div>

      <!-- Reading Mode Toggle -->
      <div class="reading-mode">
        <button 
          @click="toggleReadingMode" 
          :class="['reading-toggle', { active: readingMode }]"
        >
          {{ readingMode ? 'Exit Reading Mode' : 'Reading Mode' }}
        </button>
      </div>
    </div>

    <!-- Share Modal -->
    <Modal
      :show="showShareModal"
      title="Share Your Story"
      :buttons="shareModalButtons"
    >
      <div class="share-options">
        <button @click="shareToSocial('twitter')" class="social-btn twitter">
          Share on Twitter
        </button>
        <button @click="shareToSocial('facebook')" class="social-btn facebook">
          Share on Facebook
        </button>
        <button @click="shareToSocial('instagram')" class="social-btn instagram">
          Share on Instagram
        </button>
        <div class="share-link">
          <input 
            ref="shareLinkInput"
            :value="shareLink" 
            readonly 
            class="share-link-input"
          />
          <button @click="copyShareLink" class="copy-btn">Copy</button>
        </div>
      </div>
    </Modal>

    <LoadingSpinner :show="loading" :message="loadingMessage" />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import Modal from '@/components/Modal.vue'

export default {
  name: 'StoryPage',
  components: {
    LoadingSpinner,
    Modal
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    // Reactive data
    const loading = ref(false)
    const loadingMessage = ref('')
    const readingMode = ref(false)
    const showShareModal = ref(false)
    const shareLink = ref('')
    const shareLinkInput = ref(null)
    
    // Story data
    const storyData = ref({})
    const rawStory = ref('')
    
    // Character mapping
    const characterNames = {
      'poet': 'The Poet',
      'storyteller': 'The Storyteller',
      'philosopher': 'The Philosopher', 
      'dreamer': 'The Dreamer',
      'sage': 'The Sage'
    }
    
    // Computed properties
    const formattedStory = computed(() => {
      if (!rawStory.value) return ''
      
      // Format the story text with proper paragraphs
      return rawStory.value
        .split('\n\n')
        .map(paragraph => `<p>${paragraph.trim()}</p>`)
        .join('')
    })
    
    const wordCount = computed(() => {
      if (!rawStory.value) return 0
      return rawStory.value.split(/\s+/).filter(word => word.length > 0).length
    })
    
    const shareModalButtons = computed(() => [
      {
        text: 'Close',
        action: () => { showShareModal.value = false },
        secondary: true
      }
    ])
    
    // Methods
    const loadPageData = () => {
      try {
        if (route.query.data) {
          const data = JSON.parse(atob(route.query.data))
          storyData.value = data
          
          // Extract story content
          if (data.story) {
            if (typeof data.story === 'string') {
              rawStory.value = data.story
            } else if (data.story.story) {
              rawStory.value = data.story.story
            } else if (data.story.content) {
              rawStory.value = data.story.content
            }
          }
          
          // Generate share link
          shareLink.value = `${window.location.origin}/story?id=${data.sessionId || 'shared'}`
          
        } else {
          router.push('/')
        }
      } catch (error) {
        console.error('Error loading story data:', error)
        router.push('/')
      }
    }
    
    const getCharacterName = (characterId) => {
      return characterNames[characterId] || characterId
    }
    
    const toggleReadingMode = () => {
      readingMode.value = !readingMode.value
      
      if (readingMode.value) {
        document.body.classList.add('reading-mode')
      } else {
        document.body.classList.remove('reading-mode')
      }
    }
    
    const shareStory = () => {
      showShareModal.value = true
    }
    
    const copyStoryLink = async () => {
      try {
        await navigator.clipboard.writeText(shareLink.value)
        alert('Story link copied to clipboard!')
      } catch (error) {
        console.error('Failed to copy link:', error)
        // Fallback for older browsers
        const textArea = document.createElement('textarea')
        textArea.value = shareLink.value
        document.body.appendChild(textArea)
        textArea.select()
        document.execCommand('copy')
        document.body.removeChild(textArea)
        alert('Story link copied to clipboard!')
      }
    }
    
    const copyShareLink = () => {
      if (shareLinkInput.value) {
        shareLinkInput.value.select()
        document.execCommand('copy')
        alert('Link copied!')
      }
    }
    
    const shareToSocial = (platform) => {
      const storyTitle = `My Personalized Art Story`
      const storyDescription = `I just created a unique story inspired by my emotion "${storyData.value.selectedEmotion}" and curated paintings!`
      
      const urls = {
        twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(storyTitle + ' - ' + storyDescription)}&url=${encodeURIComponent(shareLink.value)}`,
        facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareLink.value)}`,
        instagram: `https://www.instagram.com/` // Instagram doesn't support direct sharing
      }
      
      if (platform === 'instagram') {
        alert('Please copy the link and share it manually on Instagram!')
        copyShareLink()
      } else {
        window.open(urls[platform], '_blank', 'width=600,height=400')
      }
    }
    
    const createAnotherStory = () => {
      // Go back to gallery with same data
      const galleryData = {
        ...storyData.value,
        selectedPaintings: undefined,
        selectedCharacter: undefined,
        userName: undefined
      }
      
      router.push({
        name: 'GalleryPage',
        query: { data: btoa(JSON.stringify(galleryData)) }
      })
    }
    
    const backToHome = () => {
      router.push('/')
    }
    
    // Lifecycle
    onMounted(() => {
      loadPageData()
    })
    
    return {
      loading,
      loadingMessage,
      readingMode,
      showShareModal,
      shareLink,
      shareLinkInput,
      storyData,
      formattedStory,
      wordCount,
      shareModalButtons,
      getCharacterName,
      toggleReadingMode,
      shareStory,
      copyStoryLink,
      copyShareLink,
      shareToSocial,
      createAnotherStory,
      backToHome
    }
  }
}
</script>

<style scoped>
.story-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.story-container {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  position: relative;
}

.story-header {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f1f3f4;
}

.story-header h1 {
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  color: #333;
  margin-bottom: 15px;
  font-size: 32px;
}

.story-meta {
  font-family: 'Poppins', sans-serif;
  color: #666;
  font-size: 14px;
  display: flex;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
}

.paintings-showcase {
  margin-bottom: 40px;
}

.paintings-showcase h3 {
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
  text-align: center;
}

.paintings-row {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.painting-showcase {
  flex: 1;
  max-width: 200px;
  text-align: center;
}

.painting-showcase img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  margin-bottom: 10px;
}

.painting-details h4 {
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  color: #333;
  margin-bottom: 5px;
  font-size: 14px;
}

.painting-details p {
  font-family: 'Poppins', sans-serif;
  color: #666;
  font-size: 12px;
}

.story-content {
  margin-bottom: 40px;
  line-height: 1.8;
}

.story-text {
  font-family: 'Poppins', sans-serif;
  font-size: 16px;
  color: #333;
}

.story-text :deep(p) {
  margin-bottom: 20px;
  text-align: justify;
}

.story-stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 40px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
}

.stat {
  text-align: center;
}

.stat-number {
  display: block;
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  font-size: 24px;
  color: #4ecdc4;
}

.stat-label {
  font-family: 'Poppins', sans-serif;
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.story-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
  margin-bottom: 30px;
}

.action-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 25px;
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.action-btn.primary {
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
  color: white;
}

.action-btn.secondary {
  background: #6c757d;
  color: white;
}

.action-btn.tertiary {
  background: transparent;
  color: #6c757d;
  border: 2px solid #6c757d;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.reading-mode {
  text-align: center;
}

.reading-toggle {
  background: #f8f9fa;
  color: #333;
  border: 2px solid #e9ecef;
  padding: 10px 20px;
  border-radius: 20px;
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.reading-toggle.active {
  background: #4ecdc4;
  color: white;
  border-color: #4ecdc4;
}

.share-options {
  display: flex;
  flex-direction: column;
  gap: 15px;
  align-items: center;
}

.social-btn {
  width: 200px;
  padding: 12px 20px;
  border: none;
  border-radius: 25px;
  color: white;
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.social-btn.twitter {
  background: #1da1f2;
}

.social-btn.facebook {
  background: #4267b2;
}

.social-btn.instagram {
  background: linear-gradient(45deg, #f58529, #dd2a7b, #8134af);
}

.social-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.share-link {
  display: flex;
  gap: 10px;
  width: 100%;
  max-width: 400px;
}

.share-link-input {
  flex: 1;
  padding: 10px 15px;
  border: 2px solid #e9ecef;
  border-radius: 20px;
  font-family: 'Poppins', sans-serif;
  font-size: 14px;
}

.copy-btn {
  padding: 10px 20px;
  background: #4ecdc4;
  color: white;
  border: none;
  border-radius: 20px;
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
  cursor: pointer;
}

/* Reading Mode Styles */
:global(body.reading-mode) {
  background: #f5f5f5;
}

:global(body.reading-mode) .story-container {
  background: #ffffff;
  max-width: 700px;
  padding: 60px;
}

:global(body.reading-mode) .story-text {
  font-size: 18px;
  line-height: 2;
}

/* Responsive design */
@media (max-width: 768px) {
  .story-container {
    padding: 20px;
    margin: 10px;
  }
  
  .story-header h1 {
    font-size: 24px;
  }
  
  .story-meta {
    flex-direction: column;
    gap: 5px;
  }
  
  .paintings-row {
    flex-direction: column;
    align-items: center;
  }
  
  .story-stats {
    gap: 20px;
  }
  
  .action-btn {
    font-size: 12px;
    padding: 10px 20px;
  }
  
  .social-btn {
    width: 180px;
  }
}
</style> 