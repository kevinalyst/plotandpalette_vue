<template>
  <div class="loading-modal" v-if="visible">
    <div class="loading-overlay" @click="closeModal"></div>
    <div class="loading-content">
      <div class="loading-spinner"></div>
      <h3 class="loading-title">{{ title }}</h3>
      <p class="loading-message">{{ message }}</p>
      <div class="loading-dots">
        <span class="dot" :class="{ active: dots >= 1 }"></span>
        <span class="dot" :class="{ active: dots >= 2 }"></span>
        <span class="dot" :class="{ active: dots >= 3 }"></span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'

export default {
  name: 'LoadingModal',
  props: {
    message: {
      type: String,
      default: 'Loading...'
    },
    title: {
      type: String,
      default: 'Please wait'
    },
    closable: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close'],
  setup(props, { emit }) {
    const visible = ref(true)
    const dots = ref(0)
    let dotsInterval = null

    const closeModal = () => {
      if (props.closable) {
        visible.value = false
        emit('close')
      }
    }

    const startDotsAnimation = () => {
      dotsInterval = setInterval(() => {
        dots.value = (dots.value + 1) % 4
      }, 500)
    }

    const stopDotsAnimation = () => {
      if (dotsInterval) {
        clearInterval(dotsInterval)
        dotsInterval = null
      }
    }

    onMounted(() => {
      startDotsAnimation()
    })

    onUnmounted(() => {
      stopDotsAnimation()
    })

    return {
      visible,
      dots,
      closeModal
    }
  }
}
</script>

<style scoped>
.loading-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
}

.loading-content {
  position: relative;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  animation: scaleIn 0.3s ease-in-out;
  color: white;
  max-width: 400px;
  width: 90%;
}

@keyframes scaleIn {
  from {
    transform: scale(0.8);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid #FFD700;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-title {
  font-family: 'Poppins', sans-serif;
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 10px;
  color: white;
}

.loading-message {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 300;
  margin-bottom: 20px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.4;
}

.loading-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.dot.active {
  background: #FFD700;
  transform: scale(1.2);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .loading-content {
    padding: 30px 20px;
    max-width: 300px;
  }
  
  .loading-spinner {
    width: 50px;
    height: 50px;
  }
  
  .loading-title {
    font-size: 1.3rem;
  }
  
  .loading-message {
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .loading-content {
    padding: 25px 15px;
    max-width: 250px;
  }
  
  .loading-spinner {
    width: 40px;
    height: 40px;
  }
  
  .loading-title {
    font-size: 1.2rem;
  }
  
  .loading-message {
    font-size: 0.8rem;
  }
}

/* Pulsing animation for the entire content */
.loading-content {
  animation: scaleIn 0.3s ease-in-out, pulse 2s infinite 1s;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
}
</style> 