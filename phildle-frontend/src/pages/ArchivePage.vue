<template>
  <div class="archive-page">
    <ToolBar title="Phildle" />

    <ArchiveList
      :history="history"
      :selected-id="selectedId"
      @select="selectPhildle"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchHistory } from '../services/history_service'
import ArchiveList from '../components/archive/ArchiveList.vue'
import ToolBar from '../components/toolbar/ToolBar.vue'

const router = useRouter()

interface HistoryItem {
  phildle_id: number
  date: string
  status: 'success' | 'fail' | 'not_played'
  quote_preview: string | null
}

const history = ref<HistoryItem[]>([])
const selectedId = ref<number | null>(null)

function selectPhildle(id: number, index: number) {
  selectedId.value = id
  if (index === 0) {
    router.push({ name: 'DailyPhildle' })
  } else {
    router.push({ name: 'PastPhildle', params: { id } })
  }
}

async function getHistory() {
  try {
    const data = await fetchHistory()
    history.value = data.phildles
  } catch (err) {
    console.error(err)
    history.value = []
  }
}

onMounted(getHistory)
</script>

<style scoped>
.archive-page{
  padding:2rem;
}
</style>
