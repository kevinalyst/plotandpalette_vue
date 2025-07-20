import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/views/HomePage.vue'
import GradientPalette from '@/views/GradientPalette.vue'
import ColorPalettePage from '@/views/ColorPalettePage.vue'
import GalleryPage from '@/views/GalleryPage.vue'
import StoryPage from '@/views/StoryPage.vue'

const routes = [
  {
    path: '/',
    name: 'HomePage',
    component: HomePage
  },
  {
    path: '/gradient',
    name: 'GradientPalette',
    component: GradientPalette
  },
  {
    path: '/palette',
    name: 'ColorPalettePage',
    component: ColorPalettePage
  },
  {
    path: '/gallery',
    name: 'GalleryPage',
    component: GalleryPage
  },
  {
    path: '/story',
    name: 'StoryPage',
    component: StoryPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 