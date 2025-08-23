<template>
  <div class="suggestion-field">
    <input
      class="input-field"
      type="text"
      v-model="inputValue"
      @input="onInput"
      @keydown.down.prevent="highlightNext"
      @keydown.up.prevent="highlightPrev"
      @keydown.enter.prevent="selectHighlighted"
      autocomplete="off"
      spellcheck="false"
      :disabled="props.disabled"
    />

    <ul v-if="filtered.length > 0" class="suggestions-list">
      <li
        v-for="(name, index) in filtered"
        :key="name"
        :ref="el => {
          optionRefs[index] = isHTMLElement(el) ? el : null
        }"
        :class="{ highlighted: index === highlightedIndex }"
        @mouseenter="highlightedIndex = index"
        @mousedown.prevent="select(name)"
      >
        {{ name }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  philosophersList: string[]
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'guessSelected', value: string): void
}>()

const inputValue = ref('')
const filtered = ref<string[]>([])
const highlightedIndex = ref(-1)
const optionRefs = ref<(HTMLElement | null)[]>([])

function isHTMLElement(el: unknown): el is HTMLElement {
  return el instanceof HTMLElement
}

function onInput(): void {
  if (props.disabled) {
    filtered.value = []
    return
  }
  const query = inputValue.value.toLowerCase()

  filtered.value = props.philosophersList
    .filter(name => name.toLowerCase().includes(query))
    .sort((a, b) => {
      const aName = a.toLowerCase()
      const bName = b.toLowerCase()
      const aStarts = aName.startsWith(query) ? 0 : 1
      const bStarts = bName.startsWith(query) ? 0 : 1
      if (aStarts !== bStarts) return aStarts - bStarts
      return aName.localeCompare(bName)
    })
    .slice(0, 5)

  highlightedIndex.value = filtered.value.length > 0 ? 0 : -1
}

function select(name: string): void {
  inputValue.value = ''
  filtered.value = []
  emit('guessSelected', name)
}

function highlightNext(): void {
  if (props.disabled) return
  if (highlightedIndex.value < filtered.value.length - 1) {
    highlightedIndex.value++
  }
}

function highlightPrev(): void {
  if (props.disabled) return
  if (highlightedIndex.value > 0) {
    highlightedIndex.value--
  }
}

function selectHighlighted(): void {
  if (props.disabled) return
  if (highlightedIndex.value >= 0) {
    select(filtered.value[highlightedIndex.value])
  }
}

// Watch for highlight changes and scroll into view
watch(highlightedIndex, (newIndex) => {
  const el = optionRefs.value[newIndex]
  if (el) {
    el.scrollIntoView({ block: 'nearest' })
  }
})

function clear() {
  inputValue.value = ''
  filtered.value = []
  highlightedIndex.value = -1
}

watch(
  () => props.disabled,
  (newVal) => {
    if (newVal) clear()
  }
)

</script>

<style scoped>
input {
  color: #eee;
  background-color: #242424;
  border: 1px solid #555;
  padding: 6px 8px;
  border-radius: 4px;
  font-size: 1rem;
  width: 100%;
  caret-color: #eee;
}

.suggestion-field {
  width: 50%; /* or any width you prefer */
  position: relative;
  box-sizing:border-box;
}

.suggestions-list {
  position: absolute; /* make dropdown overlay */
  top: 100%;          /* right below the input */
  left: 0;
  right: 0;
  background: #242424;
  border: 1px solid #555;
  max-height: 160px;
  overflow-y: auto;
  list-style: none;
  margin: 0;
  padding: 0;
  z-index: 1000;      /* keep it above other content */
}

.suggestions-list li {
  color: #eee;
  padding: 4px 8px;
  cursor: pointer;
}

.suggestions-list li.highlighted {
  background-color: #4e5051;
  color: white;
}

input:disabled {
  background-color: #121212;
  color: #666;
  cursor: not-allowed;
}

@media (max-width: 480px){
  .suggestion-field{
    font-size:23px;
  }
  .input-field{
    font-size:20px;
  }
}
</style>
