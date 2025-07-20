<template>
  <div v-if="show" class="loading">
    <div class="magic-cube-animation"></div>
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
  width: 60px;
  height: 60px;
  background-image: url('@/assets/images/magiccube.gif');
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