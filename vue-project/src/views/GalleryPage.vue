<template>
  <div class="gallery-page">
    <div class="gallery-container">
      <!-- Header Section -->
      <div class="header-section">
        <h2 class="page-title">Gallery</h2>
        <p class="page-subtitle">Explore saved color palettes and generated art</p>
      </div>

      <!-- Filter Section -->
      <div class="filter-section">
        <div class="filter-buttons">
          <button 
            v-for="filter in filters" 
            :key="filter.key"
            @click="activeFilter = filter.key"
            :class="['filter-btn', { active: activeFilter === filter.key }]"
          >
            {{ filter.icon }} {{ filter.label }}
          </button>
        </div>
        <div class="search-box">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search gallery..."
            class="search-input"
          >
          <span class="search-icon">🔍</span>
        </div>
      </div>

      <!-- Gallery Grid -->
      <div class="gallery-grid">
        <div v-if="filteredItems.length === 0" class="empty-state">
          <div class="empty-icon">🎨</div>
          <h3>No items found</h3>
          <p>{{ getEmptyStateMessage() }}</p>
          <button @click="createNew" class="create-btn">
            Create New Palette
          </button>
        </div>

        <div 
          v-for="item in filteredItems" 
          :key="item.id"
          class="gallery-item"
          @click="selectItem(item)"
        >
          <div class="item-image">
            <img v-if="item.image" :src="item.image" :alt="item.title" />
            <div v-else class="placeholder-image">
              <div class="color-preview" v-if="item.colors">
                <div 
                  v-for="color in item.colors.slice(0, 4)" 
                  :key="color"
                  class="color-strip"
                  :style="{ backgroundColor: color }"
                ></div>
              </div>
              <span v-else class="placeholder-icon">🎨</span>
            </div>
          </div>
          
          <div class="item-info">
            <h4>{{ item.title }}</h4>
            <p class="item-description">{{ item.description }}</p>
            <div class="item-meta">
              <span class="item-date">{{ formatDate(item.date) }}</span>
              <span class="item-type">{{ item.type }}</span>
            </div>
          </div>
          
          <div class="item-actions">
            <button @click.stop="editItem(item)" class="action-btn edit">
              ✏️
            </button>
            <button @click.stop="shareItem(item)" class="action-btn share">
              📤
            </button>
            <button @click.stop="deleteItem(item)" class="action-btn delete">
              🗑️
            </button>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div class="pagination" v-if="totalPages > 1">
        <button 
          @click="currentPage = Math.max(1, currentPage - 1)"
          :disabled="currentPage === 1"
          class="page-btn"
        >
          ← Previous
        </button>
        
        <div class="page-numbers">
          <button 
            v-for="page in visiblePages" 
            :key="page"
            @click="currentPage = page"
            :class="['page-btn', { active: currentPage === page }]"
          >
            {{ page }}
          </button>
        </div>
        
        <button 
          @click="currentPage = Math.min(totalPages, currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="page-btn"
        >
          Next →
        </button>
      </div>

      <!-- Navigation -->
      <div class="navigation-section">
        <button @click="goBack" class="back-btn">
          ← Back to Palette
        </button>
        <button @click="createNew" class="create-btn">
          Create New →
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'GalleryPage',
  setup() {
    const router = useRouter()
    const searchQuery = ref('')
    const activeFilter = ref('all')
    const currentPage = ref(1)
    const itemsPerPage = ref(12)
    const galleryItems = ref([])
    
    // Inject global state
    const appState = inject('appState')
    const showValidation = inject('showValidation')

    const filters = ref([
      { key: 'all', label: 'All', icon: '🎨' },
      { key: 'palettes', label: 'Palettes', icon: '🎨' },
      { key: 'artworks', label: 'Artworks', icon: '🖼️' },
      { key: 'stories', label: 'Stories', icon: '📖' },
      { key: 'recent', label: 'Recent', icon: '⏰' }
    ])

    // Initialize with sample data
    onMounted(() => {
      loadGalleryItems()
    })

    const loadGalleryItems = () => {
      // Sample gallery items
      galleryItems.value = [
        {
          id: 1,
          title: 'Sunset Palette',
          description: 'Warm colors inspired by a beautiful sunset',
          type: 'palette',
          date: new Date('2024-01-15'),
          colors: ['#FF6B6B', '#FF8E53', '#FF6B9D', '#C44569'],
          image: null
        },
        {
          id: 2,
          title: 'Ocean Dreams',
          description: 'Cool blues and teals from ocean photography',
          type: 'palette',
          date: new Date('2024-01-10'),
          colors: ['#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
          image: null
        },
        {
          id: 3,
          title: 'The Starry Night',
          description: 'Matched artwork with swirling blues and yellows',
          type: 'artwork',
          date: new Date('2024-01-05'),
          colors: ['#1E3A8A', '#FCD34D', '#374151', '#F3F4F6'],
          image: 'palette GIF/1.gif'
        },
        {
          id: 4,
          title: 'Autumn Story',
          description: 'Generated story from autumn color palette',
          type: 'story',
          date: new Date('2024-01-01'),
          colors: ['#D2691E', '#CD853F', '#8B4513', '#FFD700'],
          image: null
        },
        {
          id: 5,
          title: 'Spring Blossoms',
          description: 'Soft pastels from cherry blossom season',
          type: 'palette',
          date: new Date('2023-12-28'),
          colors: ['#FFB6C1', '#98FB98', '#F0E68C', '#E6E6FA'],
          image: null
        },
        {
          id: 6,
          title: 'Desert Mirage',
          description: 'Warm earth tones from desert landscapes',
          type: 'palette',
          date: new Date('2023-12-25'),
          colors: ['#CD853F', '#F4A460', '#DEB887', '#D2691E'],
          image: null
        }
      ]
    }

    const filteredItems = computed(() => {
      let items = galleryItems.value

      // Apply filter
      if (activeFilter.value !== 'all') {
        if (activeFilter.value === 'recent') {
          items = items.filter(item => {
            const daysDiff = (new Date() - item.date) / (1000 * 60 * 60 * 24)
            return daysDiff <= 7
          })
        } else {
          items = items.filter(item => {
            const typeMapping = {
              'palettes': 'palette',
              'artworks': 'artwork',
              'stories': 'story'
            }
            return item.type === typeMapping[activeFilter.value]
          })
        }
      }

      // Apply search
      if (searchQuery.value.trim()) {
        const query = searchQuery.value.toLowerCase().trim()
        items = items.filter(item => 
          item.title.toLowerCase().includes(query) ||
          item.description.toLowerCase().includes(query)
        )
      }

      // Apply pagination
      const startIndex = (currentPage.value - 1) * itemsPerPage.value
      const endIndex = startIndex + itemsPerPage.value
      return items.slice(startIndex, endIndex)
    })

    const totalPages = computed(() => {
      let items = galleryItems.value

      // Apply same filtering logic as filteredItems
      if (activeFilter.value !== 'all') {
        if (activeFilter.value === 'recent') {
          items = items.filter(item => {
            const daysDiff = (new Date() - item.date) / (1000 * 60 * 60 * 24)
            return daysDiff <= 7
          })
        } else {
          items = items.filter(item => {
            const typeMapping = {
              'palettes': 'palette',
              'artworks': 'artwork',
              'stories': 'story'
            }
            return item.type === typeMapping[activeFilter.value]
          })
        }
      }

      if (searchQuery.value.trim()) {
        const query = searchQuery.value.toLowerCase().trim()
        items = items.filter(item => 
          item.title.toLowerCase().includes(query) ||
          item.description.toLowerCase().includes(query)
        )
      }

      return Math.ceil(items.length / itemsPerPage.value)
    })

    const visiblePages = computed(() => {
      const pages = []
      const maxVisible = 5
      let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
      let end = Math.min(totalPages.value, start + maxVisible - 1)
      
      if (end - start + 1 < maxVisible) {
        start = Math.max(1, end - maxVisible + 1)
      }
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      
      return pages
    })

    const formatDate = (date) => {
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      }).format(date)
    }

    const getEmptyStateMessage = () => {
      if (searchQuery.value.trim()) {
        return `No results found for "${searchQuery.value}"`
      }
      
      switch (activeFilter.value) {
        case 'palettes':
          return 'No color palettes saved yet'
        case 'artworks':
          return 'No matched artworks found'
        case 'stories':
          return 'No generated stories yet'
        case 'recent':
          return 'No recent items from the past week'
        default:
          return 'Your gallery is empty. Create your first color palette!'
      }
    }

    const selectItem = (item) => {
      showValidation(`Selected: ${item.title}`)
      
      // Navigate based on item type
      switch (item.type) {
        case 'palette':
          router.push('/palette')
          break
        case 'artwork':
          router.push('/palette')
          break
        case 'story':
          router.push('/story')
          break
      }
    }

    const editItem = (item) => {
      showValidation(`Edit: ${item.title}`)
      // TODO: Implement edit functionality
    }

    const shareItem = (item) => {
      showValidation(`Share: ${item.title}`)
      // TODO: Implement share functionality
    }

    const deleteItem = (item) => {
      if (confirm(`Are you sure you want to delete "${item.title}"?`)) {
        galleryItems.value = galleryItems.value.filter(i => i.id !== item.id)
        showValidation(`Deleted: ${item.title}`)
      }
    }

    const createNew = () => {
      router.push('/')
    }

    const goBack = () => {
      router.push('/palette')
    }

    return {
      searchQuery,
      activeFilter,
      currentPage,
      galleryItems,
      filteredItems,
      totalPages,
      visiblePages,
      filters,
      formatDate,
      getEmptyStateMessage,
      selectItem,
      editItem,
      shareItem,
      deleteItem,
      createNew,
      goBack
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

.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  gap: 20px;
}

.filter-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.filter-btn:hover, .filter-btn.active {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
}

.search-box {
  position: relative;
}

.search-input {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 10px 40px 10px 15px;
  border-radius: 25px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  width: 250px;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.search-icon {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0.7;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.gallery-item {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  overflow: hidden;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.gallery-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.item-image {
  width: 100%;
  height: 200px;
  position: relative;
  overflow: hidden;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
}

.color-preview {
  display: flex;
  width: 80%;
  height: 40px;
  border-radius: 20px;
  overflow: hidden;
}

.color-strip {
  flex: 1;
  height: 100%;
}

.placeholder-icon {
  font-size: 2rem;
  opacity: 0.5;
}

.item-info {
  padding: 15px;
}

.item-info h4 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 5px;
}

.item-description {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  opacity: 0.8;
  margin-bottom: 10px;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  opacity: 0.7;
}

.item-actions {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 5px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.gallery-item:hover .item-actions {
  opacity: 1;
}

.action-btn {
  background: rgba(0, 0, 0, 0.7);
  border: none;
  color: white;
  padding: 5px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: rgba(0, 0, 0, 0.9);
  transform: scale(1.1);
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-state h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.empty-state p {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  opacity: 0.8;
  margin-bottom: 20px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-bottom: 40px;
}

.page-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled), .page-btn.active {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.navigation-section {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-top: 40px;
}

.back-btn, .create-btn {
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

.create-btn {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

.back-btn:hover, .create-btn:hover {
  transform: translateY(-2px);
}

.create-btn:hover {
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .filter-section {
    flex-direction: column;
    gap: 15px;
  }
  
  .search-input {
    width: 100%;
  }
  
  .gallery-grid {
    grid-template-columns: 1fr;
  }
  
  .navigation-section {
    flex-direction: column;
  }
  
  .back-btn, .create-btn {
    width: 100%;
  }
}
</style> 