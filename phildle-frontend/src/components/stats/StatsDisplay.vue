<template>
  <div class="stats-display">
    <h2>📊 Stats</h2>
    <div class="stats-grid">
      <!-- Left side: summary stats -->
      <div class="summary">
        <div class="stat-row">
          <span>Current Streak:</span>
          <strong>
            {{ props.stats.current_streak }}
            <span> {{getStreakEmoji(props.stats.current_streak)}} </span>
          </strong>
        </div>
        <div class="stat-row">
          <span>Max Streak:</span>
          <strong>
            {{ props.stats.max_streak }}
            <span> {{getStreakEmoji(props.stats.max_streak)}} </span>
          </strong>
        </div>
        <div class="stat-row">
          <span>Played:</span>
          <strong>
            {{ props.stats.total_played }}
            ✏️
          </strong>
        </div>
        <div class="stat-row">
          <span>Losses:</span>
          <strong>
            {{ props.stats.losses }} 🫣
          </strong>
        </div>
      </div>

      <!-- Right side: attempt distribution -->
      <div class="distribution">
        <h3>Attempts Distribution</h3>
        <AttemptsDistribution :stats="props.stats" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { UserStats } from "../../types/user";
import AttemptsDistribution from "./AttemptsDistribution.vue";

const props = defineProps<{
  stats: UserStats;
}>();

const getStreakEmoji = (streak: number) => {
    if (streak === 0) return "⬜️";
    if (streak >= 1 && streak < 4) return "👶";
    if (streak >= 4 && streak < 10) return "💪";
    if (streak >= 10 && streak < 20) return "🔥";
    if (streak >= 20 && streak < 80) return "🧙‍♀️";
    if (streak >= 80) return "🧙‍♂️";
}

</script>

<style scoped>
.stats-display {
  width: min(100vw, 700px);
  margin-top: 2rem;
  background: #1e1e1e;
  padding: 1.5rem;
  border-radius: 8px;
}

.stats-grid {
  display: flex;
  justify-content: space-between;
  gap: 2rem;
  align-items: center;
}

/* Mobile breakpoint: allow wider than viewport */
@media (max-width: 500px) {
  .stats-display {
    width: 80vw;       /* 20% wider than viewport */
    padding: 1rem;      /* optional: slightly reduce padding */
    margin-top: 0;
  }

  .stats-grid {
    flex-direction: column; /* stack summary & distribution vertically */
    gap: 1rem;
  }

  .summary,
  .distribution {
    min-width: 100%;
  }
}

.summary {
  flex: 1;
}

.distribution {
  flex: 1;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.6rem;
  font-size: 1.1rem;
}


</style>