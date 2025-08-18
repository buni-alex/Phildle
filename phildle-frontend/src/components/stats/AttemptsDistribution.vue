<template>
  <BarChart
    :data="chartData"
    :options="chartOptions"
  />
</template>

<script setup lang="ts">
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js';
import type { TooltipItem } from 'chart.js';
import { Bar as BarChart } from 'vue-chartjs';
import type { UserStats } from '../../types/user';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const props = defineProps<{
  stats: UserStats;
}>();

const chartData = {
  labels: ["1", "2", "3", "4", "5", '❌'],
  datasets: [
    {
      label: "Phildles Guessed",
      data: [
        props.stats.attempt_distribution[1],
        props.stats.attempt_distribution[2],
        props.stats.attempt_distribution[3],
        props.stats.attempt_distribution[4],
        props.stats.attempt_distribution[5],
        props.stats.attempt_distribution[6]
      ],
      backgroundColor: "#4ade80"
    }
  ]
};

const chartOptions = {
  responsive: true,
  indexAxis: 'y' as const,
  plugins: {
    legend: { display: false },
    tooltip: {
      enabled: true,
      callbacks: {
        label: function(context: TooltipItem<'bar'>) {
          const index = context.dataIndex;
          const value = context.parsed.x; // for horizontal bar, x is the value
          if (index === 5) return `Phildles Failed: ${value}`;
          return `Phildles Guessed: ${value}`;
        }
      }
    }
  },
  scales: {
    x: {
      ticks: { precision: 0 },
      grid: { color: '#333' }
    },
    y: {
      ticks: { color: '#ddd', font: { size: 14 } },
      grid: { display: false }
    }
  },
  elements: {
    bar: {
      borderRadius: 10,
      borderSkipped: false
    }
  }
};
</script>