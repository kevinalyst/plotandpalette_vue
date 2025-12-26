import { createI18n } from 'vue-i18n'

// Import translation files
import en from './locales/en.json'
import zh from './locales/zh.json'

// Get browser language or default to English
function getBrowserLanguage() {
  const savedLanguage = localStorage.getItem('user-language')
  if (savedLanguage) {
    return savedLanguage
  }
  
  const browserLang = navigator.language || navigator.userLanguage
  // Check if browser language starts with 'zh' (Chinese)
  if (browserLang.startsWith('zh')) {
    return 'zh'
  }
  
  return 'en'
}

const i18n = createI18n({
  legacy: false, // Use Composition API mode
  locale: getBrowserLanguage(), // Set locale from browser or localStorage
  fallbackLocale: 'en', // Fallback to English if translation missing
  messages: {
    en,
    zh
  },
  globalInjection: true // Enable $t in templates
})

export default i18n
