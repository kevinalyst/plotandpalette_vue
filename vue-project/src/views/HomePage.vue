<template>
  <div class="home-page">
    <!-- Main content container -->
    <div class="main-content">
      <!-- Title Section -->
      <div class="title-section">
        <h1 class="main-title">Plot & Palette</h1>
        <p class="subtitle">Discover the emotions and stories hidden in your photos</p>
      </div>

      <!-- Camera/Upload Section -->
      <div class="camera-section">
        <div class="camera-container">
          <!-- Camera preview -->
          <div v-if="showCamera" class="camera-preview">
            <video ref="videoElement" autoplay playsinline></video>
            <div class="camera-controls">
              <button @click="capturePhoto" class="capture-btn">
                <span class="capture-icon"></span>
              </button>
              <button @click="stopCamera" class="stop-camera-btn">Stop Camera</button>
            </div>
          </div>

          <!-- Upload area -->
          <div v-else class="upload-area" @dragover.prevent @drop="handleDrop">
            <div class="upload-content">
              <div class="upload-icon">📸</div>
              <h3>Take a photo or upload an image</h3>
              <p>Drag and drop an image here, or click to select</p>
              <input 
                ref="fileInput" 
                type="file" 
                accept="image/*" 
                @change="handleFileSelect"
                style="display: none"
              >
              <div class="upload-buttons">
                <button @click="startCamera" class="camera-btn">
                  📷 Take Photo
                </button>
                <button @click="$refs.fileInput.click()" class="upload-btn">
                  📁 Upload Image
                </button>
              </div>
            </div>
          </div>

          <!-- Preview captured/uploaded image -->
          <div v-if="capturedImage" class="image-preview">
            <img :src="capturedImage" alt="Captured image" />
            <div class="image-actions">
              <button @click="retakePhoto" class="retake-btn">Retake</button>
              <button @click="processImage" class="process-btn">Analyze Image</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Instructions Section -->
      <div class="instructions-section">
        <div class="instruction-card">
          <div class="instruction-icon">🎨</div>
          <h3>Color Analysis</h3>
          <p>Extract dominant colors from your image</p>
        </div>
        <div class="instruction-card">
          <div class="instruction-icon">😊</div>
          <h3>Emotion Detection</h3>
          <p>Discover the emotions your colors evoke</p>
        </div>
        <div class="instruction-card">
          <div class="instruction-icon">🖼️</div>
          <h3>Art Matching</h3>
          <p>Find paintings that match your palette</p>
        </div>
        <div class="instruction-card">
          <div class="instruction-icon">📖</div>
          <h3>Story Generation</h3>
          <p>Create stories inspired by your image</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, inject } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'HomePage',
  setup() {
    const router = useRouter()
    const showCamera = ref(false)
    const capturedImage = ref(null)
    const videoElement = ref(null)
    const fileInput = ref(null)
    const stream = ref(null)
    
    // Inject global state
    const setLoading = inject('setLoading')
    const setValidationMessage = inject('setValidationMessage')
    const setImageData = inject('setImageData')

    const startCamera = async () => {
      try {
        stream.value = await navigator.mediaDevices.getUserMedia({ 
          video: { facingMode: 'environment' } 
        })
        showCamera.value = true
        
        // Wait for next tick to ensure video element is rendered
        await new Promise(resolve => setTimeout(resolve, 100))
        if (videoElement.value) {
          videoElement.value.srcObject = stream.value
        }
      } catch (error) {
        console.error('Error accessing camera:', error)
        setValidationMessage('Camera access denied or not available')
      }
    }

    const stopCamera = () => {
      if (stream.value) {
        stream.value.getTracks().forEach(track => track.stop())
        stream.value = null
      }
      showCamera.value = false
    }

    const capturePhoto = () => {
      if (!videoElement.value) return

      const canvas = document.createElement('canvas')
      const context = canvas.getContext('2d')
      
      canvas.width = videoElement.value.videoWidth
      canvas.height = videoElement.value.videoHeight
      
      context.drawImage(videoElement.value, 0, 0)
      
      capturedImage.value = canvas.toDataURL('image/jpeg', 0.8)
      stopCamera()
    }

    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file) {
        processFile(file)
      }
    }

    const handleDrop = (event) => {
      event.preventDefault()
      const file = event.dataTransfer.files[0]
      if (file && file.type.startsWith('image/')) {
        processFile(file)
      }
    }

    const processFile = (file) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        capturedImage.value = e.target.result
      }
      reader.readAsDataURL(file)
    }

    const retakePhoto = () => {
      capturedImage.value = null
      // Reset file input
      if (fileInput.value) {
        fileInput.value.value = ''
      }
    }

    const processImage = async () => {
      if (!capturedImage.value) return

      setLoading(true, 'Processing your image...')
      
      try {
        // Convert base64 to blob
        const response = await fetch(capturedImage.value)
        const blob = await response.blob()
        
        // Create FormData
        const formData = new FormData()
        formData.append('image', blob, 'captured-image.jpg')
        
        // Send to server for processing
        const uploadResponse = await fetch('/api/upload', {
          method: 'POST',
          body: formData
        })
        
        if (!uploadResponse.ok) {
          throw new Error('Upload failed')
        }
        
        const result = await uploadResponse.json()
        
        // Store image data globally
        setImageData({
          originalImage: capturedImage.value,
          filename: result.filename,
          processedData: result
        })
        
        // Navigate to gradient page
        router.push('/gradient')
        
      } catch (error) {
        console.error('Error processing image:', error)
        setValidationMessage('Error processing image. Please try again.')
      } finally {
        setLoading(false)
      }
    }

    // Cleanup camera on unmount
    onUnmounted(() => {
      stopCamera()
    })

    return {
      showCamera,
      capturedImage,
      videoElement,
      fileInput,
      startCamera,
      stopCamera,
      capturePhoto,
      handleFileSelect,
      handleDrop,
      retakePhoto,
      processImage
    }
  }
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.main-content {
  max-width: 1200px;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
}

.title-section {
  text-align: center;
  color: white;
  margin-top: 40px;
}

.main-title {
  font-family: 'Poppins', sans-serif;
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.subtitle {
  font-family: 'Poppins', sans-serif;
  font-size: 1.2rem;
  font-weight: 300;
  opacity: 0.9;
}

.camera-section {
  width: 100%;
  max-width: 600px;
}

.camera-container {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 30px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.camera-preview {
  position: relative;
  border-radius: 15px;
  overflow: hidden;
}

.camera-preview video {
  width: 100%;
  height: 400px;
  object-fit: cover;
}

.camera-controls {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 15px;
  align-items: center;
}

.capture-btn {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: white;
  border: 4px solid rgba(255, 255, 255, 0.8);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.capture-btn:hover {
  transform: scale(1.1);
}

.capture-icon {
  width: 30px;
  height: 30px;
  background: #667eea;
  border-radius: 50%;
}

.stop-camera-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 25px;
  padding: 10px 20px;
  cursor: pointer;
  font-family: 'Poppins', sans-serif;
  transition: all 0.3s ease;
}

.stop-camera-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.upload-area {
  border: 2px dashed rgba(255, 255, 255, 0.3);
  border-radius: 15px;
  padding: 60px 40px;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
}

.upload-area:hover {
  border-color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.05);
}

.upload-content {
  color: white;
}

.upload-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.upload-content h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.upload-content p {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  opacity: 0.8;
  margin-bottom: 30px;
}

.upload-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.camera-btn, .upload-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 25px;
  padding: 12px 24px;
  cursor: pointer;
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.camera-btn:hover, .upload-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.image-preview {
  text-align: center;
}

.image-preview img {
  max-width: 100%;
  max-height: 400px;
  border-radius: 15px;
  margin-bottom: 20px;
}

.image-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.retake-btn, .process-btn {
  padding: 12px 24px;
  border-radius: 25px;
  border: none;
  cursor: pointer;
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.retake-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.process-btn {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  color: white;
}

.retake-btn:hover, .process-btn:hover {
  transform: translateY(-2px);
}

.instructions-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  width: 100%;
  max-width: 1000px;
}

.instruction-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 30px 20px;
  text-align: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.instruction-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.15);
}

.instruction-icon {
  font-size: 2.5rem;
  margin-bottom: 15px;
}

.instruction-card h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.2rem;
  font-weight: 600;
  color: white;
  margin-bottom: 10px;
}

.instruction-card p {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.4;
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .main-title {
    font-size: 2.5rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
  
  .camera-container {
    padding: 20px;
  }
  
  .upload-area {
    padding: 40px 20px;
  }
  
  .upload-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .instructions-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .main-title {
    font-size: 2rem;
  }
  
  .camera-preview video {
    height: 300px;
  }
  
  .capture-btn {
    width: 60px;
    height: 60px;
  }
  
  .capture-icon {
    width: 25px;
    height: 25px;
  }
}
</style> 