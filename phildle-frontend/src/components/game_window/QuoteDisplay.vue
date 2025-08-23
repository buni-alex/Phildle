<template>
  <div class="quote-display">
    <blockquote>
      "{{ props.quote }}"
    </blockquote>
   <!--
    <footer>
      — {{ props.philosopher }}
    </footer>
    -->
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  quote: string
  philosopher: string
}>()
</script>

<style scoped>
.quote-display {
  background-color: #000;
  color: #fff;
  font-family: 'Georgia', serif;
  font-style: italic;
  padding: 1.8rem;
  margin: 1.8rem auto; 
  text-align: justify;
  border-left: 3.6px solid #444; 
  border-radius: 1.35rem; 
  box-shadow:
    inset 0 0 36px rgba(255, 255, 255, 0.05), /* 40px * 0.9 */
    inset 0 0 72px rgba(255, 255, 255, 0.05), /* 80px * 0.9 */
    0 0 27px rgba(255, 255, 255, 0.1); /* 30px * 0.9 */
  width: min(90%, 620px);
  line-height: 1.62; /* 1.8 * 0.9 */
  font-size: 1.26rem; /* 1.4rem * 0.9 */
  letter-spacing: 0.045em; /* 0.05em * 0.9 */
}

blockquote {
  margin: 0;
}

footer {
  text-align: right;
  margin-top: 1.35rem; /* 1.5rem * 0.9 */
  font-weight: bold;
  color: #aaa;
  font-style: normal;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 480px){
  .quote-display{
    font-size:26px;
  }
}
</style>