<template>
  <div class="logo-refresh-button">
    <button @click="refreshApp" class="logo-btn" :class="{ 'spinning': isRefreshing }">
      <div class="logo-container">
        <div class="logo-icon">🎨</div>
        <div class="logo-text">
          <span class="logo-main">Plot & Palette</span>
          <span class="logo-sub">Color Stories</span>
        </div>
      </div>
    </button>
  </div>
</template>

<script>
import { ref, inject } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'LogoRefreshButton',
  setup() {
    const router = useRouter()
    const isRefreshing = ref(false)
    
    // Inject global methods
    const resetAppState = inject('resetAppState', () => {})
    const showValidation = inject('showValidation', () => {})

    const refreshApp = async () => {
      isRefreshing.value = true
      
      try {
        // Reset global state
        resetAppState()
        
        // Navigate to home
        await router.push('/')
        
        // Show success message
        showValidation('Application refreshed!')
        
      } catch (error) {
        console.error('Error refreshing app:', error)
        showValidation('Error refreshing application')
      } finally {
        // Stop spinning animation
        setTimeout(() => {
          isRefreshing.value = false
        }, 1000)
      }
    }

    return {
      isRefreshing,
      refreshApp
    }
  }
}
</script>

<style scoped>
.logo-refresh-button {
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 1000;
}

.logo-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  padding: 10px 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  color: white;
  font-family: 'Poppins', sans-serif;
}

.logo-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.logo-btn.spinning {
  animation: logoSpin 1s ease-in-out;
}

@keyframes logoSpin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 1.5rem;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.logo-main {
  font-size: 0.9rem;
  font-weight: 600;
  color: white;
}

.logo-sub {
  font-size: 0.7rem;
  font-weight: 300;
  color: rgba(255, 255, 255, 0.8);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .logo-refresh-button {
    top: 15px;
    left: 15px;
  }
  
  .logo-btn {
    padding: 8px 12px;
  }
  
  .logo-icon {
    font-size: 1.2rem;
  }
  
  .logo-main {
    font-size: 0.8rem;
  }
  
  .logo-sub {
    font-size: 0.6rem;
  }
}

@media (max-width: 480px) {
  .logo-text {
    display: none;
  }
  
  .logo-container {
    gap: 0;
  }
  
  .logo-icon {
    font-size: 1.5rem;
  }
}
</style> 