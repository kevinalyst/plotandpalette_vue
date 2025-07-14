import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import HomePage from './views/HomePage.vue'
import GradientPage from './views/GradientPage.vue'
import ColorPalettePage from './views/ColorPalettePage.vue'
import GalleryPage from './views/GalleryPage.vue'
import StoryPage from './views/StoryPage.vue'

// Import global styles
import './assets/styles/main.css'

const routes = [
  { path: '/', name: 'Home', component: HomePage },
  { path: '/gradient', name: 'Gradient', component: GradientPage },
  { path: '/palette', name: 'Palette', component: ColorPalettePage },
  { path: '/gallery', name: 'Gallery', component: GalleryPage },
  { path: '/story', name: 'Story', component: StoryPage }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.mount('#app') 