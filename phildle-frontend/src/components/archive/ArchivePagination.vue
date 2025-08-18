<template>
  <div v-if="totalPages > 1" class="pagination">
    <button @click="goToPage(1)" :disabled="currentPage === 1">« First</button>
    <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1">‹ Prev</button>

    <button
      v-for="page in paginationPages"
      :key="page.key"
      @click="page.num && goToPage(page.num)"
      :class="{ active: page.num === currentPage, ellipsis: !page.num }"
      :disabled="!page.num"
    >
      {{ page.num || '…' }}
    </button>

    <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages">Next ›</button>
    <button @click="goToPage(totalPages)" :disabled="currentPage === totalPages">Last »</button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  totalPages: number
  currentPage: number
}

const props = defineProps<Props>()
const emit = defineEmits<{ 'update:page': [number] }>()

function goToPage(page: number) {
  if (page < 1) page = 1
  if (page > props.totalPages) page = props.totalPages
  emit('update:page', page)
}

// Compute pages to show with ellipses
const paginationPages = computed(() => {
  const pages: { num: number | null; key: string }[] = []
  const delta = 2

  if (props.totalPages <= 7) {
    for (let i = 1; i <= props.totalPages; i++) pages.push({ num: i, key: i.toString() })
  } else {
    pages.push({ num: 1, key: 'first' })

    if (props.currentPage - delta > 2) pages.push({ num: null, key: 'left-ellipsis' })
    else for (let i = 2; i < props.currentPage - delta; i++) pages.push({ num: i, key: `p${i}` })

    for (let i = Math.max(2, props.currentPage - delta); i <= Math.min(props.totalPages - 1, props.currentPage + delta); i++) {
      pages.push({ num: i, key: `p${i}` })
    }

    if (props.currentPage + delta < props.totalPages - 1) pages.push({ num: null, key: 'right-ellipsis' })
    else for (let i = props.currentPage + delta + 1; i < props.totalPages; i++) pages.push({ num: i, key: `p${i}` })

    pages.push({ num: props.totalPages, key: 'last' })
  }

  return pages
})
</script>

<style scoped>
.pagination {
  display: flex;
  justify-content: center;
  gap: 0.3rem;
  margin: 1rem 0;
}

.pagination button {
  background-color: #2a2a2a;
  color: #fff;
  border: none;
  padding: 0.4rem 0.7rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.pagination button.active {
  background-color: #444;
}

.pagination button.ellipsis {
  cursor: default;
}

.pagination button:hover:not(.active):not(.ellipsis) {
  background-color: #3a3a3a;
}

.pagination button:disabled {
  opacity: 0.4;
  cursor: default;
}
</style>