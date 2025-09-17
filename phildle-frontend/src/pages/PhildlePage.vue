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
    <!-- the key is absolutely necessary to make Vue not recycle the component -->
    <!-- note that it must be unique. The date should be unique -->
    <transition name="fade">
      <PhildleMain
        v-if="splashGone && dailyPhildle"
        :key= "dailyPhildle.date" 
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
import { getPhilosophersNames } from '../caches/philosophers_names_cache'
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
    // fetch user, philosophers, dailyPhildle in parallel
    const id = route.params.id ? Number(route.params.id) : null

    const userPromise = getUser() as Promise<{ user_uuid: string; new_user: boolean }>
    const philosophersPromise = getPhilosophersNames() as Promise<string[]>
    const dailyPromise = id 
      ? fetchPhildleById(id) as Promise<DailyPhildle>
      : fetchDailyPhildle() as Promise<DailyPhildle>
    
    //also preload the other pages in the background
    import('../pages/ArchivePage.vue')
    import('../pages/StatsPage.vue')
      
    const [userInit, philosophersList, daily] = await Promise.all([
      userPromise,
      philosophersPromise,
      dailyPromise
    ])

    if (userInit.new_user){ 
      showAboutModal.value = true
    }
    philosophers.value = philosophersList
    dailyPhildle.value = daily

  } catch (e) {
    console.error(e)
  } finally {
    // hide splash after minimum 200ms or after data ready
    setTimeout(() => {
      showSplash.value = false
      splashGone.value = true
    }, 200)
  }
}

onMounted(() => {
  showSplash.value = true

  loadPhildle()
})

watch(() => route.fullPath, loadPhildle) // react when route changes, othewise vue caches
</script>

<style scoped>
.phildle-page {
  padding: 2rem;
  margin-top:2rem;
}

.loading-overlay {
  position: fixed;
  inset: 0; /* shorthand for top:0; right:0; bottom:0; left:0 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999; /* keep it above everything else */
}

.loading-title {
  font-size: 72px;
  text-align: center;
}

@media (max-width: 500px) {
.phildle-page {
  padding: 1rem;
}
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