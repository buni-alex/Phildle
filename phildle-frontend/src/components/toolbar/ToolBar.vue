<template>
  <header class="toolbar">
    <button
      class="menu-button"
      aria-label="Menu"
      @click="toggleMenu"
    >
      <span v-if="!menuOpen">&#9776;</span> <!-- Hamburger -->
      <span v-else>&#10005;</span>           <!-- X -->
    </button>
    <span class="toolbar-title">{{ title }}</span>
  </header>

  <nav class="side-menu" :class="{ open: menuOpen }">
  <ul>
    <li>
      <button
        @mouseenter="preloadToday"
        @click="goToToday"
        :class="{ active: route.name === 'DailyPhildle' }"
      >
        Today's Phildle
      </button>
    </li>
    <li>
      <button
        @mouseenter="preloadArchive"
        @click="goToArchive"
        :class="{ active: route.name === 'Archive' }"
      >
        Archive
      </button>
    </li>
    <li>
      <button
        @mouseenter="preloadStats"
        @click="goToStats"
        :class="{ active: route.name === 'Stats' }"
      >
        Your Stats
      </button>
    </li>
    <li>
      <button
        @click="popAboutModal"
        :class="{ active: showAboutModal }"
      >
        About / How to Play
      </button>
    </li>
  </ul>
</nav>

  <teleport to="body">
    <AboutModal :show="showAboutModal" @close="showAboutModal = false" />
  </teleport>

</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AboutModal from '../modals/AboutModal.vue';

const router = useRouter()
const route = useRoute() 
const showAboutModal = ref(false)

defineProps<{
  title: string
}>()

const menuOpen = ref(false)

function toggleMenu() {
  menuOpen.value = !menuOpen.value
}

function goToStats() {
  menuOpen.value = false
  router.push({name: 'Stats'})
}

function goToToday() {
  menuOpen.value = false
  router.push({ name: 'DailyPhildle' })
}

function goToArchive() {
  menuOpen.value = false
  router.push({ name: 'Archive' })
}

function popAboutModal(){
  menuOpen.value = false
  showAboutModal.value = true
}

function preloadToday() {
  import('../../pages/PhildlePage.vue')
}
function preloadArchive() {
  import('../../pages/ArchivePage.vue')
}
function preloadStats() {
  import('../../pages/StatsPage.vue')
}
</script>

<style scoped>
.toolbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 3rem;
  display: flex;
  align-items: center;
  background-color: #242424;
  color: white;
  padding: 0 1rem;
  font-family: 'Fira Sans', sans-serif;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  z-index: 3000;
}

.menu-button {
  background: none;
  border: none;
  color: inherit;
  font-size: 1.5rem;
  cursor: pointer;
  margin-right: 0.75rem;
  height: 100%;
  width: 3.3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.menu-button:focus,
.menu-button:active {
  outline: 2px solid #323232;
}

.menu-button:hover{
  background-color: #323232;
}

.toolbar-title {
  font-size: 1.4rem;
  font-weight: bold;
}

.side-menu {
  position: fixed;
  top: 0;
  left: -250px;
  width: 250px;
  height: 100%;
  background: #333;
  color: white;
  padding-top: 3rem;
  transition: left 0.3s ease;
  z-index: 2000;
}
.side-menu.open {
  left: 0;
}
.side-menu ul {
  list-style: none;
  padding: 0;
}
.side-menu li {
  padding: 0;
  padding-bottom:0.2rem;
}
.side-menu li button {
  display: block;
  width: 100%;
  text-align: center;
  background: none;
  border: none;
  color: inherit;
  font-size: 1rem;
  padding: 1rem;
  cursor: pointer;
  font-family: inherit;
}

.side-menu li button:hover,
.side-menu li button:focus,
.side-menu li button.active {
  background: #444;
  outline: none;
}

.side-menu li button:focus-visible {
  outline: 2px solid #000000;
  outline-offset: -2px;
}
</style>