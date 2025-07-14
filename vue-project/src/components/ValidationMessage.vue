<template>
  <div class="validation-message" v-if="visible" :class="messageType">
    <div class="message-content">
      <div class="message-icon">
        <span v-if="messageType === 'success'">✅</span>
        <span v-else-if="messageType === 'error'">❌</span>
        <span v-else-if="messageType === 'warning'">⚠️</span>
        <span v-else>ℹ️</span>
      </div>
      <div class="message-text">
        <p>{{ message }}</p>
      </div>
      <button @click="closeMessage" class="close-btn">
        <span>×</span>
      </button>
    </div>
    <div class="progress-bar" :style="{ width: `${progress}%` }"></div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'

export default {
  name: 'ValidationMessage',
  props: {
    message: {
      type: String,
      required: true
    },
    type: {
      type: String,
      default: 'info',
      validator: value => ['success', 'error', 'warning', 'info'].includes(value)
    },
    duration: {
      type: Number,
      default: 3000
    },
    persistent: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close'],
  setup(props, { emit }) {
    const visible = ref(true)
    const progress = ref(100)
    let progressInterval = null
    let autoCloseTimeout = null

    const messageType = computed(() => {
      // Determine message type based on content if not explicitly set
      if (props.type !== 'info') return props.type
      
      const msg = props.message.toLowerCase()
      if (msg.includes('success') || msg.includes('complete') || msg.includes('saved')) {
        return 'success'
      } else if (msg.includes('error') || msg.includes('failed') || msg.includes('wrong')) {
        return 'error'
      } else if (msg.includes('warning') || msg.includes('caution')) {
        return 'warning'
      }
      return 'info'
    })

    const closeMessage = () => {
      visible.value = false
      clearTimers()
      emit('close')
    }

    const clearTimers = () => {
      if (progressInterval) {
        clearInterval(progressInterval)
        progressInterval = null
      }
      if (autoCloseTimeout) {
        clearTimeout(autoCloseTimeout)
        autoCloseTimeout = null
      }
    }

    const startProgressBar = () => {
      if (props.persistent) return
      
      const startTime = Date.now()
      const duration = props.duration
      
      progressInterval = setInterval(() => {
        const elapsed = Date.now() - startTime
        const remaining = Math.max(0, duration - elapsed)
        progress.value = (remaining / duration) * 100
        
        if (remaining <= 0) {
          closeMessage()
        }
      }, 50)
    }

    const setupAutoClose = () => {
      if (props.persistent) return
      
      autoCloseTimeout = setTimeout(() => {
        closeMessage()
      }, props.duration)
    }

    onMounted(() => {
      startProgressBar()
      setupAutoClose()
    })

    onUnmounted(() => {
      clearTimers()
    })

    return {
      visible,
      progress,
      messageType,
      closeMessage
    }
  }
}
</script>

<style scoped>
.validation-message {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 9998;
  max-width: 400px;
  min-width: 300px;
  border-radius: 12px;
  overflow: hidden;
  animation: slideInRight 0.3s ease-out;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.message-content {
  display: flex;
  align-items: center;
  padding: 15px;
  gap: 12px;
  color: white;
  font-family: 'Poppins', sans-serif;
  position: relative;
}

.message-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.message-text {
  flex: 1;
}

.message-text p {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 500;
  line-height: 1.4;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.progress-bar {
  height: 3px;
  background: rgba(255, 255, 255, 0.8);
  transition: width 0.05s linear;
  border-radius: 0 0 12px 12px;
}

/* Message type styles */
.validation-message.success {
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.9) 0%, rgba(56, 142, 60, 0.9) 100%);
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.validation-message.success .progress-bar {
  background: rgba(255, 255, 255, 0.9);
}

.validation-message.error {
  background: linear-gradient(135deg, rgba(244, 67, 54, 0.9) 0%, rgba(211, 47, 47, 0.9) 100%);
  border: 1px solid rgba(244, 67, 54, 0.3);
}

.validation-message.error .progress-bar {
  background: rgba(255, 255, 255, 0.9);
}

.validation-message.warning {
  background: linear-gradient(135deg, rgba(255, 152, 0, 0.9) 0%, rgba(245, 124, 0, 0.9) 100%);
  border: 1px solid rgba(255, 152, 0, 0.3);
}

.validation-message.warning .progress-bar {
  background: rgba(255, 255, 255, 0.9);
}

.validation-message.info {
  background: linear-gradient(135deg, rgba(33, 150, 243, 0.9) 0%, rgba(25, 118, 210, 0.9) 100%);
  border: 1px solid rgba(33, 150, 243, 0.3);
}

.validation-message.info .progress-bar {
  background: rgba(255, 255, 255, 0.9);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .validation-message {
    top: 70px;
    right: 15px;
    left: 15px;
    max-width: none;
    min-width: auto;
  }
  
  .message-content {
    padding: 12px;
  }
  
  .message-text p {
    font-size: 0.8rem;
  }
  
  .message-icon {
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .validation-message {
    top: 60px;
    right: 10px;
    left: 10px;
  }
  
  .message-content {
    padding: 10px;
    gap: 8px;
  }
  
  .message-text p {
    font-size: 0.75rem;
  }
}

/* Hover effect */
.validation-message:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(0, 0, 0, 0.4);
}

/* Animation for closing */
.validation-message.closing {
  animation: slideOutRight 0.3s ease-in forwards;
}

@keyframes slideOutRight {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}
</style> 