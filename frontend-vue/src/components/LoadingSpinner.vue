<template>
  <div v-if="show" class="loading">
    <div v-if="type === 'keyboard'" class="keyboard-animation"></div>
    <div v-else-if="type === 'dance'" class="dance-animation"></div>
    <div v-else-if="type === 'palette'" class="palette-animation"></div>
    <div v-else class="magic-cube-animation"></div>
    <p class="loading-analysis-text">{{ message }}</p>
  </div>
</template>

<script>
export default {
  name: 'LoadingSpinner',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    message: {
      type: String,
      default: 'Your palette is being analysed. Please hold on a moment...'
    },
    type: {
      type: String,
      default: 'magic-cube', // 'magic-cube', 'keyboard', 'dance', or 'palette'
      validator: (value) => ['magic-cube', 'keyboard', 'dance', 'palette'].includes(value)
    }
  }
}
</script>

<style scoped>
.loading {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.magic-cube-animation {
  width: 500px;
  height: 500px;
  background-image: url('@/assets/images/magiccube.gif');
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  margin-bottom: 20px;
}

.keyboard-animation {
  width: 600px;
  height: 450px;
  background-image: url('@/assets/images/keyboard.gif');
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}

.dance-animation {
  width: 500px;
  height: 400px;
  background-image: url('@/assets/images/dance.gif');
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  margin-bottom: 20px;
}

.palette-animation {
  width: 500px;
  height: 500px;
  background-image: url('@/assets/images/paletteloading.gif');
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  margin-bottom: 20px;
}

.loading-analysis-text {
  color: white;
  font-family: 'Poppins', sans-serif;
  font-size: 18px;
  font-weight: 300;
  text-align: center;
  margin: 0;
  padding: 0 20px;
}
</style> 