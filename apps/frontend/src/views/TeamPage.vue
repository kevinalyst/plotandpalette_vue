<template>
  <div class="team-page">
    <!-- Logo in top-left corner -->
    <button class="logo-refresh-button" @click="goToHomepage">
      <img src="@/assets/images/logo.png" alt="Logo" class="logo-image" />
    </button>

    <!-- Language Switcher -->
    <div class="language-switcher-container">
      <LanguageSwitcher />
    </div>

    <!-- Meet our team text -->
    <div class="meet-team-text">
      <h1>{{ $t('team.title') }}</h1>
      <div class="underline"></div>
    </div>

    <!-- Homepage container in top-right corner -->
    <div class="homepage-container" @click="goToHomepage">
      <p>{{ $t('team.homepage') }}</p>
    </div>

    <!-- Team image in center -->
    <div class="team-image-container">
      <img src="@/assets/images/teamimage.png" alt="Team Image" class="team-image" />
    </div>

    <!-- Team members section -->
    <div class="team-members-section">
      <!-- Marci Ma -->
      <div class="team-member">
        <div class="member-info">
          <h3>{{ $t('team.uiUxDesigner') }}</h3>
          <h2>Marci Ma</h2>
          <div class="email-container">
            <img src="@/assets/images/mail 2.png" alt="Email" class="email-icon" />
            <span class="email-text">C.Ma20@newcastle.ac.uk</span>
          </div>
          <div class="linkedin-container" @click="openLinkedIn('https://www.linkedin.com/in/marci-ma/')">
            <span class="linkedin-text">{{ $t('team.linkedinProfile') }}</span>
          </div>
        </div>
      </div>

      <!-- Jiacheng Cheng -->
      <div class="team-member">
        <div class="member-info">
          <h3>{{ $t('team.frontendDeveloper') }}</h3>
          <h2>Jiacheng Cheng</h2>
          <div class="email-container">
            <img src="@/assets/images/mail 2.png" alt="Email" class="email-icon" />
            <span class="email-text">c0045893@newcastle.ac.uk</span>
          </div>
          <div class="linkedin-container" @click="openLinkedIn('https://www.linkedin.com/in/jiacheng-cheng-677417309/')">
            <span class="linkedin-text">{{ $t('team.linkedinProfile') }}</span>
          </div>
        </div>
      </div>

      <!-- Kevin Li -->
      <div class="team-member">
        <div class="member-info">
          <h3>{{ $t('team.backendDeveloper') }}</h3>
          <h2>Kevin Li</h2>
          <div class="email-container">
            <img src="@/assets/images/mail 2.png" alt="Email" class="email-icon" />
            <span class="email-text">axiuluo40@gmail.com</span>
          </div>
          <div class="linkedin-container" @click="openLinkedIn('https://www.linkedin.com/in/kevin-li-8167381a6/')">
            <span class="linkedin-text">{{ $t('team.linkedinProfile') }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'

export default {
  name: 'TeamPage',
  components: {
    LanguageSwitcher
  },
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

/* Language Switcher */
.language-switcher-container {
  position: absolute;
  top: 40px;
  right: 15vw;
  z-index: 100;
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
  background: none;
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
  max-width: 80vw;
  max-height: 60vh;
  object-fit: contain;
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
}
</style>
