<template>
  <div class="stats-page">
    <ToolBar title="Phildle" />

    <StatsDisplay v-if="stats" :stats="stats" />
    <p v-else>Loading stats...</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import StatsDisplay from "../components/stats/StatsDisplay.vue";
import ToolBar from "../components/toolbar/ToolBar.vue";
import { fetchUserStats } from "../services/history_service";
import type { UserStats } from "../types/user";

const stats = ref<UserStats | null>(null);

onMounted(async () => {
  try {
    stats.value = await fetchUserStats();
  } catch (error) {
    console.error("Failed to load user stats:", error);
  }
});
</script>

<style scoped>
.stats-page {
  padding: 2rem;
}
</style>