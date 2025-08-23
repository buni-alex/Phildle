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
import { ref, onMounted, watch, nextTick } from 'vue'
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
const showSplash = ref(false)
const splashGone = ref(false)
const showAboutModal = ref(false)

async function loadPhildle() {
  try {
    // Show splash on first visit
    if (!sessionStorage.getItem('phildleSplashShown')) {
      showSplash.value = true
      sessionStorage.setItem('phildleSplashShown', 'true')
    }

    const userInit = await getUser()
    if (userInit.new_user) {
      showAboutModal.value = true
    }

    philosophers.value = await getPhilosophers()

    const id = route.params.id ? Number(route.params.id) : null
    dailyPhildle.value = id ? await fetchPhildleById(id) : await fetchDailyPhildle()

    // Ensure Vue renders splash before hiding
    await nextTick()

    // Hide splash after data is loaded
    if (showSplash.value) {
      showSplash.value = false
      // splashGone will be set automatically via @after-leave
    } else {
      splashGone.value = true
    }

  } catch (e: any) {
    console.error(e)
    splashGone.value = true
  }
}


onMounted(loadPhildle)
watch(() => route.fullPath, loadPhildle) // react when route changes, othewise vue caches
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