<template>
  <div class="stats-page">
    <ToolBar title="Phildle" />

    <StatsDisplay v-if="stats" :stats="stats" />
    <p v-else>Loading stats...</p>

    <AboutModal :show="showAboutModal" @close="showAboutModal = false" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import StatsDisplay from "../components/stats/StatsDisplay.vue";
import ToolBar from "../components/toolbar/ToolBar.vue";
import { fetchUserStats } from "../services/history_service";
import type { UserStats } from "../types/user";
import { getUser } from "../caches/user_cache";

const stats = ref<UserStats | null>(null);
const showAboutModal = ref(false);

onMounted(async () => {
  try {
    const user = await getUser();
    if (user.new_user) showAboutModal.value = true;

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