<template>
  <div class="team-page">
    <!-- Background image -->
    <div class="article-background"></div>
    <!-- Logo in top-left corner -->
    <button class="logo-refresh-button" @click="goToHomepage">
      <img src="@/assets/images/logo.png" alt="Logo" class="logo-image" />
    </button>

    <!-- Meet our team text -->
    <div class="meet-team-text">
      <h1>Article</h1>
      <div class="underline"></div>
    </div>

    <!-- Homepage container in top-right corner -->
    <div class="homepage-container" @click="goToHomepage">
      <p>Homepage</p>
    </div>

    <!-- Team image in center -->
    <div class="team-image-container">
      <img src="@/assets/images/flash.gif" alt="Team Image" class="team-image" />
    </div>

    <!-- Coming soon text -->
    <div class="coming-soon-text">
      Full paper of this research coming soon...
    </div>
  </div>
</template>

<script>
export default {
  name: 'TeamPage',
  methods: {
    goToHomepage() {
      this.$router.push('/')
    },
    openLinkedIn(url) {
      window.open(url, '_blank')
    }
  }
}
</script>

<style scoped>
.team-page {
  position: relative;
  width: 100vw;
  height: 100vh;
  background: white;
  overflow: hidden;
}

.article-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-image: url('@/assets/images/articlebackground.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: 0;
}

/* Logo button - same style as homepage */
.logo-refresh-button {
  position: absolute;
  top: 30px;
  left: 30px;
  background: none;
  border: none;
  outline: none;
  cursor: pointer;
  z-index: 100;
  transition: transform 0.3s ease;
}

.logo-refresh-button:hover {
  transform: scale(1.1);
}

.logo-refresh-button:focus {
  outline: none;
}

.logo-refresh-button:active {
  outline: none;
  transform: scale(0.95);
}

.logo-image {
  width: 40px;
  height: 40px;
  object-fit: contain;
  transition: transform 0.3s ease;
}

.logo-refresh-button:hover .logo-image {
  transform: rotate(180deg);
}

/* Meet our team text */
.meet-team-text {
  position: absolute;
  top: 20px;
  left: 120px;
  z-index: 100;
}

.meet-team-text h1 {
  font-family: 'Poppins', sans-serif;
  font-weight: 260;
  font-size: 60px;
  color: black;
  background-color: white;
  margin: 0;
  margin-bottom: 10px;
}

.underline {
  width: 100%;
  height: 2px;
  background-color: black;
}

/* Homepage container - same style as People container */
.homepage-container {
  position: absolute;
  top: 40px;
  right: 5vw;
  background: white;
  border: none;
  cursor: pointer;
  z-index: 100;
  transition: transform 0.3s ease;
  font-size: 1.1vw;
  color: black;
  text-shadow: 0 2px 4px rgba(255, 255, 255, 0.3);
  font-family: 'Poppins', sans-serif;
}

.homepage-container:hover {
  transform: scale(1.1);
  cursor: pointer;
}

/* Team image in center */
.team-image-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1;
}

.team-image {
  max-width: 30vw;
  max-height: auto;
  object-fit: contain;
}

.coming-soon-text {
  position: absolute;
  left: 50%;
  top: calc(50% + 200px);
  transform: translateX(-50%);
  font-family: 'Poppins', sans-serif;
  font-style: italic;
  font-size: 2rem;
  color: #222;
  background: rgba(255,255,255,0.7);
  padding: 18px 36px;
  border-radius: 16px;
  z-index: 2;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

/* Team members section */
.team-members-section {
  position: absolute;
  bottom: 40px;
  left: 55%;
  transform: translateX(-50%);
  display: flex;
  justify-content: space-between;
  width: 90vw;
  max-width: 1400px;
  z-index: 10;
}

.team-member {
  flex: 1;
  margin: 0 20px;
  text-align: left;
}

.member-info h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 14px;
  color: #666;
  margin: 0 0 5px 0;
  font-weight: 400;
}

.member-info h2 {
  font-family: 'Poppins', sans-serif;
  font-size: 24px;
  color: black;
  margin: 0 0 15px 0;
  font-weight: 600;
}

.email-container {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.email-icon {
  width: 20px;
  height: 20px;
  margin-right: 8px;
  object-fit: contain;
}

.email-text {
  font-family: 'Poppins', sans-serif;
  font-size: 14px;
  color: black;
  text-decoration: underline;
}

.linkedin-container {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.linkedin-container:hover {
  transform: translateY(-1px);
}

.linkedin-text {
  font-family: 'Poppins', sans-serif;
  font-size: 14px;
  color: black;
  text-decoration: underline;
}

/* Global button focus disable */
button:focus {
  outline: none !important;
}

/* Responsive design */
@media (max-width: 768px) {
  .team-members-section {
    flex-direction: column;
    align-items: center;
    width: 95vw;
    gap: 20px;
  }
  
  .team-member {
    margin: 0;
    text-align: center;
  }
  
  .homepage-container {
    font-size: 16px;
    right: 20px;
  }
  
  .member-info h2 {
    font-size: 20px;
  }
  
  .meet-team-text {
    left: 80px;
    top: 35px;
  }
  
  .meet-team-text h1 {
    font-size: 32px;
  }
  .coming-soon-text {
    font-size: 1.1rem;
    padding: 10px 12px;
    top: calc(50% + 120px);
  }
}
</style> 