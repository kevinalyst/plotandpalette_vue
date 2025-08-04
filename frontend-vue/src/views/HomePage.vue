<template>
  <div class="homepage">
    <button class="logo-refresh-button" @click="refreshPage">
      <img src="@/assets/images/logo.png" alt="Logo" class="logo-image" />
    </button>

    <div class="get-in-touch-container" @click="getInTouch" v-if="!disableGetInTouch">
      <p>Get in touch</p>
    </div>
    <div class="people-container" @click="goToTeamPage" v-if="!disablePeople">
      <p>People</p>
    </div>
    <div class = "text-container">
    </div>
    <div class="colourbar-container">
      <img src="@/assets/images/colourbar.png" alt="Colour Bar" class="colourbar-image" />
    </div>
    <div class="homepage-controls">
      <button class="start-button" @click="startJourney" v-if="!disableStartJourney">Start the journey!</button>
    </div>
    <div class="paintings-container">
      <img src="@/assets/images/paintings.png" alt="Paintings" class="paintings-image" />
    </div>

    <!-- Get in touch form -->
    <div class="get-in-touch-form-container" v-if="isGetInTouch">
      <button class="get-in-touch-form-close" @click="closeForm">×</button>
      <div class="get-in-touch-form-container-left">
        <p class="get-in-touch-form-container-left-title">Send us a message</p>
        <div class="get-in-touch-form-container-left-line"/>
        <p class="get-in-touch-form-container-left-text">If you have any thoughts,<br/>we'd love to hear from you.</p>
        <div class="get-in-touch-form-container-left-email">
          <span class="email-icon">✉</span>
          <a href = "mailto:C.Ma20@newcastle.ac.uk">C.Ma20@newcastle.ac.uk</a>
        </div>
      </div>
      <div class="get-in-touch-form-container-right">
        <div class="get-in-touch-form-field">
          <label>Name</label>
          <input type="text" class="get-in-touch-form-input" />
        </div>
        <div class="get-in-touch-form-field">
          <label>Email</label>
          <input type="email" class="get-in-touch-form-input" />
        </div>
        <div class="get-in-touch-form-field">
          <label>Message</label>
          <textarea class="get-in-touch-form-textarea"></textarea>
        </div>
        <button class="get-in-touch-form-send-button">Send</button>
      </div>
    </div>

    <!-- User Information form -->
    <div class="user-information-form-container" v-if="isUserInformation">
      <button class="user-information-form-close" @click="closeForm">×</button>
      <h2 class="user-information-form-title">Tell us about yourself</h2>
      
      <div class="username-field">
        <label class="form-field-label">Create a username:</label>
        <input 
          type="text" 
          class="username-input" 
          v-model="userInformation.username"
          placeholder="Type here..."
          maxlength="50"
        />
        <p class="username-rule">* Minimum 6 characters with both letters and numbers</p>
      </div>
      
      <div class="user-information-form-grid">
        <div class="form-field">
          <label class="form-field-label">Age Range:</label>
          <select class="form-field-select" v-model="userInformation.age">
            <option value="" disabled selected>Select Options</option>
            <option value="18-24">18-24</option>
            <option value="25-34">25-34</option>
            <option value="35-44">35-44</option>
            <option value="45-54">45-54</option>
            <option value="55+">55+</option>
            <option value="prefer-not-to-say">Prefer not to say</option>
          </select>
        </div>
        
        <div class="form-field">
          <label class="form-field-label">Gender:</label>
          <select class="form-field-select" v-model="userInformation.gender">
            <option value="" disabled selected>Select Options</option>
            <option value="woman">Woman</option>
            <option value="man">Man</option>
            <option value="non-binary">Non-binary</option>
            <option value="prefer-not-to-say">Prefer not to say</option>
          </select>
        </div>
        
        <div class="form-field">
          <label class="form-field-label">Field of Study/Profession:</label>
          <p class="form-field-label" style="visibility: hidden;">&nbsp;</p>
          <select class="form-field-select" v-model="userInformation.fieldOfStudy">
            <option value="" disabled selected>Select Options</option>
            <option value="arts-humanities">Arts & Humanities</option>
            <option value="design-creative-arts">Design & Creative Arts</option>
            <option value="computer-science">Computer Science</option>
            <option value="social-sciences">Social Sciences</option>
            <option value="business-management">Business & Management</option>
            <option value="natural-sciences">Natural Sciences</option>
            <option value="healthcare-medicine">Healthcare & Medicine</option>
            <option value="education-research">Education & Research</option>
            <option value="engineering">Engineering</option>
            <option value="public-services">Public Services</option>
            <option value="other">Other</option>
            <option value="prefer-not-to-say">Prefer not to say</option>
          </select>
        </div>
        
        <div class="form-field">
          <label class="form-field-label">Art Engagement Frequency:</label>
            <p class="form-field-label">(in person or online)</p>
          <select class="form-field-select" v-model="userInformation.frequency">
            <option value="" disabled selected>Select Options</option>
            <option value="daily">Daily or almost daily</option>
            <option value="weekly">Weekly (1-3 times per week)</option>
            <option value="monthly">Monthly (1-3 times per month)</option>
            <option value="few-times-year">A few times a year (1-3 times per year)</option>
            <option value="rarely">Rarely (less than once a year)</option>
            <option value="first-time">First time (never)</option>
          </select>
        </div>
      </div>
      
      <button class="user-information-form-submit" @click="submitUserInformation" :disabled="!isUserInformationComplete">Submit</button>
      
      <div class="user-information-form-note">
        <p><em>*Please note:</em></p>
        <p>We will collect your <u>basic demographics</u> and <u>interaction logs</u>.</p>
        <p>All data is anonymised, securely stored until 2029, and used solely for academic research (Newcastle University Ethics Approval No. 54009/2023). Participation is voluntary – you may withdraw at any time!</p>
      </div>
    </div>
    
    <!-- GIF Preloading Spinner -->
    <LoadingSpinner
      :show="isGifPreloading"
      type="palette"
      message="Hang tight! The palettes are coming..."
    />


    <!-- <div class="homepage-content">
      <div class="colourbar-container">
        <img src="@/assets/images/colourbar.png" alt="Colour Bar" class="colourbar-image" />
      </div>
      <div class="paintings-container">
        <img src="@/assets/images/paintings.png" alt="Paintings" class="paintings-image" />
      </div>
      <div class="homepage-controls">
        <button class="start-button" @click="startJourney">Start the journey!</button>
      </div>
    </div> -->
  </div>
</template>

<script>
import ApiService from '@/services/api.js'
import GifPreloader from '@/services/gifPreloader.js'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

export default {
  name: 'HomePage',
  components: {
    LoadingSpinner
  },
  data() {
    return {
      isGetInTouch: false,
      isUserInformation: false,
      disableGetInTouch: false,
      disableStartJourney: false,
      disablePeople: false,
      isGifPreloading: false,
      


      userInformation: {
        username: '',
        age: '',
        gender: '',
        fieldOfStudy: '',
        frequency: '',
      },
    }
  },
  computed: {
    isUsernameValid() {
      const username = this.userInformation.username
      if (!username || username.length < 6) return false
      
      // Check if contains both letters and numbers
      const hasLetters = /[a-zA-Z]/.test(username)
      const hasNumbers = /[0-9]/.test(username)
      
      return hasLetters && hasNumbers
    },
    isUserInformationComplete() {
      return this.userInformation.username &&
             this.isUsernameValid &&
             this.userInformation.age && 
             this.userInformation.gender && 
             this.userInformation.fieldOfStudy && 
             this.userInformation.frequency
    }
  },
  methods: {
    closeForm() {
      this.isGetInTouch = false
      this.isUserInformation = false
      this.disableStartJourney = false
      this.disableGetInTouch = false
    },
    getInTouch() {
      this.isGetInTouch = true
      this.disableStartJourney = true
      this.disableGetInTouch = true
      // window.open('https://www.instagram.com/the_art_of_the_journey/', '_blank')
    },
    goToTeamPage() {
      this.$router.push('/team')
    },
    async startJourney() {
      // Check if username exists in localStorage first
      const existingUsername = localStorage.getItem('username')
      
      if (existingUsername) {
        console.log('👤 Username found in localStorage:', existingUsername)
        
        try {
          // Verify username exists in database
          console.log('🔍 Checking username in database...')
          const response = await ApiService.request('/username-check', {
            method: 'POST',
            body: JSON.stringify({
              username: existingUsername
            })
          })
          
          console.log('📊 Username check response:', response)
          
          if (response.success && response.username_exist) {
            console.log('✅ Returning user verified in database:', existingUsername)
            // Start GIF preloading for verified returning users
            await this.preloadGifsAndNavigate()
          } else {
            console.log('❌ Username not found in database, clearing localStorage')
            // Clear invalid username and show form
            localStorage.removeItem('username')
            this.isUserInformation = true
            this.disableStartJourney = true
            this.disableGetInTouch = true
          }
          
        } catch (error) {
          console.error('❌ Error checking username:', error)
          console.log('⚠️ Database error, clearing localStorage and showing form')
          // On error, clear localStorage and show form to be safe
          localStorage.removeItem('username')
          this.isUserInformation = true
          this.disableStartJourney = true
          this.disableGetInTouch = true
        }
      } else {
        console.log('👤 No username in localStorage, showing user information form')
        // Show user information form for new users
        this.isUserInformation = true
        this.disableStartJourney = true
        this.disableGetInTouch = true
      }
    },
    async submitUserInformation() {
      if (!this.isUserInformationComplete) return
      
      try {
        console.log('👤 Storing username and user information...')
        
        const response = await ApiService.request('/store-username', {
          method: 'POST',
          body: JSON.stringify({
            name: this.userInformation.username,
            age: this.userInformation.age,
            gender: this.userInformation.gender,
            fieldOfStudy: this.userInformation.fieldOfStudy,
            frequency: this.userInformation.frequency
          })
        })
        
        console.log('✅ Username stored:', response.username)
        
        // Store username for future use (persists across sessions)
        localStorage.setItem('username', response.username)
        
        // Navigate to gradient palette page with GIF preloading
        await this.preloadGifsAndNavigate()
        
      } catch (error) {
        console.error('❌ Error storing username:', error)
        alert('Failed to save user information. Please try again.')
      }
    },
    refreshPage() {
      this.$router.push('/article')
    },
    async testConnection() {
      try {
        console.log('🔗 Testing backend connection...')
        const response = await ApiService.checkHealth()
        console.log('✅ Backend connection successful!', response)
      } catch (error) {
        console.error('❌ Backend connection failed:', error)
        alert('❌ Backend connection failed. Check console for details.')
      }
    },
    async preloadGifsAndNavigate() {
      try {
        console.log('🎯 Starting GIF preloading process...')
        this.isGifPreloading = true
        
        // Preload first batch of 3 random GIFs
        const preloadedGifs = await GifPreloader.preloadRandomGifs(3)
        
        if (preloadedGifs.length > 0) {
          console.log('✅ GIFs preloaded successfully, navigating to gradient page')
          // Navigate to gradient palette page with preloaded GIFs
          this.$router.push('/gradient')
        } else {
          console.log('⚠️ No GIFs preloaded, navigating anyway')
          // Navigate even if preloading failed
          this.$router.push('/gradient')
        }
        
      } catch (error) {
        console.error('❌ Error preloading GIFs:', error)
        // Navigate to gradient page even if preloading fails
        this.$router.push('/gradient')
      } finally {
        this.isGifPreloading = false
      }
    }
  },
  async mounted() {
    // Ensure body has no-scroll class for homepage
    document.body.classList.add('no-scroll')
    
    // Test backend connection on page load
    await this.testConnection()
  },
  beforeUnmount() {
    // Remove no-scroll class when leaving
    document.body.classList.remove('no-scroll')
  }
}
</script>

<style scoped>

p{
  /* font-size: 0.8vw; */
  /* font-weight: 600; */
  color: black;
  font-family: 'Poppins', sans-serif;
}

a{
  text-decoration: underline;
}

.homepage {
  position: relative;
  width: 100vw;
  height: 100vh;
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
  outline: none;
  cursor: pointer;
  z-index: 100;
  transition: transform 0.3s ease;
}

.logo-refresh-button:hover {
  transform: scale(1.1);
}

/* Add these focus and active states */
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
  transition: transform 0.3s ease;  /* Add smooth rotation transition */
}

/* Add rotation effect when hovering the button */
.logo-refresh-button:hover .logo-image {
  transform: rotate(180deg);  /* Rotate 90 degrees clockwise */
}
.get-in-touch-container {
  position: absolute;
  top: 40px;
  right: 5vw;
  background: none;
  border: none;
  cursor: pointer;
  z-index: 100;
  transition: transform 0.3s ease;
  font-size: 1.1vw;
  /* font-weight: 600; */
  color: black;
  font-family: 'Poppins', sans-serif;
  
}

.get-in-touch-container:hover {
  transform: scale(1.1);
  cursor: pointer;
}

.people-container {
  position: absolute;
  top: 40px;
  right: 15vw;
  background: none;
  border: none;
  cursor: pointer;
  z-index: 100;
  transition: transform 0.3s ease;
  font-size: 1.1vw;
  color: black;
  font-family: 'Poppins', sans-serif;
}

.people-container:hover {
  transform: scale(1.1);
  cursor: pointer;
}

.get-in-touch-form-container {
  width: 800px;
  height: 500px;
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1000;
  background-color: #d3d3d3;
  display: flex;
  flex-direction: row;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.get-in-touch-form-close {
  position: absolute;
  top: 15px;
  right: 15px;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  z-index: 1001;
  color: black;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s ease;
}

.get-in-touch-form-close:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.get-in-touch-form-container-left {
  padding: 50px;
  width: 50%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  background-color: #a9a9a9;
}

.get-in-touch-form-container-left-title {
  font-size: 60px;
  font-weight: 300;
  color: black;
  font-family: 'Poppins', sans-serif;
  margin: 0;
  margin-bottom: 20px;
  line-height: 1.2;
}

.get-in-touch-form-container-left-line {
  width: 100%;
  height: 2px;
  background-color: black;
  margin-bottom: 30px;
}

.get-in-touch-form-container-left-text {
  font-size: 16px;
  color: black;
  font-family: 'Poppins', sans-serif;
  margin: 0;
  margin-bottom: auto;
  line-height: 1.4;
}

.get-in-touch-form-container-left-email {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  color: black;
  font-family: 'Poppins', sans-serif;
  margin-top: auto;
}

.email-icon {
  font-size: 40px;
  align-content: center;
  padding-bottom: 10px;
}

.get-in-touch-form-container-right {
  padding: 50px;
  width: 50%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background-color: #d3d3d3;
}

.get-in-touch-form-field {
  margin-bottom: 20px;
}

.get-in-touch-form-field label {
  display: block;
  font-size: 16px;
  color: black;
  font-family: 'Poppins', sans-serif;
  margin-bottom: 8px;
  font-weight: normal;
}

.get-in-touch-form-input {
  width: 100%;
  height: 40px;
  background-color: white;
  border: none;
  border-radius: 8px;
  padding: 0 15px;
  font-size: 14px;
  font-family: 'Poppins', sans-serif;
  outline: none;
  box-sizing: border-box;
}

.get-in-touch-form-textarea {
  width: 100%;
  height: 150px;
  background-color: white;
  border: none;
  border-radius: 8px;
  padding: 15px;
  font-size: 14px;
  font-family: 'Poppins', sans-serif;
  outline: none;
  resize: none;
  box-sizing: border-box;
}

.get-in-touch-form-send-button {
  align-self: flex-end;
  background-color: #8d9498;
  border: none;
  border-radius: 25px;
  padding: 12px 30px;
  color: white;
  font-size: 16px;
  font-family: 'Poppins', sans-serif;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.get-in-touch-form-send-button:hover {
  background-color: #7a7f83;
  transform: translateY(-2px);
}






.text-container {
  background-image: url('@/assets/images/backgroundtext.png');
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
  width: 100%;
  height: 100%;
  transform: translate(-50%, -50%); 
  position: absolute;
  top: 50%;
  left: 50%;
  z-index: 10;
}

.colourbar-container {
  
  position: absolute;
  top: 50%;
  left: 50%;
  z-index: 9;
}

.colourbar-image {
  width: 68vw;
  height: auto;
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





.paintings-container {
  margin-bottom: 30px;
  position: absolute;
  top: 50%;
  right: 20%;
  transform: translate(-50%, -50%);
  z-index: 10;
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
  width: 30vw;
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
  width: 30vw;
  height: auto;
  object-fit: contain;
}

.homepage-controls {
  position: absolute;
  bottom: 10%;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  margin-top: 20px;
}

.start-button {
  background: rgba(0, 0, 0, 0.15);
  border: 2px solid rgba(0, 0, 0, 0.3);
  border-radius: 50px;
  padding: 15px 30px;
  color: black;
  cursor: pointer;
  transition: all 0.3s ease;
  text-shadow: 0 2px 4px rgba(255, 255, 255, 0.3);
}

.start-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}
.user-information-form-container {
  width: 800px;
  height: 620px;
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1000;
  background-color: #c5c5c5;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  box-sizing: border-box;
}

.user-information-form-close {
  position: absolute;
  top: 20px;
  right: 20px;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: black;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s ease;
}

.user-information-form-close:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.user-information-form-title {
  font-size: 30px;
  font-weight: normal;
  color: black;
  font-family: 'Poppins', sans-serif;
  margin: 0;
  margin-bottom: 20px;
  text-align: center;
}

.username-field {
  width: 100%;
  max-width: 600px;
  margin-bottom: 30px;
}

.username-input {
  width: 100%;
  height: 35px;
  background-color: white;
  border: none;
  border-radius: 8px;
  padding: 0 15px;
  font-size: 16px;
  font-family: 'Poppins', sans-serif;
  color: black;
  outline: none;
  box-sizing: border-box;
  margin-bottom: 8px;
}

.username-input::placeholder {
  color: #999;
  font-style: italic;
}

.username-input:focus {
  color: black;
}

.username-rule {
  font-size: 14px;
  color: black;
  font-family: 'Poppins', sans-serif;
  margin: 0;
  font-style: italic;
}

.user-information-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px 40px;
  width: 100%;
  max-width: 600px;
  margin-bottom: 40px;
}

.form-field {
  display: flex;
  flex-direction: column;
}

.form-field-label {
  font-size: 16px;
  color: black;
  font-family: 'Poppins', sans-serif;
  margin-bottom: 5px;
  font-weight: normal;
}

.form-field-select {
  width: 100%;
  height: 35px;
  background-color: white;
  border: none;
  border-radius: 8px;
  padding: 0 15px;
  font-size: 16px;
  font-family: 'Poppins', sans-serif;
  color: #999;
  outline: none;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 12px center;
  background-repeat: no-repeat;
  background-size: 16px;
  box-sizing: border-box;
}

.form-field-select:focus {
  color: black;
}

.form-field-select option:not([disabled]) {
  color: black;
}

.user-information-form-submit {
  background-color: #a8a8a8;
  border: 1px solid black;
  border-radius: 80px;
  padding: 5px 25px;
  color: black;
  font-size: 16px;
  font-family: 'Poppins', sans-serif;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
  margin-bottom: 20px;
}

.user-information-form-submit:hover {
  background-color: #999;
  transform: translateY(-2px);
}

.user-information-form-submit:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  transform: none;
  opacity: 0.6;
}

.user-information-form-submit:disabled:hover {
  background-color: #ccc;
  transform: none;
}

.user-information-form-note {
  max-width: 600px;
  text-align: left;
  font-size: 14px;
  color: black;
  font-family: 'Poppins', sans-serif;
  font-style: italic;
  line-height: 1.4;
}

.user-information-form-note p {
  margin: 5px 0;
  font-size: 14px;
  color: black;
  text-shadow: none;
}

/* Global button focus disable */
button:focus {
  outline: none !important;
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