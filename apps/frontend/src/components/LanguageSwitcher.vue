<template>
  <div class="language-switcher">
    <button 
      class="lang-button" 
      :class="{ active: currentLocale === 'en' }"
      @click="switchLanguage('en')"
    >
      EN
    </button>
    <span class="separator">|</span>
    <button 
      class="lang-button" 
      :class="{ active: currentLocale === 'zh' }"
      @click="switchLanguage('zh')"
    >
      中文
    </button>
  </div>
</template>

<script>
import { useI18n } from 'vue-i18n'

export default {
  name: 'LanguageSwitcher',
  setup() {
    const { locale } = useI18n()
    
    const switchLanguage = (lang) => {
      locale.value = lang
      localStorage.setItem('user-language', lang)
      console.log(`🌐 Language switched to: ${lang}`)
    }
    
    return {
      currentLocale: locale,
      switchLanguage
    }
  }
}
</script>

<style scoped>
.language-switcher {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'Poppins', sans-serif;
}

.lang-button {
  background: none;
  border: none;
  font-size: 1vw;
  color: rgba(0, 0, 0, 0.5);
  cursor: pointer;
  padding: 4px 8px;
  transition: all 0.3s ease;
  font-family: 'Poppins', sans-serif;
}

.lang-button:hover {
  color: rgba(0, 0, 0, 0.8);
  transform: scale(1.1);
}

.lang-button.active {
  color: black;
  font-weight: 600;
}

.separator {
  color: rgba(0, 0, 0, 0.3);
  font-size: 1vw;
}

/* Responsive design */
@media (max-width: 768px) {
  .lang-button {
    font-size: 14px;
  }
  
  .separator {
    font-size: 14px;
  }
}
</style>
