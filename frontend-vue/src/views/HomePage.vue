<template>
  <div class="homepage">
    <button class="logo-refresh-button" @click="refreshPage">
      <img src="@/assets/images/logo.png" alt="Logo" class="logo-image" />
    </button>
    <div class="homepage-content">
      <div class="colourbar-container">
        <img src="@/assets/images/colourbar.png" alt="Colour Bar" class="colourbar-image" />
      </div>
      <div class="paintings-container">
        <img src="@/assets/images/paintings.png" alt="Paintings" class="paintings-image" />
      </div>
      <div class="homepage-controls">
        <button class="start-button" @click="startJourney">Start the journey!</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomePage',
  methods: {
    startJourney() {
      this.$router.push('/gradient')
    },
    refreshPage() {
      this.$router.push('/')
    }
  },
  mounted() {
    // Ensure body has no-scroll class for homepage
    document.body.classList.add('no-scroll')
  },
  beforeUnmount() {
    // Remove no-scroll class when leaving
    document.body.classList.remove('no-scroll')
  }
}
</script>

<style scoped>
.homepage {
  position: relative;
  width: 100vw;
  height: 100vh;
  background-image: url('@/assets/images/backgroundtext.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.logo-refresh-button {
  position: absolute;
  top: 30px;
  left: 30px;
  background: none;
  border: none;
  cursor: pointer;
  z-index: 100;
  transition: transform 0.3s ease;
}

.logo-refresh-button:hover {
  transform: scale(1.1);
}

.logo-image {
  width: 60px;
  height: 60px;
  object-fit: contain;
}

.homepage-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  z-index: 10;
  position: relative;
}

.colourbar-container {
  margin-bottom: 20px;
}

.colourbar-image {
  max-width: 400px;
  height: auto;
  object-fit: contain;
}

.paintings-container {
  margin-bottom: 30px;
  position: relative;
  transition: opacity 0.3s ease;
}

.paintings-container:hover {
  opacity: 0.9;
}

/* Hover effect to change paintings.png to paintingsguide.png */
.paintings-container::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('@/assets/images/paintingsguide.png');
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.paintings-container:hover::after {
  opacity: 1;
}

.paintings-image {
  max-width: 600px;
  height: auto;
  object-fit: contain;
}

.homepage-controls {
  margin-top: 20px;
}

.start-button {
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
  color: white;
  border: none;
  padding: 15px 40px;
  font-size: 18px;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.start-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
  background: linear-gradient(45deg, #ff5252, #26a69a);
}

/* Responsive design */
@media (max-width: 768px) {
  .colourbar-image {
    max-width: 300px;
  }
  
  .paintings-image {
    max-width: 400px;
  }
  
  .start-button {
    padding: 12px 30px;
    font-size: 16px;
  }
  
  .logo-refresh-button {
    top: 20px;
    left: 20px;
  }
  
  .logo-image {
    width: 50px;
    height: 50px;
  }
}
</style> 