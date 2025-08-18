import { createRouter, createWebHistory } from 'vue-router'
import PhildlePage from '../pages/PhildlePage.vue'
import ArchivePage from '../pages/ArchivePage.vue'
import StatsPage from '../pages/StatsPage.vue'

const routes = [
  {
    path: '/',
    redirect: '/today'  // default to today's phildle
  },
  {
    path: '/today',
    component: PhildlePage,
    name: 'DailyPhildle'
  },
  {
    path: '/phildle/:id',
    component: PhildlePage,
    name: 'PastPhildle',
    props: true
  },
  {
    path: '/archive',
    name: 'Archive',
    component: ArchivePage,
  },
  {
    path: '/stats',
    name: 'Stats',
    component: StatsPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router