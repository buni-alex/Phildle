import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/today'  // default to today's phildle
  },
  {
    path: '/today',
    name: 'DailyPhildle',
    component: () => import('../pages/PhildlePage.vue')
  },
  {
    path: '/phildle/:id',
    name: 'PastPhildle',
    component: () => import('../pages/PhildlePage.vue'),
    props: true
  },
  {
    path: '/archive',
    name: 'Archive',
    component: () => import('../pages/ArchivePage.vue')
  },
  {
    path: '/stats',
    name: 'Stats',
    component: () => import('../pages/StatsPage.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router