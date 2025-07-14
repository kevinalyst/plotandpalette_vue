<template>
  <div class="gradient-page">
    <div class="gradient-container">
      <!-- Header Section -->
      <div class="header-section">
        <h2 class="page-title">Color Gradient Analysis</h2>
        <p class="page-subtitle">Analyzing the color distribution in your image</p>
      </div>

      <!-- Image Display -->
      <div class="image-section">
        <div class="original-image-container">
          <img :src="imageData?.originalImage" alt="Original image" class="original-image" />
          <div class="image-info">
            <p>Original Image</p>
          </div>
        </div>
      </div>

      <!-- Gradient Visualization -->
      <div class="gradient-visualization">
        <div class="gradient-header">
          <h3>Color Gradient</h3>
          <p>Extracted color palette from your image</p>
        </div>
        
        <div class="gradient-display">
          <div 
            class="gradient-bar"
            :style="{ background: gradientStyle }"
          ></div>
          
          <div class="color-markers">
            <div 
              v-for="(color, index) in extractedColors" 
              :key="index"
              class="color-marker"
              :style="{ left: `${(index / (extractedColors.length - 1)) * 100}%` }"
            >
              <div 
                class="color-dot"
                :style="{ backgroundColor: color.hex }"
              ></div>
              <div class="color-label">
                <span class="color-name">{{ color.name }}</span>
                <span class="color-percentage">{{ color.percentage }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Color Analysis -->
      <div class="color-analysis">
        <h3>Dominant Colors</h3>
        <div class="color-grid">
          <div 
            v-for="(color, index) in extractedColors" 
            :key="index"
            class="color-card"
          >
            <div 
              class="color-swatch"
              :style="{ backgroundColor: color.hex }"
            ></div>
            <div class="color-details">
              <h4>{{ color.name }}</h4>
              <p class="color-hex">{{ color.hex }}</p>
              <p class="color-percentage">{{ color.percentage }}%</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <div class="navigation-section">
        <button @click="goBack" class="back-btn">
          ← Back to Upload
        </button>
        <button @click="proceedToPalette" class="continue-btn">
          Continue to Palette →
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'GradientPage',
  setup() {
    const router = useRouter()
    const extractedColors = ref([])
    const isLoading = ref(false)
    
    // Inject global state
    const imageData = inject('imageData')
    const setLoading = inject('setLoading')
    const setValidationMessage = inject('setValidationMessage')

    // Computed gradient style
    const gradientStyle = computed(() => {
      if (extractedColors.value.length === 0) return ''
      
      const colors = extractedColors.value.map(color => color.hex)
      return `linear-gradient(90deg, ${colors.join(', ')})`
    })

    // Extract colors from image
    const extractColors = async () => {
      if (!imageData.value?.originalImage) {
        setValidationMessage('No image data available')
        router.push('/')
        return
      }

      setLoading(true, 'Extracting colors from your image...')
      
      try {
        // Create canvas to analyze image
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')
        const img = new Image()
        
        img.onload = () => {
          canvas.width = img.width
          canvas.height = img.height
          ctx.drawImage(img, 0, 0)
          
          // Sample colors from image
          const colors = sampleColorsFromCanvas(canvas, ctx)
          extractedColors.value = colors
          
          setLoading(false)
        }
        
        img.src = imageData.value.originalImage
        
      } catch (error) {
        console.error('Error extracting colors:', error)
        setValidationMessage('Error analyzing image colors')
        setLoading(false)
      }
    }

    // Sample colors from canvas
    const sampleColorsFromCanvas = (canvas, ctx) => {
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
      const data = imageData.data
      const colorMap = new Map()
      
      // Sample every 10th pixel to improve performance
      for (let i = 0; i < data.length; i += 40) {
        const r = data[i]
        const g = data[i + 1]
        const b = data[i + 2]
        const a = data[i + 3]
        
        if (a > 128) { // Only consider non-transparent pixels
          const hex = rgbToHex(r, g, b)
          colorMap.set(hex, (colorMap.get(hex) || 0) + 1)
        }
      }
      
      // Get top 6 colors
      const sortedColors = Array.from(colorMap.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 6)
      
      const totalPixels = sortedColors.reduce((sum, [, count]) => sum + count, 0)
      
      return sortedColors.map(([hex, count]) => ({
        hex,
        name: getColorName(hex),
        percentage: Math.round((count / totalPixels) * 100)
      }))
    }

    // Convert RGB to hex
    const rgbToHex = (r, g, b) => {
      return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)
    }

    // Get color name (simplified)
    const getColorName = (hex) => {
      const colorNames = {
        '#FF0000': 'Red',
        '#00FF00': 'Green',
        '#0000FF': 'Blue',
        '#FFFF00': 'Yellow',
        '#FF00FF': 'Magenta',
        '#00FFFF': 'Cyan',
        '#000000': 'Black',
        '#FFFFFF': 'White',
        '#808080': 'Gray',
        '#FFA500': 'Orange',
        '#800080': 'Purple',
        '#FFC0CB': 'Pink',
        '#A52A2A': 'Brown',
        '#90EE90': 'Light Green',
        '#87CEEB': 'Sky Blue'
      }
      
      // Find closest color name (simplified approach)
      const rgb = hexToRgb(hex)
      if (!rgb) return 'Unknown'
      
      const { r, g, b } = rgb
      
      if (r > 200 && g < 100 && b < 100) return 'Red'
      if (r < 100 && g > 200 && b < 100) return 'Green'
      if (r < 100 && g < 100 && b > 200) return 'Blue'
      if (r > 200 && g > 200 && b < 100) return 'Yellow'
      if (r > 200 && g < 100 && b > 200) return 'Magenta'
      if (r < 100 && g > 200 && b > 200) return 'Cyan'
      if (r > 150 && g > 100 && b < 100) return 'Orange'
      if (r > 100 && g < 100 && b > 150) return 'Purple'
      if (r > 200 && g > 150 && b > 150) return 'Pink'
      if (r < 100 && g < 100 && b < 100) return 'Dark'
      if (r > 200 && g > 200 && b > 200) return 'Light'
      
      return 'Mixed'
    }

    // Convert hex to RGB
    const hexToRgb = (hex) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
      return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
      } : null
    }

    const goBack = () => {
      router.push('/')
    }

    const proceedToPalette = () => {
      if (extractedColors.value.length === 0) {
        setValidationMessage('Please wait for color extraction to complete')
        return
      }
      
      // Store extracted colors in global state
      imageData.value.extractedColors = extractedColors.value
      router.push('/palette')
    }

    onMounted(() => {
      extractColors()
    })

    return {
      extractedColors,
      gradientStyle,
      imageData,
      isLoading,
      goBack,
      proceedToPalette
    }
  }
}
</script>

<style scoped>
.gradient-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.gradient-container {
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

.image-section {
  display: flex;
  justify-content: center;
  margin-bottom: 40px;
}

.original-image-container {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  text-align: center;
}

.original-image {
  max-width: 400px;
  max-height: 300px;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.image-info {
  margin-top: 15px;
}

.image-info p {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 500;
  opacity: 0.9;
}

.gradient-visualization {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 40px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.gradient-header {
  text-align: center;
  margin-bottom: 30px;
}

.gradient-header h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.gradient-header p {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  opacity: 0.8;
}

.gradient-display {
  position: relative;
  margin-bottom: 40px;
}

.gradient-bar {
  height: 80px;
  border-radius: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.color-markers {
  position: relative;
  margin-top: 20px;
}

.color-marker {
  position: absolute;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.color-dot {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  margin-bottom: 10px;
}

.color-label {
  text-align: center;
  background: rgba(0, 0, 0, 0.5);
  padding: 5px 10px;
  border-radius: 10px;
  backdrop-filter: blur(5px);
}

.color-name {
  display: block;
  font-family: 'Poppins', sans-serif;
  font-size: 0.8rem;
  font-weight: 600;
}

.color-percentage {
  display: block;
  font-family: 'Poppins', sans-serif;
  font-size: 0.7rem;
  opacity: 0.8;
}

.color-analysis {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 40px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.color-analysis h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 20px;
  text-align: center;
}

.color-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 20px;
}

.color-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.color-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.15);
}

.color-swatch {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  margin: 0 auto 15px;
  border: 3px solid white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.color-details h4 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 5px;
}

.color-hex {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  opacity: 0.8;
  margin-bottom: 5px;
}

.color-percentage {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: #FFD700;
}

.navigation-section {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-top: 40px;
}

.back-btn, .continue-btn {
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

.continue-btn {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

.back-btn:hover, .continue-btn:hover {
  transform: translateY(-2px);
}

.continue-btn:hover {
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }
  
  .original-image {
    max-width: 300px;
    max-height: 200px;
  }
  
  .gradient-visualization, .color-analysis {
    padding: 20px;
  }
  
  .color-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
  }
  
  .navigation-section {
    flex-direction: column;
  }
  
  .back-btn, .continue-btn {
    width: 100%;
    padding: 12px 20px;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.8rem;
  }
  
  .original-image {
    max-width: 250px;
    max-height: 150px;
  }
  
  .gradient-bar {
    height: 60px;
  }
  
  .color-grid {
    grid-template-columns: 1fr;
  }
  
  .color-marker {
    display: none; /* Hide markers on very small screens */
  }
}
</style> 