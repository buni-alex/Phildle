<template>
  <div v-if="props.show" class="modal-overlay">
    <div class="modal-content" :class="{popOut: closing}">
      <h2 style="text-align: center;">Welcome to Phildle!</h2>
      <p class="mb-4">
        Guess the philosopher behind the quote! Each wrong guess gives you clues related to
        <b>era / school of thought</b>, <b>country of birth</b>, <b>birth date</b> and <b>death date</b>.
        Keep guessing until you get it right... or run out of attempts!
        You've got 5 shots to prove yourself a true bookworm.
      </p>

      <div class="section">
        <img src="../../assets/hints_example.png" alt="Hints screenshot" class="example-img"/>
      </div>

      <p class="mb-4">
        Start typing a philosopher’s name and pick your choice from the suggestions list.
        You don't have to worry about getting those tongue-twisting German names right - we've got you covered!
      </p>

      <div class="section">
        <img src="../../assets/suggestion-field_example.png" alt="Suggestion screenshot" class="example-img"/>
      </div>

      <p class="mb-4">
        Want to admire your own hard work and wisdom? Take a look at the "Your Stats" section, accessible from the side-menu.
        Legends say that those who cultivate their streaks with constancy may ascend to the level of a consummate philosophical Sage. 
      </p>

      <div class="section">
        <img src="../../assets/stats_example.png" alt="Stats screenshot" class="example-img"/>
      </div>

      <p class="mb-4">
        Missed a daily? No worries! You can play any past Phildle from the Archive.
        You may even replay Phildles that you've failed, or liked so much that you want to check out again,
        <b>but note that these will contribute only to your Played stats</b>.
      </p>

      <button class="close-btn" @click="onClose">Got it!</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps<{ show: boolean }>()
const emit = defineEmits(['close']);
const closing = ref(false);

watch(
  () => props.show,
  (val) => {
    if (val) closing.value = false; // reset animation when opening
  }
);

const onClose = () => {
  closing.value = true;
  setTimeout(() => emit('close'), 300);
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  box-sizing: border-box;
  background: rgba(0,0,0,0.8);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 4rem 1rem 2rem; /* top + horizontal + bottom padding */
  z-index: 1000;
  overflow-y: auto;
}

.modal-content {
  background: #121212;
  color: #eee;
  padding: 2rem;
  border-radius: 12px;
  width: 100%;
  max-width: 600px;

  /* allow modal to grow with content, but not exceed viewport */
  max-height: 100%;
  overflow-y: auto;

  /* ensure it grows naturally if content is short */
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  animation: popIn 0.3s ease;
}

h2 {
  font-size: 1.8rem;
  margin-bottom: 1rem;
}

h3 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.section {
  margin-bottom: 1.5rem;
}

.example-img {
  width: 100%;
  max-width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.5);
  margin-top: 0.5rem;
}

p {
  line-height: 1.5;
  text-align: justify
}

.close-btn {
  background: #242424; 
  color:#eee; 
  border-radius: 5.4px; 
  border: 1.8px solid #767575; 
  font-weight: bold; 
  padding: 0.5rem 1rem; 
  cursor: pointer; 
  display: block;
  margin: 1rem auto 0; /* top margin + auto horizontal + bottom margin */
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
</style>