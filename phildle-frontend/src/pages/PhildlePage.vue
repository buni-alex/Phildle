<template>
  <div class="phildle-page">
    <ToolBar title="Phildle" />

    <!-- Splash overlay -->
    <transition
      name="splash"
      appear
      @after-leave="splashGone = true"
    >
      <div v-if="showSplash" class="loading-overlay">
        <h1 class="loading-title">Phildle</h1>
      </div>
    </transition>

    <!-- Main content -->
    <transition name="fade">
      <PhildleMain
        v-if="splashGone && dailyPhildle"
        :dailyPhildle="dailyPhildle"
        :philosophers="philosophers"
      />
    </transition>

    <AboutModal :show="showAboutModal" @close="showAboutModal = false" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { fetchDailyPhildle, fetchPhildleById } from '../services/data_service'
import { getUser } from '../caches/user_cache'
import { getPhilosophers } from '../caches/philosophers_names_cache'
import type { DailyPhildle } from '../types/daily_phildle'
import ToolBar from '../components/toolbar/ToolBar.vue'
import PhildleMain from '../components/game_window/PhildleMain.vue'
import AboutModal from '../components/modals/AboutModal.vue'

const route = useRoute()
const dailyPhildle = ref<DailyPhildle | null>(null)
const philosophers = ref<string[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const showSplash = ref(false)
const splashGone = ref(false)
const showAboutModal = ref(false)

async function loadPhildle() {
  try {
    loading.value = true
    error.value = null
    const userInit = await getUser()
    if (userInit.new_user) {
      showAboutModal.value = true 
    }
    philosophers.value = await getPhilosophers()

    const id = route.params.id ? Number(route.params.id) : null
    dailyPhildle.value = id ? await fetchPhildleById(id) : await fetchDailyPhildle()
  } catch (e: any) {
    error.value = e.message ?? 'Unknown error'
  } finally {
    loading.value = false

    // Check sessionStorage to see if splash was already shown
    // (first access of the main page)
    if (!sessionStorage.getItem('phildleSplashShown')) {
      showSplash.value = true
      // Mark it as shown for the rest of the session
      sessionStorage.setItem('phildleSplashShown', 'true')
    } else {
      splashGone.value = true // do not show
    }
  }
}

onMounted(loadPhildle)
watch(() => route.fullPath, loadPhildle) // 👈 react when route changes, othewise vue caches
</script>

<style scoped>
.phildle-page {
  padding: 2rem;
  margin-top:2rem;
}
@media (max-width: 500px) {
.phildle-page {
  padding: 1rem;
}
}

.loading-title {
  font-size:72px;
}

/* Splash transition */
/* Splash fade */
:deep(.splash-enter-from) { opacity: 0; transform: translateY(20px); }
:deep(.splash-enter-active) { transition: all 600ms ease; }
:deep(.splash-enter-to) { opacity: 1; transform: translateY(0); }

:deep(.splash-leave-from) { opacity: 1; }
:deep(.splash-leave-active) { transition: opacity 0.6s ease; }
:deep(.splash-leave-to) { opacity: 0; }

/* Main content fade-in (faster, minimal delay) */
:deep(.fade-enter-from) { opacity: 0; }
:deep(.fade-enter-active) { transition: opacity 0.35s ease; } /* faster fade */
:deep(.fade-enter-to) { opacity: 1; }
</style>