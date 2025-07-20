import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'

// Create the Vue app with router
const app = createApp(App)

// Use router
app.use(router)

// Global error handler
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue Error:', err)
  console.error('Vue Info:', info)
}

// Mount the app
app.mount('#app') 