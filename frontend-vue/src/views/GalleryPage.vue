<template>
  <div class="gallery-page">
    <div class="gallery-container">
      <!-- Step Progress Indicator -->
      <div class="progress-indicator">
        <div class="progress-step completed">1. Emotion Selected</div>
        <div :class="['progress-step', { completed: step2Complete }]">2. Choose 3 Paintings</div>
        <div :class="['progress-step', { completed: step3Complete }]">3. Select Character</div>
        <div :class="['progress-step', { completed: step4Complete }]">4. Create Story</div>
      </div>

      <!-- Selected Paintings Drop Zone -->
      <div class="selection-area">
        <h2>Your Selected Paintings</h2>
        <p class="instruction">
          <span class="step-label">Step 2:</span> 
          Drag and drop 3 paintings that speak to you
        </p>
        
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
              <span>Drop painting {{ i }} here</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Painting Gallery -->
      <div class="gallery-section">
        <h3>Recommended Paintings</h3>
        <div class="paintings-grid">
          <div 
            v-for="(painting, index) in recommendations" 
            :key="index"
            class="painting-item"
            draggable="true"
            @dragstart="handleDragStart($event, painting)"
            @click="selectPainting(painting)"
          >
            <img :src="painting.url" :alt="painting.title" />
            <div class="painting-info">
              <h4>{{ painting.title }}</h4>
              <p>{{ painting.artist }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Character Selection -->
      <div v-if="step2Complete" class="character-section">
        <h3>Choose Your Narrative Style</h3>
        <p class="instruction">
          <span class="step-label">Step 3:</span> 
          Select a character to guide your story
        </p>
        
        <div class="character-cards">
          <div 
            v-for="character in characters" 
            :key="character.id"
            :class="['character-card', { 'selected': selectedCharacter === character.id }]"
            @click="selectCharacter(character.id)"
          >
            <img :src="character.image" :alt="character.name" />
            <h4>{{ character.name }}</h4>
            <p>{{ character.description }}</p>
          </div>
        </div>
      </div>

      <!-- Name Input -->
      <div v-if="step3Complete" class="name-section">
        <h3>Tell us your name</h3>
        <p class="instruction">This will personalize your story</p>
        <input 
          v-model="userName" 
          type="text" 
          placeholder="Enter your name"
          class="name-input"
          maxlength="50"
        />
      </div>

      <!-- Generate Story Button -->
      <div v-if="step4Complete" class="story-section">
        <button 
          class="generate-story-btn"
          @click="generateStory"
          :disabled="generatingStory"
        >
          {{ generatingStory ? 'Creating Your Story...' : 'Generate Story' }}
        </button>
      </div>
    </div>
    
    <LoadingSpinner :show="loading" :message="loadingMessage" />
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

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
    const generatingStory = ref(false)
    
    // Page data
    const pageData = ref({})
    const recommendations = ref([])
    const selectedPaintings = ref([])
    const selectedCharacter = ref('')
    const userName = ref('')
    
    // Step completion tracking
    const step2Complete = computed(() => selectedPaintings.value.length === 3)
    const step3Complete = computed(() => step2Complete.value && selectedCharacter.value)
    const step4Complete = computed(() => step3Complete.value && userName.value.trim().length > 0)
    
    // Character options
    const characters = ref([
      {
        id: 'poet',
        name: 'The Poet',
        description: 'Weaves tales with lyrical beauty and emotional depth',
        image: require('@/assets/images/style1-a.png')
      },
      {
        id: 'storyteller',
        name: 'The Storyteller', 
        description: 'Creates engaging narratives with vivid descriptions',
        image: require('@/assets/images/style2-a.png')
      },
      {
        id: 'philosopher',
        name: 'The Philosopher',
        description: 'Explores deep meanings and profound insights',
        image: require('@/assets/images/style3-a.png')
      },
      {
        id: 'dreamer',
        name: 'The Dreamer',
        description: 'Crafts whimsical and imaginative stories',
        image: require('@/assets/images/style4-a.png')
      },
      {
        id: 'sage',
        name: 'The Sage',
        description: 'Shares wisdom through timeless tales',
        image: require('@/assets/images/style5-a.png')
      }
    ])
    
    // Drag and drop
    const draggedPainting = ref(null)
    
    // Methods
    const loadPageData = () => {
      try {
        if (route.query.data) {
          const data = JSON.parse(atob(route.query.data))
          pageData.value = data
          recommendations.value = data.recommendations || []
        } else {
          router.push('/')
        }
      } catch (error) {
        console.error('Error loading page data:', error)
        router.push('/')
      }
    }
    
    const handleDragStart = (event, painting) => {
      draggedPainting.value = painting
      event.dataTransfer.effectAllowed = 'copy'
    }
    
    const handleDrop = (event, slotIndex) => {
      event.preventDefault()
      
      if (draggedPainting.value && !selectedPaintings.value[slotIndex]) {
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
    
    const selectPainting = (painting) => {
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
      selectedPaintings.value[index] = null
    }
    
    const selectCharacter = (characterId) => {
      selectedCharacter.value = characterId
    }
    
    const generateStory = async () => {
      if (!step4Complete.value) return
      
      generatingStory.value = true
      loading.value = true
      loadingMessage.value = 'Creating your personalized story...'
      
      try {
        // Save selection first
        const selectionResponse = await fetch('/api/save-selection', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: pageData.value.sessionId,
            palette_filename: pageData.value.filename,
            emotion: pageData.value.selectedEmotion,
            emotion_probability: pageData.value.selectedProbability,
            selected_paintings: selectedPaintings.value.filter(p => p),
            character: selectedCharacter.value,
            user_name: userName.value
          })
        })
        
        if (!selectionResponse.ok) {
          console.warn('Failed to save selection, continuing with story generation')
        }
        
        // Generate story
        const storyResponse = await fetch('/api/generate-story', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: pageData.value.sessionId,
            user_name: userName.value,
            narrative_style: selectedCharacter.value,
            emotion: pageData.value.selectedEmotion,
            emotion_probability: pageData.value.selectedProbability,
            selected_paintings: selectedPaintings.value.filter(p => p)
          })
        })
        
        if (!storyResponse.ok) {
          throw new Error('Failed to generate story')
        }
        
        const storyData = await storyResponse.json()
        
        // Navigate to story page
        const storyPageData = {
          ...pageData.value,
          selectedPaintings: selectedPaintings.value.filter(p => p),
          selectedCharacter: selectedCharacter.value,
          userName: userName.value,
          story: storyData
        }
        
        router.push({
          name: 'StoryPage',
          query: { data: btoa(JSON.stringify(storyPageData)) }
        })
        
      } catch (error) {
        console.error('Error generating story:', error)
        loading.value = false
        generatingStory.value = false
        alert('Failed to generate story. Please try again.')
      }
    }
    
    // Lifecycle
    onMounted(() => {
      loadPageData()
      // Initialize selectedPaintings as array of nulls
      selectedPaintings.value = [null, null, null]
    })
    
    return {
      loading,
      loadingMessage,
      generatingStory,
      recommendations,
      selectedPaintings,
      selectedCharacter,
      userName,
      characters,
      step2Complete,
      step3Complete,
      step4Complete,
      handleDragStart,
      handleDrop,
      selectPainting,
      removePainting,
      selectCharacter,
      generateStory
    }
  }
}
</script>

<style scoped>
.gallery-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.gallery-container {
  max-width: 1400px;
  margin: 0 auto;
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.progress-indicator {
  display: flex;
  justify-content: center;
  margin-bottom: 40px;
  gap: 20px;
  flex-wrap: wrap;
}

.progress-step {
  padding: 10px 20px;
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 25px;
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
  color: #6c757d;
  transition: all 0.3s ease;
}

.progress-step.completed {
  background: linear-gradient(135deg, #4ecdc4, #44a08d);
  border-color: #4ecdc4;
  color: white;
}

.selection-area {
  margin-bottom: 40px;
  text-align: center;
}

.selection-area h2 {
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  color: #333;
  margin-bottom: 10px;
}

.instruction {
  font-family: 'Poppins', sans-serif;
  color: #666;
  margin-bottom: 30px;
}

.step-label {
  font-weight: 600;
  color: #4ecdc4;
}

.drop-zones {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.drop-zone {
  width: 200px;
  height: 250px;
  border: 3px dashed #ddd;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  position: relative;
}

.drop-zone:hover {
  border-color: #4ecdc4;
}

.drop-zone.has-painting {
  border: 3px solid #4ecdc4;
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
  border-radius: 8px;
}

.remove-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  width: 25px;
  height: 25px;
  background: #ff4757;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drop-placeholder {
  color: #999;
  font-family: 'Poppins', sans-serif;
  text-align: center;
}

.gallery-section {
  margin-bottom: 40px;
}

.gallery-section h3 {
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
  text-align: center;
}

.paintings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.painting-item {
  background: #f8f9fa;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.painting-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.painting-item img {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.painting-info {
  padding: 15px;
}

.painting-info h4 {
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  margin-bottom: 5px;
  color: #333;
  font-size: 14px;
}

.painting-info p {
  font-family: 'Poppins', sans-serif;
  color: #666;
  font-size: 12px;
}

.character-section {
  margin-bottom: 40px;
  text-align: center;
}

.character-section h3 {
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
}

.character-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.character-card {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.character-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  border-color: #4ecdc4;
}

.character-card.selected {
  border-color: #4ecdc4;
  background: linear-gradient(135deg, #4ecdc4, #44a08d);
  color: white;
}

.character-card img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 15px;
}

.character-card h4 {
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  margin-bottom: 10px;
}

.character-card p {
  font-family: 'Poppins', sans-serif;
  font-size: 14px;
  line-height: 1.4;
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
  border-color: #4ecdc4;
  outline: none;
}

.story-section {
  text-align: center;
}

.generate-story-btn {
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
  color: white;
  border: none;
  padding: 20px 50px;
  font-size: 20px;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.generate-story-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.generate-story-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
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
}
</style> 