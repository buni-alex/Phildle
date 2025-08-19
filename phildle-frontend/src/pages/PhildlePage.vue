<template>
  <div class="phildle-page">
    <ToolBar title="Phildle" />

    <PhildleMain
      v-if="dailyPhildle"
      :dailyPhildle="dailyPhildle"
      :philosophers="philosophers"
    />

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
    if (id) {
      dailyPhildle.value = await fetchPhildleById(id)
    } else {
      dailyPhildle.value = await fetchDailyPhildle()
    }
  } catch (e: any) {
    error.value = e.message ?? 'Unknown error'
  } finally {
    loading.value = false
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
</style>