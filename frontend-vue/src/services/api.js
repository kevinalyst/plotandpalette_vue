// API Service for Plot & Palette Backend
const API_BASE = '/api'

class ApiService {
  
  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    // If sending FormData, let the browser set the correct multipart boundary
    if (config.body instanceof FormData) {
      if (config.headers && 'Content-Type' in config.headers) {
        delete config.headers['Content-Type']
      }
    }

    try {
      console.log(`🌐 API Request: ${config.method || 'GET'} ${url}`)
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const error = await response.text()
        console.error(`❌ API Error: ${response.status} ${response.statusText}`, error)
        throw new Error(`API Error: ${response.status} ${response.statusText}`)
      }

      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        const data = await response.json()
        console.log(`✅ API Success: ${url}`, data)
        return data
      } else {
        return response
      }
    } catch (error) {
      console.error(`🔥 API Request Failed: ${url}`, error)
      throw error
    }
  }

  // Palette endpoints
  async savePalette(formData) {
    return this.request('/save-palette', {
      method: 'POST',
      body: formData, // FormData doesn't need Content-Type header
      headers: {} // Remove default JSON header for FormData
    })
  }

  async getRecommendations(data) {
    return this.request('/get-recommendations', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  async getRecommendationsFromColors(rawColors) {
    return this.request('/get-recommendations-from-colors', {
      method: 'POST',
      body: JSON.stringify({ rawColors })
    })
  }

  async getPaletteInfo(filename) {
    return this.request(`/palette/${filename}`)
  }

  async getRecentPalettes() {
    return this.request('/recent-palettes')
  }

  // Get current session's palette data
  async getSessionPalette(sessionId) {
    return this.request(`/session-palette/${sessionId}`)
  }

  // Emotion endpoints
  async saveEmotion(data) {
    return this.request('/save-emotion', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  // Selection endpoints  
  async saveSelection(data) {
    return this.request('/save-selection', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  async getSelectionHistory() {
    return this.request('/selection-history')
  }

  // Story endpoints
  async generateStory(data) {
    console.log('🔮 API Service - generateStory called with data:', data)
    
    // Validate data before sending
    if (!data) {
      throw new Error('No data provided to generateStory')
    }
    
    if (!data.paintings || !Array.isArray(data.paintings) || data.paintings.length !== 3) {
      throw new Error(`Invalid paintings array: expected 3 paintings, got ${data.paintings ? data.paintings.length : 0}`)
    }
    
    for (let i = 0; i < data.paintings.length; i++) {
      const painting = data.paintings[i]
      if (!painting.url || !painting.title || !painting.artist) {
        throw new Error(`Painting ${i + 1} is missing required fields: url=${!!painting.url}, title=${!!painting.title}, artist=${!!painting.artist}`)
      }
    }
    
    if (!data.character) {
      throw new Error('No character provided')
    }
    
    if (!data.nickname || !data.nickname.trim()) {
      throw new Error('No nickname provided for story generation')
    }
    
    // Log emotion data for debugging
    console.log('🔮 API Service - Emotion data:', {
      emotion: data.emotion,
      probability: data.probability
    })
    
    console.log('✅ API Service - Data validation passed')
    
    return this.request('/generate-story', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  // Health check
  async checkHealth() {
    return this.request('/health')
  }

  // Status check
  async getStatus() {
    return this.request('/status')
  }
}

export default new ApiService() 