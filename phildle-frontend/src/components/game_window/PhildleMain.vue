<template>
  <div class="phildle-main">
  <div>
    <QuoteDisplay
      :quote="props.dailyPhildle.quote_text"
      :philosopher="props.dailyPhildle.philosopher_name"
    />

    <div class = "sticky-wrapper">
      <div class="suggestion-row">
        <SuggestionField
          v-if="props.philosophers.length"
          :philosophersList="props.philosophers"
          :disabled="gameLogic.gameOver.value || gameLogic.guessedCorrectly.value"
          @guessSelected="onGuessSelected"
        />

        <div class="lives">
          <span class="lives-text">Attempts left:</span>
          <span class="lives-circles">
            <span 
              v-for="n in maxLives" 
              :key="n" 
              class="life-circle" 
              :class="{ lost: n > gameLogic.lives.value }"
            ></span>
          </span>
        </div>
      </div>
    </div>

    <div class="hints-container">
      <div v-for="(guess, index) in guessHistory" :key="index" class="hint-row">
        <HintsDisplay :correctName=dailyPhildle.philosopher_name :guessedPhilosopher="guess.guessedPhilosopher" :hints="guess.hints" />
      </div>
    </div>

    <!-- Give Up Button -->
    <button
      v-if="!gameLogic.gameOver.value && !gameLogic.guessedCorrectly.value"
      class="give-up-btn"
      @click="onGiveUp"
    >
      Give Up
    </button>

    <EndGameModal
      v-if="showModal"
      :win="gameLogic.guessedCorrectly.value"
      :dailyPhildle="props.dailyPhildle"
      :attempts="props.dailyPhildle.daily_replay
              ? props.dailyPhildle.daily_replay.attempts
              : maxLives - gameLogic.lives.value + 1"
      :isDaily="isDailyPhildle"
      @close="closeModal"
    />
  </div>
  </div>
</template>

<script setup lang="ts">
import { usePhildleGame } from '../../composables/game_logic.ts'
import QuoteDisplay from './QuoteDisplay.vue'
import SuggestionField from './SuggestionField.vue'
import EndGameModal from '../modals/EndGameModal.vue'
import type { DailyPhildle } from '../../types/daily_phildle'
import type { Philosopher } from '../../types/philosopher.ts'
import HintsDisplay from './HintsDisplay.vue'
import type { Hints } from '../../types/hints'
import {ref, watch, nextTick, computed} from 'vue'

const props = defineProps<{
  dailyPhildle: DailyPhildle,
  philosophers: string[],
}>()

const showModal = ref(false);
const gameLogic = usePhildleGame(props.dailyPhildle)
const guessHistory = ref<{ guessedPhilosopher: Philosopher, hints: Hints }[]>([])
const maxLives = 5

// Determine if the current Phildle is today's daily
const isDailyPhildle = computed(() => {
  console.log(props.dailyPhildle.date)
  const today = new Date().toISOString().slice(0, 10); // "YYYY-MM-DD"
  const phildleDate = new Date(props.dailyPhildle.date).toISOString().slice(0, 10);
  console.log(today, phildleDate)
  return today === phildleDate;
});

if (props.dailyPhildle.daily_replay) {
  if(props.dailyPhildle.daily_replay.daily_success){
    gameLogic.lives.value = maxLives - props.dailyPhildle.daily_replay.attempts
    gameLogic.guessedCorrectly.value = true

    const correctHints = gameLogic.getCorrectHints()

    guessHistory.value.push({
      guessedPhilosopher: correctHints.correctPhilosopher,
      hints: correctHints.correctHints
    })
  }
  else
    gameLogic.gameOver.value = true
  // if you want modal instantly:
  showModal.value = true
}

async function onGuessSelected(philosopherName: string) {
  try {
    gameLogic.guess(philosopherName)
  } catch (error) {
    console.error('Failed to fetch philosopher', error)
  }
}

watch(
  () => (gameLogic.guessedCorrectly.value || gameLogic.gameOver.value),
  (gameEnded) => {
    if (gameEnded) {
      setTimeout(() => {
        showModal.value = true;
      }, 2100); // 2s animation + 1s wait
    }
  }
);

watch(() => gameLogic.hints.value, async (newHints) => {
  if (newHints && Object.keys(newHints).length > 0 && gameLogic.currentGuess.value) {
    guessHistory.value.push({
      guessedPhilosopher: gameLogic.currentGuess.value,
      hints: newHints
    })

    await nextTick() // wait until DOM updates
    window.scrollTo({
      top: document.documentElement.scrollHeight,
      behavior: 'smooth'
    })
  }
})

function onGiveUp() {
  gameLogic.giveUp()
}

function closeModal() {
  showModal.value = false;
}

</script>

<style scoped>
.hint {
  font-weight: bold;
}

.hint-row + .hint-row {
  margin-top: 0.75rem; 
}

.hints-container {
  margin-top: 1.35rem;
}

.sticky-wrapper {
  position: sticky;
  top: 3rem;
  z-index: 1000;
  text-align: center; /* center inner inline-flex */
}

.suggestion-row {
  display: inline-flex;      /* shrink-wrap width */
  justify-content: center;
  align-items: flex-start;
  min-width: 500px; /* or whatever size fits nicely */
  gap: 1.8rem;              /* spacing between children */
  position: sticky;
  top: 3rem;
  background-color: #242424;
  border-radius: 0px 0px 10px 10px;
  padding: 0.5rem 0.1rem;     /* optional for some internal spacing */
}

.lives {
  display: flex;
  align-items: center; /* vertical centering */
  gap: 6px;
}

.lives-circles {
  display: flex;
  gap: 4px;
}

.life-circle {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background-color: white;
  border: 1px solid #333;
  transition: opacity 0.5s, transform 0.5s;
}

.life-circle.lost {
  opacity: 0;       /* faded out */
  transform: scale(0.7); /* optional shrink effect */
}

.give-up-btn {
  display: block;
  margin: 1rem auto 0;
  padding: 0.6rem 1.2rem;
  background-color: #c0392b;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
}

.give-up-btn:hover {
  background-color: #e74c3c;
}
</style>
