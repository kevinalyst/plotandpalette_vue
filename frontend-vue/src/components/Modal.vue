<template>
  <div v-if="show" class="modal">
    <div class="modal-content">
      <h3>{{ title }}</h3>
      <p v-if="message">{{ message }}</p>
      <slot></slot>
      <div class="modal-buttons">
        <button 
          v-for="button in buttons" 
          :key="button.text"
          :class="['modal-btn', button.secondary ? 'secondary' : '']"
          @click="button.action"
        >
          {{ button.text }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Modal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      required: true
    },
    message: {
      type: String,
      default: ''
    },
    buttons: {
      type: Array,
      default: () => []
    }
  }
}
</script>

<style scoped>
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 12px;
  text-align: center;
  max-width: 500px;
  margin: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-content h3 {
  margin: 0 0 15px 0;
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  color: #333;
}

.modal-content p {
  margin: 0 0 20px 0;
  font-family: 'Poppins', sans-serif;
  color: #666;
  line-height: 1.6;
}

.modal-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.modal-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease;
  background: #007bff;
  color: white;
}

.modal-btn:hover {
  background: #0056b3;
}

.modal-btn.secondary {
  background: #6c757d;
  color: white;
}

.modal-btn.secondary:hover {
  background: #545b62;
}
</style> 