<template>
    <div class="feedback-page">
        <!-- Prolific completion modal (shown only for Prolific participants after successful submit) -->
        <div v-if="showProlificModal" class="prolific-modal-overlay">
          <div class="prolific-modal">
            <h2>Thanks for your participation!</h2>
            <p>
              Here is your Prolific redirect link:
              <a :href="prolificRedirectUrl" target="_blank" rel="noopener">Open redirect</a>
            </p>
            <p>
              Or copy this completion code:
              <strong>{{ prolificCompletionCode }}</strong>
            </p>
            <div class="prolific-modal-actions">
              <button @click="openProlific" class="start-button">Open Redirect</button>
              <button @click="copyCompletionCode" class="maybe-later-button">Copy Code</button>
              <button @click="closeProlificModal" class="maybe-later-button">Close</button>
            </div>
          </div>
        </div>
        
        <div class="feedback-page-container">
            <div class="feedback-page-content-container">
                <div v-if="step === 1" class="feedback-page-content feedback-first-page">
                    <div class="feedback-first-page-header">
                        <h1>Share Your Experience with Plot & Palette!</h1>
                        <div class="title-underline"></div>
                    </div>
                    
                    <p class="feedback-description">Thank you for exploring Plot & Palette! Your feedback will help us improve this artistic 
                        journey for future users.</p>
                    
                    <p class="feedback-intro">This short questionnaire includes 13 rating questions and 2 open-ended questions.</p>
                    
                    <div class="scorebar-container">
                        <img src="@/assets/images/scorebar.png" alt="Score Bar" class="scorebar-image" />
                    </div>
                    
                    <p class="feedback-instruction">Please respond based on your immediate impressions.</p>
                    
                    <p class="feedback-declaration">*All data is anonymised, securely stored until 2029, and used only for academic research (Newcastle University Ethics Approval No. 54009/2023). Participation is voluntary—you may close this page at any time.</p>
                </div>
                <div v-if="step === 2" class="feedback-page-content feedback-second-page">
                    <button class="close-button" @click="goToFirstPage">
                        <img src="@/assets/images/closebutton.png" alt="Close" class="close-button-image" />
                    </button>
                    <h1>Part 1: System Usability & Interface Design</h1>
                    <div class="title-underline"></div>
                    <div class="feedback-page-content-question feedback-question-1">
                        <p> 01. I thought the website was easy to use.</p>
                        <div class="feedback-question-options">
                            <div class="feedback-question-option" :class="{ 'selected': answers.q1 === 1 }" @click="answers.q1 = 1">
                                <p>1</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q1 === 2 }" @click="answers.q1 = 2">
                                <p>2</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q1 === 3 }" @click="answers.q1 = 3">
                                <p>3</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q1 === 4 }" @click="answers.q1 = 4">
                                <p>4</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q1 === 5 }" @click="answers.q1 = 5">
                                <p>5</p>
                            </div>
                        </div>
                    </div>
                    <div class="feedback-page-content-question feedback-question-2">
                        <p> 02. I could naviagte and interact with the website smoothly.</p>
                        <div class="feedback-question-options">
                            <div class="feedback-question-option" :class="{ 'selected': answers.q2 === 1 }" @click="answers.q2 = 1">
                                <p>1</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q2 === 2 }" @click="answers.q2 = 2">
                                <p>2</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q2 === 3 }" @click="answers.q2 = 3">
                                <p>3</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q2 === 4 }" @click="answers.q2 = 4">
                                <p>4</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q2 === 5 }" @click="answers.q2 = 5">
                                <p>5</p>
                            </div>
                        </div>
                    </div>
                    <div class="feedback-page-content-question feedback-question-3">
                        <p> 03. The website's visual design was aesthetically pleasing.</p>
                        <div class="feedback-question-options">
                            <div class="feedback-question-option" :class="{ 'selected': answers.q3 === 1 }" @click="answers.q3 = 1">
                                <p>1</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q3 === 2 }" @click="answers.q3 = 2">
                                <p>2</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q3 === 3 }" @click="answers.q3 = 3">
                                <p>3</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q3 === 4 }" @click="answers.q3 = 4">
                                <p>4</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q3 === 5 }" @click="answers.q3 = 5">
                                <p>5</p>
                            </div>
                        </div>
                    </div>

                </div>
                <div v-if="step === 3" class="feedback-page-content feedback-third-page">
                    <button class="close-button" @click="goToFirstPage">
                        <img src="@/assets/images/closebutton.png" alt="Close" class="close-button-image" />
                    </button>
                    <h1>Part 2: Core Features & Personalisation</h1>
                    <div class="title-underline"></div>
                    <div class="feedback-page-content-question feedback-question-4">
                        <p> 04. I could find the perfect palette that reasonates with me.</p>
                        <div class="feedback-question-options">
                            <div class="feedback-question-option" :class="{ 'selected': answers.q4 === 1 }" @click="answers.q4 = 1">
                                <p>1</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q4 === 2 }" @click="answers.q4 = 2">
                                <p>2</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q4 === 3 }" @click="answers.q4 = 3">
                                <p>3</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q4 === 4 }" @click="answers.q4 = 4">
                                <p>4</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q4 === 5 }" @click="answers.q4 = 5">
                                <p>5</p>
                            </div>
                        </div>
                    </div>
                    <div class="feedback-page-content-question feedback-question-5">
                        <p> 05. The colour extractions and emotion predictions from my captured palette were insightful.</p>
                        <div class="feedback-question-options">
                            <div class="feedback-question-option" :class="{ 'selected': answers.q5 === 1 }" @click="answers.q5 = 1">
                                <p>1</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q5 === 2 }" @click="answers.q5 = 2">
                                <p>2</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q5 === 3 }" @click="answers.q5 = 3">
                                <p>3</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q5 === 4 }" @click="answers.q5 = 4">
                                <p>4</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q5 === 5 }" @click="answers.q5 = 5">
                                <p>5</p>
                            </div>
                        </div>
                    </div>
                    
                </div>
                <div v-if="step === 4" class="feedback-page-content feedback-fourth-page">
                    <button class="close-button" @click="goToFirstPage">
                        <img src="@/assets/images/closebutton.png" alt="Close" class="close-button-image" />
                    </button>
                    <h1>Part 2: Core Features & Personalisation</h1>
                    <div class="title-underline"></div>
                    <div class="feedback-page-content-question feedback-question-6">
                        <p> 06. The paintings recommended to me were a good match for the colour palette I captured.</p>
                        <div class="feedback-question-options">
                            <div class="feedback-question-option" :class="{ 'selected': answers.q6 === 1 }" @click="answers.q6 = 1">
                                <p>1</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q6 === 2 }" @click="answers.q6 = 2">
                                <p>2</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q6 === 3 }" @click="answers.q6 = 3">
                                <p>3</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q6 === 4 }" @click="answers.q6 = 4">
                                <p>4</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q6 === 5 }" @click="answers.q6 = 5">
                                <p>5</p>
                            </div>
                        </div>
                    </div>
                    <div class="feedback-page-content-question feedback-question-7">
                        <p> 07. The generated story was consistent with the emotion, paintings, and narrative style I selected.</p>
                        <div class="feedback-question-options">
                            <div class="feedback-question-option" :class="{ 'selected': answers.q7 === 1 }" @click="answers.q7 = 1">
                                <p>1</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q7 === 2 }" @click="answers.q7 = 2">
                                <p>2</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q7 === 3 }" @click="answers.q7 = 3">
                                <p>3</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q7 === 4 }" @click="answers.q7 = 4">
                                <p>4</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q7 === 5 }" @click="answers.q7 = 5">
                                <p>5</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div v-if="step === 5" class="feedback-page-content feedback-fifth-page">
                    <button class="close-button" @click="goToFirstPage">
                        <img src="@/assets/images/closebutton.png" alt="Close" class="close-button-image" />
                    </button>
                    <h1>Part 3: Emotional & Artistic Experience</h1>
                    <div class="title-underline"></div>
                    <div class="feedback-page-content-question feedback-question-8">
                        <p> 08. Throughout the experience with Plot & Palette, it evoked a range of emotional responses for me (any emotions).</p>
                        <div class="feedback-question-options">
                            <div class="feedback-question-option" :class="{ 'selected': answers.q8 === 1 }" @click="answers.q8 = 1">
                                <p>1</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q8 === 2 }" @click="answers.q8 = 2">
                                <p>2</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q8 === 3 }" @click="answers.q8 = 3">
                                <p>3</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q8 === 4 }" @click="answers.q8 = 4">
                                <p>4</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q8 === 5 }" @click="answers.q8 = 5">
                                <p>5</p>
                            </div>
                        </div>
                    </div>
                    <div class="feedback-page-content-question feedback-question-9">
                        <p> 09. The experience of creating stories from colour palettes was engaging and stimulating.</p>
                        <div class="feedback-question-options">
                            <div class="feedback-question-option" :class="{ 'selected': answers.q9 === 1 }" @click="answers.q9 = 1">
                                <p>1</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q9 === 2 }" @click="answers.q9 = 2">
                                <p>2</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q9 === 3 }" @click="answers.q9 = 3">
                                <p>3</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q9 === 4 }" @click="answers.q9 = 4">
                                <p>4</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q9 === 5 }" @click="answers.q9 = 5">
                                <p>5</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div v-if="step === 6" class="feedback-page-content feedback-sixth-page">
                    <button class="close-button" @click="goToFirstPage">
                        <img src="@/assets/images/closebutton.png" alt="Close" class="close-button-image" />
                    </button>
                    <h1>Part 3: Emotional & Artistic Experience</h1>
                    <div class="title-underline"></div>
                    <div class="feedback-page-content-question feedback-question-10">
                        <p> 10. I felt immersed in the journey through colours - emotions - arts - stories.</p>
                        <div class="feedback-question-options">
                            <div class="feedback-question-option" :class="{ 'selected': answers.q10 === 1 }" @click="answers.q10 = 1">
                                <p>1</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q10 === 2 }" @click="answers.q10 = 2">
                                <p>2</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q10 === 3 }" @click="answers.q10 = 3">
                                <p>3</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q10 === 4 }" @click="answers.q10 = 4">
                                <p>4</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q10 === 5 }" @click="answers.q10 = 5">
                                <p>5</p>
                            </div>
                        </div>
                    </div>
                    <div class="feedback-page-content-question feedback-question-11">
                        <p> 11. The experience with Plot & Palette offered me a meaningful and inspiring way to discover and appreciate art.</p>
                        <div class="feedback-question-options">
                            <div class="feedback-question-option" :class="{ 'selected': answers.q11 === 1 }" @click="answers.q11 = 1">
                                <p>1</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q11 === 2 }" @click="answers.q11 = 2">
                                <p>2</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q11 === 3 }" @click="answers.q11 = 3">
                                <p>3</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q11 === 4 }" @click="answers.q11 = 4">
                                <p>4</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q11 === 5 }" @click="answers.q11 = 5">
                                <p>5</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div v-if="step === 7" class="feedback-page-content feedback-seventh-page">
                    <button class="close-button" @click="goToFirstPage">
                        <img src="@/assets/images/closebutton.png" alt="Close" class="close-button-image" />
                    </button>
                    <h1>Part 4: Future Intent</h1>
                    <div class="title-underline"></div>
                    <div class="feedback-page-content-question feedback-question-12">
                        <p> 12. I would be interested in using Plot & Palette again in the future.</p>
                        <div class="feedback-question-options">
                            <div class="feedback-question-option" :class="{ 'selected': answers.q12 === 1 }" @click="answers.q12 = 1">
                                <p>1</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q12 === 2 }" @click="answers.q12 = 2">
                                <p>2</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q12 === 3 }" @click="answers.q12 = 3">
                                <p>3</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q12 === 4 }" @click="answers.q12 = 4">
                                <p>4</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q12 === 5 }" @click="answers.q12 = 5">
                                <p>5</p>
                            </div>
                        </div>
                    </div>
                    <div class="feedback-page-content-question feedback-question-13">
                        <p> 13. I would recommend Plot & Palette to friends who are interested in art or storytelling.</p>
                        <div class="feedback-question-options">
                            <div class="feedback-question-option" :class="{ 'selected': answers.q13 === 1 }" @click="answers.q13 = 1">
                                <p>1</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q13 === 2 }" @click="answers.q13 = 2">
                                <p>2</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q13 === 3 }" @click="answers.q13 = 3">
                                <p>3</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q13 === 4 }" @click="answers.q13 = 4">
                                <p>4</p>
                            </div>
                            <div class="feedback-question-option" :class="{ 'selected': answers.q13 === 5 }" @click="answers.q13 = 5">
                                <p>5</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div v-if="step === 8" class="feedback-page-content feedback-eighth-page">
                    <button class="close-button" @click="goToFirstPage">
                        <img src="@/assets/images/closebutton.png" alt="Close" class="close-button-image" />
                    </button>
                    <h1>Part 5: Open-Ended Feedback</h1>
                    <div class="title-underline"></div>
                    <div class="feedback-page-content-question feedback-question-14">
                        <p>14. What did you like most about your experience with Plot & Palette?</p>
                        <textarea v-model="answers.q14" class="feedback-question-input" type="text" placeholder="Type your answer here..."></textarea>
                        
                    </div>
                    <div class="feedback-page-content-question feedback-question-15">
                        <p>15. What, if anything, would you suggest to improve Plot & Palette?</p>
                        <textarea v-model="answers.q15" class="feedback-question-input" type="text" placeholder="Type your answer here..."></textarea>
                        
                    </div>
                </div>
                
                <div v-if="step === 9" class="feedback-page-content feedback-ninth-page">
                    <div class="thank-you-container">
                        <div class="thank-you-gif-container">
                            <img src="@/assets/images/thankyou.gif" alt="Thank You" class="thank-you-gif" />
                        </div>
                        
                        <div class="thank-you-text-container">
                            <p class="thank-you-text">Thank you for being part of us!</p>
                            <div class="thank-you-underline"></div>
                        </div>
                        
                        <button @click="goToHomepage" class="homepage-button">Homepage</button>
                    </div>
                </div>
                
                <div class="feedback-page-content-container-buttons">
                    <div v-if="step === 1" class="first-page-buttons">
                        <button @click="goBackToStory" class="maybe-later-button">Maybe later</button>
                        <button @click="step++" class="start-button">Start</button>
                    </div>
                    <div v-else class="navigation-buttons">
                        <button v-if="step > 1 && step !== 9" @click="step--" class="previous-step-button">
                            <img src="@/assets/images/leftbutton.png" alt="Previous" class="nav-button-image" />
                        </button>
                        <button v-if="step < 8" @click="step++" class="next-step-button" :disabled="!canProceedToNext()">
                            <img src="@/assets/images/rightbutton.png" alt="Next" class="nav-button-image" />
                        </button>
                        <button v-if="step === 8" @click="submitAnswers" class="next-step-button">
                            <img src="@/assets/images/rightbutton.png" alt="Next" class="nav-button-image" />
                        </button>
                    </div>
                </div>
                
            </div>
        </div>
    </div>
</template>

<script>
// import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ApiService from '@/services/api.js'

export default {
  name: 'FeedbackPage',
  data() {
    return {
      step: 1,
      // Prolific integration state
      prolificParticipant: false,
      showProlificModal: false,
      prolificRedirectUrl: 'https://app.prolific.com/submissions/complete?cc=C4TQU6TF',
      prolificCompletionCode: 'C4TQU6TF',
      answers: {
        q1: null,
        q2: null,
        q3: null,
        q4: null,
        q5: null,
        q6: null,
        q7: null,
        q8: null,
        q9: null,
        q10: null,
        q11: null,
        q12: null,
        q13: null,
        q14: '',
        q15: ''
      }
    }
  },
  mounted() {
    // Capture Prolific params from URL on load and stash them
    try {
      const params = new URLSearchParams(window.location.search)
      ;['PROLIFIC_PID', 'STUDY_ID', 'SESSION_ID'].forEach((key) => {
        const value = params.get(key)
        if (value) {
          localStorage.setItem(key, value)
        }
      })
      this.prolificParticipant = !!localStorage.getItem('PROLIFIC_PID')
    } catch (e) {
      // no-op
    }
  },
  methods: {
    goToFirstPage() {
      this.step = 1
    },
    goToHomepage() {
      // Navigate to homepage while preserving username in localStorage
      // The username should persist for future sessions
      this.$router.push('/')
    },
    canProceedToNext() {
      if (this.step === 2) {
        return this.answers.q1 !== null && this.answers.q2 !== null && this.answers.q3 !== null
      } else if (this.step === 3) {
        return this.answers.q4 !== null && this.answers.q5 !== null
      } else if (this.step === 4) {
        return this.answers.q6 !== null && this.answers.q7 !== null
      } else if (this.step === 5) {
        return this.answers.q8 !== null && this.answers.q9 !== null
      } else if (this.step === 6) {
        return this.answers.q10 !== null && this.answers.q11 !== null
      } else if (this.step === 7) {
        return this.answers.q12 !== null && this.answers.q13 !== null
      }
      return true
    },
    async submitAnswers() {
      try {
        const sessionId = localStorage.getItem('sessionId')
        const prolificPid = localStorage.getItem('PROLIFIC_PID')
        const prolificStudyId = localStorage.getItem('STUDY_ID')
        const prolificSessionId = localStorage.getItem('SESSION_ID')
        
        // Submit the answers directly (q1-q13 as integers, q14-q15 as text)
        const result = await ApiService.request('/submit-feedback', {
          method: 'POST',
          body: JSON.stringify({
            answers: this.answers,
            sessionId: sessionId,
            // Include Prolific identifiers when available (backend may ignore if unused)
            PROLIFIC_PID: prolificPid || undefined,
            STUDY_ID: prolificStudyId || undefined,
            SESSION_ID: prolificSessionId || undefined
          })
        })

        console.log('✅ Feedback submitted successfully')
        
        // Move to thank you page
        this.step = 9
        
        // If this is a Prolific participant and backend returned success, show redirect modal
        if (this.prolificParticipant && result && result.success === true) {
          this.showProlificModal = true
        }
        
      } catch (error) {
        console.error('❌ Error submitting feedback:', error)
        alert('Failed to submit feedback. Please try again.')
      }
    },
    goBackToStory() {
      this.$router.push('/story')
    },
    closeProlificModal() {
      this.showProlificModal = false
    },
    openProlific() {
      window.open(this.prolificRedirectUrl, '_blank', 'noopener')
    },
    async copyCompletionCode() {
      try {
        await navigator.clipboard.writeText(this.prolificCompletionCode)
        alert('Completion code copied')
      } catch (e) {
        // Fallback if clipboard not available
        prompt('Copy this code:', this.prolificCompletionCode)
      }
    }
  },
  // components: {
  //   LoadingSpinner
  // }
}
</script>

<style scoped>
.feedback-page {
  width: 100vw;
  height: 100vh;
  position: relative;
  background-image: url('@/assets/images/colourbar.png');
  background-size: 85vw auto;
  background-position: center;
  background-repeat: no-repeat;
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: 'Poppins', sans-serif;
}

.feedback-page-container {  
  width: 70vw;
  height: 80vh;
  background-color: rgba(216, 213, 213, 0.75);
  border: 1px solid rgba(12, 12, 12, 1);
  border-radius: 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-left: 5vw;
  padding-right: 5vw;
}

.feedback-page-content-container{
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.feedback-page-content{
    flex: 8;
    display: flex;
    flex-direction: column;
    align-items: left;
    justify-content: left;
    gap: 20px;
    padding-top: 5vh;
    padding-bottom: 5vh;
    width: 100%;
    position: relative;
}

.close-button {
    position: absolute;
    top: 40px;
    right: 20px;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.9);
    border: 2px solid rgba(0, 0, 0, 0.3);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    z-index: 10;
    outline: none;
    padding: 8px;
}

.close-button:focus {
    outline: none;
}

.close-button:active {
    outline: none;
}

.close-button:hover {
    background: rgba(255, 255, 255, 1);
    border-color: rgba(0, 0, 0, 0.5);
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.close-button-image {
    width: 40px;
    height: 40px;
    object-fit: fill;
}

.feedback-first-page {
    text-align: left;
    max-width: 1000px;
}

.feedback-first-page-header {
    margin-bottom: 30px;
}

.feedback-first-page h1 {
    font-family: 'Poppins', sans-serif;
    font-size: 36px;
    font-weight: 600;
    color: black;
    margin: 0;
    margin-bottom: 15px;
}

.title-underline {
    width: 1000px;
    height: 2px;
    background-color: black;
    margin: 0 auto;
}

.feedback-description {
    font-family: 'Poppins', sans-serif;
    font-size: 20px;
    color: black;
    margin: 0 0 20px 0;
    line-height: 1.5;
}

.feedback-intro {
    font-family: 'Poppins', sans-serif;
    font-size: 20px;
    color: black;
    margin: 0 0 20px 0;
    line-height: 1.5;
}

.scorebar-container {
    width: 100%;
    display: flex;
    justify-content: center;
    margin: 0px 0;
}

.scorebar-image {
    max-width: 600px;
    height: auto;
    object-fit: contain;
}

.feedback-instruction {
    font-family: 'Poppins', sans-serif;
    font-size: 20px;
    color: black;
    margin: 20px 0 0 0;
    line-height: 1.5;
}

.feedback-declaration {
    font-family: 'Poppins', sans-serif;
    font-size: 16px;
    font-style: italic;
    color: grey;
    margin: 10px 0 0 0;
    line-height: 1.5;
}

.feedback-page-content-container-buttons{
    flex: 2;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    width: 100%;
}

.first-page-buttons {
    display: flex;
    gap: 30px;
    align-items: center;
    justify-content: center;
}

.maybe-later-button {
    background: rgba(255, 255, 255, 0.8);
    border: 2px solid rgba(0, 0, 0, 0.3);
    border-radius: 50px;
    padding: 15px 30px;
    color: black;
    cursor: pointer;
    transition: all 0.3s ease;
    font-family: 'Poppins', sans-serif;
    font-size: 16px;
    font-weight: 500;
    outline: none;
}

.maybe-later-button:focus {
    outline: none;
}

.maybe-later-button:active {
    outline: none;
}

.maybe-later-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
    background: rgba(255, 255, 255, 0.9);
}

.start-button {
    background: rgba(0, 0, 0, 0.8);
    border: 2px solid rgba(0, 0, 0, 0.9);
    border-radius: 50px;
    padding: 15px 30px;
    color: white;
    cursor: pointer;
    transition: all 0.3s ease;
    font-family: 'Poppins', sans-serif;
    font-size: 16px;
    font-weight: 500;
    outline: none;
}

.start-button:focus {
    outline: none;
}

.start-button:active {
    outline: none;
}

.start-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    background: rgba(0, 0, 0, 0.9);
}

.navigation-buttons {
    display: flex;
    gap: 20px;
    align-items: center;
    justify-content: space-between;
    width: 100%;
}

.next-step-button, .previous-step-button{
    background: rgba(0, 0, 0, 0.15);
    border: 2px solid rgba(0, 0, 0, 0.3);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    padding: 0;
    cursor: pointer;
    transition: all 0.3s ease;
    outline: none;
    display: flex;
    align-items: center;
    justify-content: center;
}

.next-step-button:focus, .previous-step-button:focus {
    outline: none;
}

.next-step-button:active, .previous-step-button:active {
    outline: none;
}

.next-step-button:hover, .previous-step-button:hover{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.next-step-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
}

.next-step-button:disabled:hover {
    transform: none;
    box-shadow: none;
}

.nav-button-image {
    width: 40px;
    height: 40px;
    object-fit: fill;
}

.feedback-page-content-question{
    padding-top: 10px;
    padding-bottom: 10px;
}

.feedback-page-content-question p {
    font-family: 'Poppins', sans-serif;
    font-size: 20px;
}

.feedback-question-options{
    display: flex;
    flex-direction: row;
    align-items: left;
    justify-content: start;
}

.feedback-question-option{
    margin-top: 10px;
    margin-right: 10px;
    width: 50px;
    height: 50px;
    background-color: #ffffff;
    color: #060606;
    border: 1px solid #000000;
    border-radius: 25px;
    cursor: pointer;
    transition: all 0.3s ease;
    text-shadow: 0 2px 4px rgba(255, 255, 255, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Poppins', sans-serif;
    outline: none;
}

.feedback-question-option:focus {
    outline: none;
}

.feedback-question-option:active {
    outline: none;
}

.feedback-question-option:hover{
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.feedback-question-option.selected {
    background-color: black;
    color: white;
    border-color: black;
}

.feedback-question-input{
    margin-top: 5px;
    width: 100%;
    height: 100px;
    background-color: #ffffff;
    color: #060606;
    border: 1px solid #000000;
    font-family: 'Poppins', sans-serif;
    font-size: 20px;
    padding: 15px;
    resize: none;
    outline: none;
}

.feedback-question-input::placeholder {
    font-family: 'Poppins', sans-serif;
    font-style: italic;
    font-size: 20px;
    color: grey;
}

.feedback-question-input:focus::placeholder {
    opacity: 0;
}

/* Thank You Page Styles */
.feedback-ninth-page {
    display: flex;
    align-items: center;
    justify-content: center;
}

.thank-you-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    max-width: 800px;
    width: 100%;
}

.thank-you-gif-container {
    margin-bottom: 40px;
}

.thank-you-gif {
    max-width: 500px;
    height: auto;
    object-fit: contain;
}

.thank-you-text-container {
    margin-bottom: 40px;
}

.thank-you-text {
    font-family: 'Poppins', sans-serif;
    font-size: 22px;
    color: black;
    margin: 0 0 15px 0;
    font-weight: 400;
}

.thank-you-underline {
    width: 300px;
    height: 2px;
    background-color: black;
    margin: 0 auto;
}

.homepage-button {
    background: rgba(255, 255, 255, 0.8);
    border: 2px solid rgba(0, 0, 0, 0.3);
    border-radius: 50px;
    padding: 15px 40px;
    color: black;
    cursor: pointer;
    transition: all 0.3s ease;
    font-family: 'Poppins', sans-serif;
    font-size: 18px;
    font-weight: 500;
    outline: none;
}

.homepage-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
    background: rgba(255, 255, 255, 0.9);
}

.homepage-button:focus {
    outline: none;
}

.homepage-button:active {
    outline: none;
}

h1, h2, h3, p {
    font-family: 'Poppins', sans-serif;
}

/* Global button focus disable */
button:focus {
  outline: none !important;
}

/* Prolific modal styles */
.prolific-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.prolific-modal {
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.3);
  border-radius: 16px;
  padding: 24px 28px;
  max-width: 520px;
  width: calc(100% - 40px);
  text-align: center;
}

.prolific-modal-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* Responsive design */
@media (max-width: 768px) {
  .feedback-container {
    padding: 40px 30px;
  }
  
  .feedback-header h1 {
    font-size: 28px;
  }
  
  .rating-buttons {
    flex-wrap: wrap;
  }
  
  .checkbox-group {
    grid-template-columns: 1fr;
  }
  
  .rating-scale {
    flex-direction: column;
    gap: 20px;
  }
  
  .form-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .action-btn {
    width: 100%;
    max-width: 250px;
  }
  
  .thank-you-gif {
    max-width: 300px;
  }
  
  .thank-you-text {
    font-size: 18px;
  }
  
  .thank-you-underline {
    width: 200px;
  }
  
  .homepage-button {
    font-size: 16px;
    padding: 12px 30px;
  }
}
</style> 