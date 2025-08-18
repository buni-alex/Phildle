<template>
  <div class="archive-table-container">
    <table class="archive-table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Quote</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(item, index) in pagedHistory"
          :key="item.phildle_id"
          :class="{ selected: item.phildle_id === props.selectedId }"
          @click="emit('select', item.phildle_id, currentPageStartIndex + index)"
        >
          <td>{{ item.date }}</td>
          <td class="quote-cell">{{ item.quote_preview }}</td>
          <td class="status">{{ statusIcon(item.status) }}</td>
        </tr>
      </tbody>
    </table>

    <!-- Pagination -->
    <ArchivePagination
      :totalPages="totalPages"
      :currentPage="currentPage"
      @update:page="currentPage = $event"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import ArchivePagination from './ArchivePagination.vue'

interface Props {
  history: {
    phildle_id: number
    date: string
    status: 'success' | 'fail' | 'not_played'
    quote_preview: string | null
  }[]
  selectedId: number | null
}
const props = defineProps<Props>()
const emit = defineEmits<{ select: [number, number] }>()

const PAGE_SIZE = 11
const currentPage = ref(1)

const totalPages = computed(() => Math.ceil(props.history.length / PAGE_SIZE))
const currentPageStartIndex = computed(() => (currentPage.value - 1) * PAGE_SIZE)

const pagedHistory = computed(() =>
  props.history.slice(currentPageStartIndex.value, currentPageStartIndex.value + PAGE_SIZE)
)

function statusIcon(status: string) {
  return status === 'success'
    ? '✅'
    : status === 'fail'
      ? '❌'
      : '⏳'
}
</script>

<style scoped>
.archive-table-container {
  width: min(90vw, 700px);
  margin: 2rem auto;
  border-radius: 12px;
  overflow: hidden;
  background-color: #1e1e1e;
  color: #fff;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  font-family: system-ui, sans-serif;
}

.archive-table {
  width: 100%;
  border-collapse: collapse;
}

.archive-table th {
  background-color: #2a2a2a;
  font-weight: 600;
  padding: 0.75rem 1rem;
  text-align: center;
}

.archive-table td {
  padding: 0.75rem 1rem;
  text-align: center;
  vertical-align: middle;
  cursor: pointer;
  transition: background-color 0.2s;
}

.archive-table td.quote-cell {
  text-align: left;
  font-style: italic;
}

.archive-table tbody tr:hover {
  background-color: #333;
}

.archive-table tbody tr.selected {
  background-color: #444;
}

.status {
  text-align: center;
}
</style>
