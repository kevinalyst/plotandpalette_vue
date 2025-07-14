<template>
  <div class="story-page">
    <div class="story-container">
      <!-- Header Section -->
      <div class="header-section">
        <h2 class="page-title">Story Generation</h2>
        <p class="page-subtitle">Create narratives inspired by your color palette [[memory:2258489]]</p>
      </div>

      <!-- Story Input Section -->
      <div class="story-input-section">
        <div class="input-header">
          <h3>Story Elements</h3>
          <p>Configure the elements for your story generation</p>
        </div>
        
        <div class="input-grid">
          <div class="input-group">
            <label>📷 Image</label>
            <div class="image-display">
              <img v-if="storyData.image" :src="storyData.image" alt="Story image" />
              <div v-else class="placeholder-image">
                <span>📷</span>
                <p>No image selected</p>
              </div>
            </div>
          </div>

          <div class="input-group">
            <label>🎨 Artist</label>
            <input 
              v-model="storyData.artist" 
              type="text" 
              placeholder="Enter artist name..."
              class="story-input"
            />
          </div>

          <div class="input-group">
            <label>🖼️ Title</label>
            <input 
              v-model="storyData.title" 
              type="text" 
              placeholder="Enter artwork title..."
              class="story-input"
            />
          </div>

          <div class="input-group">
            <label>📅 Year</label>
            <input 
              v-model="storyData.year" 
              type="number" 
              placeholder="Enter year..."
              class="story-input"
            />
          </div>
        </div>
      </div>

      <!-- Story Style Selection -->
      <div class="style-section">
        <div class="style-header">
          <h3>Narrative Style</h3>
          <p>Choose from five preset story styles</p>
        </div>
        
        <div class="style-grid">
          <div 
            v-for="style in storyStyles" 
            :key="style.id"
            class="style-card"
            :class="{ selected: selectedStyle === style.id }"
            @click="selectedStyle = style.id"
          >
            <div class="style-icon">{{ style.icon }}</div>
            <h4>{{ style.name }}</h4>
            <p>{{ style.description }}</p>
          </div>
        </div>
      </div>

      <!-- Generate Button -->
      <div class="generate-section">
        <button 
          @click="generateStory" 
          :disabled="!canGenerate || isGenerating"
          class="generate-btn"
        >
          <span v-if="isGenerating">🔄 Generating...</span>
          <span v-else>✨ Generate Story</span>
        </button>
      </div>

      <!-- Generated Story Display -->
      <div class="story-display" v-if="generatedStory">
        <div class="story-header">
          <h3>Generated Story</h3>
          <div class="story-meta">
            <span>Style: {{ getCurrentStyleName() }}</span>
            <span>•</span>
            <span>{{ formatDate(new Date()) }}</span>
          </div>
        </div>
        
        <div class="story-content">
          <div class="story-text">
            <p v-for="(paragraph, index) in storyParagraphs" :key="index">
              {{ paragraph }}
            </p>
          </div>
        </div>
        
        <div class="story-actions">
          <button @click="copyStory" class="action-btn">
            📋 Copy Story
          </button>
          <button @click="saveStory" class="action-btn">
            💾 Save Story
          </button>
          <button @click="shareStory" class="action-btn">
            📤 Share Story
          </button>
          <button @click="regenerateStory" class="action-btn secondary">
            🔄 Regenerate
          </button>
        </div>
      </div>

      <!-- Story History -->
      <div class="story-history" v-if="storyHistory.length > 0">
        <div class="history-header">
          <h3>Story History</h3>
          <button @click="clearHistory" class="clear-btn">Clear All</button>
        </div>
        
        <div class="history-list">
          <div 
            v-for="story in storyHistory" 
            :key="story.id"
            class="history-item"
            @click="selectFromHistory(story)"
          >
            <div class="history-preview">
              <h4>{{ story.title }}</h4>
              <p>{{ story.preview }}</p>
            </div>
            <div class="history-meta">
              <span>{{ story.style }}</span>
              <span>{{ formatDate(story.createdAt) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <div class="navigation-section">
        <button @click="goBack" class="back-btn">
          ← Back to Palette
        </button>
        <button @click="viewGallery" class="gallery-btn">
          Gallery →
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'StoryPage',
  setup() {
    const router = useRouter()
    const selectedStyle = ref(1)
    const isGenerating = ref(false)
    const generatedStory = ref('')
    const storyHistory = ref([])
    
    // Story data - requires image, title, artist, and year as per memory
    const storyData = ref({
      image: null,
      title: '',
      artist: '',
      year: ''
    })
    
    // Inject global state
    const appState = inject('appState')
    const showValidation = inject('showValidation')

    // Five preset story styles as per memory
    const storyStyles = ref([
      {
        id: 1,
        name: 'Romantic',
        icon: '💕',
        description: 'Passionate love stories with emotional depth and tender moments'
      },
      {
        id: 2,
        name: 'Adventure',
        icon: '⚔️',
        description: 'Thrilling tales of exploration, quests, and heroic journeys'
      },
      {
        id: 3,
        name: 'Mystery',
        icon: '🔍',
        description: 'Suspenseful narratives with hidden secrets and unexpected twists'
      },
      {
        id: 4,
        name: 'Fantasy',
        icon: '🧙‍♂️',
        description: 'Magical worlds filled with mythical creatures and enchanting powers'
      },
      {
        id: 5,
        name: 'Historical',
        icon: '🏛️',
        description: 'Stories set in different time periods with rich historical context'
      }
    ])

    // Initialize from global state
    onMounted(() => {
      if (appState?.selectedPaintings?.value?.length > 0) {
        const painting = appState.selectedPaintings.value[0]
        storyData.value = {
          image: painting.image || null,
          title: painting.title || '',
          artist: painting.artist || '',
          year: painting.year || ''
        }
      }
      
      loadStoryHistory()
    })

    const canGenerate = computed(() => {
      return storyData.value.image && 
             storyData.value.title && 
             storyData.value.artist && 
             storyData.value.year && 
             selectedStyle.value
    })

    const storyParagraphs = computed(() => {
      return generatedStory.value.split('\n\n').filter(p => p.trim())
    })

    const getCurrentStyleName = () => {
      const style = storyStyles.value.find(s => s.id === selectedStyle.value)
      return style ? style.name : 'Unknown'
    }

    const formatDate = (date) => {
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date)
    }

    const generateStory = async () => {
      if (!canGenerate.value) {
        showValidation('Please fill in all required fields: image, title, artist, and year')
        return
      }

      isGenerating.value = true
      
      try {
        // Simulate API call to story generation service
        await new Promise(resolve => setTimeout(resolve, 3000))
        
        // Generate story based on selected style
        const story = generateStoryContent()
        generatedStory.value = story
        
        // Add to history
        addToHistory(story)
        
        showValidation('Story generated successfully!')
        
      } catch (error) {
        console.error('Error generating story:', error)
        showValidation('Error generating story. Please try again.')
      } finally {
        isGenerating.value = false
      }
    }

    const generateStoryContent = () => {
      const style = storyStyles.value.find(s => s.id === selectedStyle.value)
      const styleTemplates = {
        1: `In the gentle embrace of "${storyData.value.title}" by ${storyData.value.artist} (${storyData.value.year}), two souls found each other across the canvas of time. The warm hues whispered of passion, while the cool tones spoke of eternal devotion.

        Their love story unfolded like the very brushstrokes before them - bold and tender, passionate and serene. Each color told a chapter of their romance, from the first shy glance to the passionate embrace that would define their forever.

        As they stood before this masterpiece, they realized that their love, like the painting itself, was a work of art - created with patience, nurtured with care, and destined to inspire others for generations to come.`,
        
        2: `The ancient map hidden within "${storyData.value.title}" by ${storyData.value.artist} (${storyData.value.year}) revealed the location of the lost treasure. Captain Elena traced the intricate patterns with her weathered finger, her heart racing with anticipation.

        The colors seemed to shift and dance, pointing toward uncharted territories where danger and fortune awaited in equal measure. With her loyal crew at her side, she set sail toward the horizon, guided by the very hues that had captured the imagination of adventurers for centuries.

        Through storms and calm seas, past mythical islands and treacherous reefs, the painting's colors served as her compass, leading her to a discovery that would change the course of history itself.`,
        
        3: `Detective Morgan stared at "${storyData.value.title}" by ${storyData.value.artist} (${storyData.value.year}), knowing that within its layers lay the key to solving the century-old mystery. The painting had been the only witness to events that had baffled investigators for decades.

        Each brushstroke seemed to hold secrets - the deep shadows concealing clues, the bright highlights revealing truths long buried. As she studied the intricate details, patterns began to emerge that connected the past to the present in ways she had never imagined.

        The final revelation came not through the image itself, but through the very pigments used - a chemical signature that would expose the truth and bring justice to those who had waited so long for answers.`,
        
        4: `In the mystical realm where "${storyData.value.title}" by ${storyData.value.artist} (${storyData.value.year}) served as a portal between worlds, young Aria discovered her true heritage. The painting pulsed with ancient magic, its colors shifting with the phases of the moon.

        Each hue contained the essence of different magical creatures - the blues of the water sprites, the greens of the forest guardians, the golds of the sun dragons. As she touched the canvas, she felt the power coursing through her veins, awakening abilities she never knew she possessed.

        With her newfound powers and the guidance of the painting's embedded wisdom, Aria embarked on a quest to restore balance to the realm and fulfill the prophecy that had been whispered in the colors for centuries.`,
        
        5: `In the year ${storyData.value.year}, when "${storyData.value.title}" was first revealed to the world, ${storyData.value.artist} could hardly have imagined the impact it would have on society. The painting captured not just an image, but the very spirit of an era in transition.

        Against the backdrop of historical upheaval, the artwork served as a beacon of hope for those who dared to dream of a better tomorrow. Its colors reflected the struggles and triumphs of a generation caught between the old world and the new.

        As historians would later discover, hidden within the composition were subtle references to the political and social movements of the time, making it not just a work of art, but a historical document that would influence the course of events for generations to come.`
      }
      
      return styleTemplates[selectedStyle.value] || styleTemplates[1]
    }

    const addToHistory = (story) => {
      const historyItem = {
        id: Date.now(),
        title: storyData.value.title,
        preview: story.split('\n\n')[0].substring(0, 100) + '...',
        content: story,
        style: getCurrentStyleName(),
        createdAt: new Date(),
        storyData: { ...storyData.value },
        styleId: selectedStyle.value
      }
      
      storyHistory.value.unshift(historyItem)
      
      // Keep only last 10 stories
      if (storyHistory.value.length > 10) {
        storyHistory.value = storyHistory.value.slice(0, 10)
      }
      
      saveStoryHistory()
    }

    const loadStoryHistory = () => {
      const saved = localStorage.getItem('storyHistory')
      if (saved) {
        try {
          storyHistory.value = JSON.parse(saved).map(item => ({
            ...item,
            createdAt: new Date(item.createdAt)
          }))
        } catch (error) {
          console.error('Error loading story history:', error)
        }
      }
    }

    const saveStoryHistory = () => {
      localStorage.setItem('storyHistory', JSON.stringify(storyHistory.value))
    }

    const selectFromHistory = (story) => {
      generatedStory.value = story.content
      storyData.value = { ...story.storyData }
      selectedStyle.value = story.styleId
      showValidation('Story loaded from history')
    }

    const clearHistory = () => {
      if (confirm('Are you sure you want to clear all story history?')) {
        storyHistory.value = []
        saveStoryHistory()
        showValidation('Story history cleared')
      }
    }

    const copyStory = async () => {
      try {
        await navigator.clipboard.writeText(generatedStory.value)
        showValidation('Story copied to clipboard!')
      } catch (error) {
        console.error('Error copying story:', error)
        showValidation('Error copying story')
      }
    }

    const saveStory = () => {
      const blob = new Blob([generatedStory.value], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${storyData.value.title}_story.txt`
      a.click()
      URL.revokeObjectURL(url)
      showValidation('Story saved!')
    }

    const shareStory = async () => {
      if (navigator.share) {
        try {
          await navigator.share({
            title: `Story: ${storyData.value.title}`,
            text: generatedStory.value
          })
          showValidation('Story shared!')
        } catch (error) {
          console.error('Error sharing story:', error)
          copyStory()
        }
      } else {
        copyStory()
      }
    }

    const regenerateStory = () => {
      generatedStory.value = ''
      generateStory()
    }

    const goBack = () => {
      router.push('/palette')
    }

    const viewGallery = () => {
      router.push('/gallery')
    }

    return {
      storyData,
      selectedStyle,
      isGenerating,
      generatedStory,
      storyHistory,
      storyStyles,
      canGenerate,
      storyParagraphs,
      getCurrentStyleName,
      formatDate,
      generateStory,
      selectFromHistory,
      clearHistory,
      copyStory,
      saveStory,
      shareStory,
      regenerateStory,
      goBack,
      viewGallery
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
  max-width: 1200px;
  margin: 0 auto;
  color: white;
}

.header-section {
  text-align: center;
  margin-bottom: 40px;
}

.page-title {
  font-family: 'Poppins', sans-serif;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.page-subtitle {
  font-family: 'Poppins', sans-serif;
  font-size: 1.1rem;
  font-weight: 300;
  opacity: 0.9;
}

.story-input-section {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 40px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.input-header {
  text-align: center;
  margin-bottom: 30px;
}

.input-header h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.input-header p {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  opacity: 0.8;
}

.input-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.input-group label {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 10px;
  color: white;
}

.story-input {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  padding: 12px;
  color: white;
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
}

.story-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.image-display {
  width: 100%;
  height: 150px;
  border-radius: 10px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-display img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder-image {
  text-align: center;
  opacity: 0.6;
}

.placeholder-image span {
  font-size: 2rem;
  display: block;
  margin-bottom: 10px;
}

.style-section {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 40px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.style-header {
  text-align: center;
  margin-bottom: 30px;
}

.style-header h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.style-header p {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  opacity: 0.8;
}

.style-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.style-card {
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.style-card:hover, .style-card.selected {
  border-color: #FFD700;
  background: rgba(255, 215, 0, 0.1);
  transform: translateY(-3px);
}

.style-icon {
  font-size: 2rem;
  margin-bottom: 15px;
}

.style-card h4 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.style-card p {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  opacity: 0.8;
  line-height: 1.4;
}

.generate-section {
  text-align: center;
  margin-bottom: 40px;
}

.generate-btn {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  color: white;
  border: none;
  padding: 15px 40px;
  border-radius: 25px;
  font-family: 'Poppins', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.story-display {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 40px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.story-header {
  text-align: center;
  margin-bottom: 30px;
}

.story-header h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.story-meta {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  opacity: 0.8;
}

.story-content {
  margin-bottom: 30px;
}

.story-text {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.story-text p {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 20px;
  text-align: justify;
}

.story-text p:last-child {
  margin-bottom: 0;
}

.story-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 10px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.action-btn.secondary {
  background: rgba(255, 215, 0, 0.2);
  border-color: rgba(255, 215, 0, 0.3);
}

.story-history {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 40px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.history-header h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.5rem;
  font-weight: 600;
}

.clear-btn {
  background: rgba(255, 107, 107, 0.2);
  color: white;
  border: 1px solid rgba(255, 107, 107, 0.3);
  padding: 8px 16px;
  border-radius: 15px;
  cursor: pointer;
  font-family: 'Poppins', sans-serif;
  font-size: 0.8rem;
  transition: all 0.3s ease;
}

.clear-btn:hover {
  background: rgba(255, 107, 107, 0.3);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.history-item {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.history-item:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.history-preview h4 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 5px;
}

.history-preview p {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  opacity: 0.8;
  margin-bottom: 10px;
}

.history-meta {
  font-family: 'Poppins', sans-serif;
  font-size: 0.8rem;
  opacity: 0.7;
}

.navigation-section {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-top: 40px;
}

.back-btn, .gallery-btn {
  padding: 15px 30px;
  border-radius: 25px;
  border: none;
  cursor: pointer;
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.back-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.gallery-btn {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

.back-btn:hover, .gallery-btn:hover {
  transform: translateY(-2px);
}

.gallery-btn:hover {
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .input-grid {
    grid-template-columns: 1fr;
  }
  
  .style-grid {
    grid-template-columns: 1fr;
  }
  
  .story-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .action-btn {
    width: 100%;
    text-align: center;
  }
  
  .navigation-section {
    flex-direction: column;
  }
  
  .back-btn, .gallery-btn {
    width: 100%;
  }
}
</style> 