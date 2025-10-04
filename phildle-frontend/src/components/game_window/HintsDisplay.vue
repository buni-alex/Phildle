<template>
  <div class="hints-display">
    <!-- 1. Philosopher Name -->
    <div class="hint-square name">
      <div class="flip-inner">
        <div class="flip-front"></div>
        <div class="flip-back"
             :class="{ correct: hints.nameHint }">
          {{ guessedPhilosopher.name }}
        </div>
      </div>
    </div>

    <!-- 2. School(s) -->
    <div class="hint-square school">
      <div class="flip-inner">
        <div class="flip-front"></div>
        <div class="flip-back"
             :class="{
               correct: hints.schoolHint?.allCorrectMatched,
               partial: !hints.schoolHint?.allCorrectMatched && hints.schoolHint?.matches?.some(m => m === 'true' || m === 'maybe')
             }">
          <span
            v-for="(school, i) in schoolArray"
            :key="i"
            style="display: block; white-space: normal; margin-bottom: 2px;"
          >
            <span style="white-space: normal;">{{ school }}</span>
            <span style="white-space: nowrap;" v-if="hints.schoolHint">
              {{
                hints.schoolHint.matches[i] === 'true' ? ' ✅' :
                hints.schoolHint.matches[i] === 'maybe' ? ' 🤔💭' :
                ' ❌'
              }}
              <span v-if="i !== schoolArray.length - 1">,</span>
            </span>
          </span>
        </div>
      </div>
    </div>

    <!-- 3. Country -->
    <div class="hint-square country">
      <div class="flip-inner">
        <div class="flip-front"></div>
        <div class="flip-back"
             :class="{ 
               correct: hints.countryHint?.fullyCorrect, 
               partial: !hints.countryHint?.fullyCorrect && hints.countryHint?.canonicalCorrect 
             }">
          {{ extractedCountry }}
          <span class="country-hint" v-if="hints.countryHint">
            {{ hints.countryHint.fullyCorrect ? '✅' :
               hints.countryHint.canonicalCorrect && !hints.countryHint.fullyCorrect ? '🤔💭' :
               '❌' }}
          </span>
          <div v-if="hints.countryHint?.canonicalCorrect && !hints.countryHint.fullyCorrect" class="country-note">
            It may have been called differently at the time.
          </div>
        </div>
      </div>
    </div>

    <!-- 4. Birth Date -->
    <div class="hint-square birth-date">
      <div class="flip-inner">
        <div class="flip-front"></div>
        <div class="flip-back"
             :class="{ correct: hints.birthDateHint === 'same',
                       partial: hints.birthDateHint === 'maybe'}">
          {{ formatDate(guessedPhilosopher.birth_date) }}
          <span class="date-hint" v-if="hints.birthDateHint">
            {{ dateHintEmoji(hints.birthDateHint) }}
          </span>
          <div v-if="hints.birthDateHint === 'maybe'" class="date-note">
            Or at least around that time.
          </div>
        </div>
      </div>
    </div> 

    <!-- 5. Death Date -->
    <div class="hint-square death-date">
      <div class="flip-inner">
        <div class="flip-front"></div>
        <div class="flip-back"
             :class="{ correct: hints.deathDateHint === 'same',
                       partial: hints.deathDateHint === 'maybe'}">
          {{ guessedPhilosopher.death_date ? formatDate(guessedPhilosopher.death_date) : 'N/A' }}
          <span class="date-hint" v-if="hints.deathDateHint">
            {{ dateHintEmoji(hints.deathDateHint) }}
          </span>
          <div v-if="hints.deathDateHint === 'maybe'" class="date-note">
            Or at least around that time.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Hints } from '../../types/hints';
import type { Philosopher } from '../../types/philosopher';
import { computed } from 'vue';
import { extractCountryName } from '../../utils/country_hint'
import { formatDate } from '../../utils/format_date'

const props = defineProps<{
  guessedPhilosopher: Philosopher,
  hints: Hints
}>();

// Keep the school array for looping
const schoolArray = computed(() =>
  props.guessedPhilosopher.school
    ? props.guessedPhilosopher.school.split(',').map(s => s.trim())
    : []
)

const extractedCountry = extractCountryName(props.guessedPhilosopher.country)

function dateHintEmoji(hint: string): string {
  switch(hint) {
    case 'earlier': return '⬇️';
    case 'later': return '⬆️';
    case 'same': return '✅';
    case 'maybe': return '✅';
    default: return '⛔';
  }
}

</script>

<style>
.hints-display {
  display: grid;
  grid-template-columns: 1.5fr 2.5fr 2fr 1fr 1fr;
  gap: 9px;
  font-family: 'Fira Sans', sans-serif;
}

.hint-square {
  position: relative;
  display: flex;
  width: 100%;
  min-width: 0; /* allow shrinking below content width */
}

.flip-inner {
  position: relative;
  min-width: 100%;
  perspective: 1000px;
  transform-style: preserve-3d;
  animation: flip-with-recoil 2s cubic-bezier(0.81, 0, 0.2, 1) forwards;

  display: flex;
}

.flip-front,
.flip-back {
  border: 1.8px solid #444;
  border-radius: 5.4px;
  padding: 10px 9px;
  box-sizing: border-box;

  color: #eee;
  background-color: #484343;

  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  justify-content: center;
  min-width: 100%;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}

.flip-back {
  transform: translate(-100%, 0) rotateX(180deg);
}

.flip-back.correct {
  background-color: #399b3c !important; 
  border-color: #388E3C!important;
  color: white;
  font-weight: bold;
}

.flip-back.partial {
  background-color: #b59f3b!important; 
  border-color: #A88621!important;
  color: #eee;
  font-weight: bold;
}

/* Animation: start on back, rotate to front */
@keyframes flip-with-recoil {
  0% {
    transform: rotateX(0deg);
  }
  46% {
    transform: rotateX(205deg); /* main flip over-rotate */
  }
  65% {
    transform: rotateX(170deg); /* recoil back */
  }
  80% {
    transform: rotateX(190deg); /* recoil forward */
  }
  90% {
    transform: rotateX(175deg); /* smaller recoil */
  }
  100% {
    transform: rotateX(180deg); /* settle */
  }
}

.country-note, .date-note{
  font-style: italic !important;
}


@media (max-width: 600px) {
  .hints-display {
    display: flex;
    gap: 9px; 
    align-items: stretch;
  }
  .hint-square {
    position: relative;
    display: flex;
    flex: 1 1 108px;
  }
}

@media (max-width: 480px){
  .hints-display{
    font-size:larger;
  }
}
</style>