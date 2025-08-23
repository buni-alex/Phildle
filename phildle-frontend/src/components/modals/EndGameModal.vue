<template>
  <div class="modal-overlay" @click.self="onClose">
    <div class="modal-content"
         :class="{popOut: closing}">
      <h2 v-if="win">🎉 You got it!</h2>
      <h2 v-else>💀 Game Over!</h2>

      <p class="philosopher-name"> It was {{ dailyPhildle.philosopher_name }}!</p>

      <div class="details">
        <p><strong>School:</strong> {{ dailyPhildle.school }}</p>
        <p><strong>Country:</strong> {{ dailyPhildle.country }}</p>
        <p><strong>Birth:</strong> {{ formatDate(dailyPhildle.birth_date) }}</p>
        <p><strong>Death:</strong> {{ dailyPhildle.death_date ? formatDate(dailyPhildle.death_date) : 'N/A' }}</p>
      </div>

      <div class="button-column">
        <a
          :href="whatsappLink"
          target="_blank"
          rel="noopener"
          class="whatsapp-btn"
        >
          <i class="fab fa-whatsapp"></i> Share
        </a>

        <button class="close-btn" @click="onClose">Close</button>

        <div class="philosopher-info">
          <img v-if="dailyPhildle.wiki_image_url" 
            :src="dailyPhildle.wiki_image_url" 
            :alt="dailyPhildle.philosopher_name" 
            :class="imagePositionClass" />
          <p v-html="dailyPhildle.info"></p>
          <div v-html="attribution"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DailyPhildle } from '../../types/daily_phildle';
import { formatDate } from '../../utils/format_date';
import { ref, computed } from 'vue';
import { formatImageAttribution } from "../../utils/format_attribution_cite";

const props = defineProps<{
  win: boolean;
  dailyPhildle: DailyPhildle;
  attempts: number;
  isDaily: boolean;
}>();

const imageLeft = Math.random() < 0.5; // 50/50 chance
const imagePositionClass = imageLeft ? 'image-left' : 'image-right';

const attribution = computed(() =>
  formatImageAttribution(props.dailyPhildle.wiki_image_meta)
);

const emit = defineEmits(['close']);
const closing = ref(false);

const onClose = () => {
  closing.value = true;
  // Wait for animation to finish before emitting close
  setTimeout(() => {
    emit('close');
  }, 300); // match the animation duration
};

const whatsappLink = computed(() => {
  const phildleType = props.isDaily ? "today's Phildle" : "a Phildle";
  const currentURL = window.location.href; // grab current page URL
  const resultText = props.win
    ? `I just guessed ${phildleType} in ${props.attempts} attempts 🤓! Try it out yourself at ${currentURL} 🧠✨`
    : `I just played ${phildleType}! This one was tough! Why don't you try it out? You might get your mind blown 🤯! 
    ${currentURL}`;

  return `https://wa.me/?text=${encodeURIComponent(resultText)}`;
});
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.8);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 5rem 1rem 1rem;
  overflow-y: auto; 
  z-index: 1000;
  box-sizing: border-box;
}

.modal-content {
  background: #121212;
  color: #eee;
  padding: 2rem;
  border-radius: 12px;
  width: 100%;
  max-width: 600px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-sizing: border-box;
  animation: popIn 0.3s ease;
}

/* small devices (mobile) */
@media (max-width: 480px) {
  .modal-content {
    transform: scale(1);
    margin-top: 0;
    margin-left: 1rem;
    margin-right: 1rem;
  }
}

.philosopher-name {
  font-size: 1.5rem;
  font-weight: bold;
}

.details p {
  margin: 0.3rem 0;
}

.button-column {
  display: flex;
  flex-direction: column;
  gap: 0.8rem; /* space between buttons */
  align-items:center;
  margin-top: 1rem;
}

.whatsapp-btn,
.close-btn {
  padding: 0.5rem 1rem;
  font-weight: bold;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  border: none;
  border-radius: 6px;
}

.whatsapp-btn {
  background-color: #1ebe57;
  color: #fff;
}

.whatsapp-btn:hover {
  background-color: #2fda6e;
}

.whatsapp-btn i {
  margin-right: 0.5rem;
}

.close-btn { 
  background: #242424; 
  color:#eee; 
  border-radius: 5.4px; 
  border: 1.8px solid #767575; 
  font-weight: bold; 
  padding: 0.5rem 1rem; 
  cursor: pointer; 
}

.close-btn:hover {
  background-color: #323232;
}


@keyframes popIn {
  from { transform: scale(0.8); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
@keyframes popOut {
  from { transform: scale(1); opacity: 1; }
  to { transform: scale(0.8); opacity: 0; }
}

.popOut {
  animation: popOut 0.3s ease forwards;
}

.philosopher-info {
  /* no flex needed */
  overflow: hidden; /* ensures container wraps floated image */
}

.philosopher-info img {
  float: left; /* or right */
  margin: 0 1rem 1rem 0; /* space between image and text */
  max-width: 200px;
  max-height: 200px;
  object-fit: cover;
  border-radius: 8px;
}

.image-left { float: left; margin-right: 1rem; }
.image-right { float: right; margin-left: 1rem; }

.philosopher-info p {
  text-align: justify;
  line-height: 1.5rem;
}

</style>