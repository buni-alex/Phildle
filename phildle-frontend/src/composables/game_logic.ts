import { ref } from 'vue'
import type { DailyPhildle } from '../types/daily_phildle'
import type { Philosopher } from '../types/philosopher'
import { getCountryHint } from '../utils/country_hint'
import { getDateHint } from '../utils/date_hint'
import { getSchoolHint } from '../utils/school_hint'
import type { Hints } from '../types/hints'
import { fetchPhilosopher } from '../services/data_service'
import { recordPlay } from '../services/history_service'

export function usePhildleGame(dailyPhildle: DailyPhildle, startingLives = 5) {
  const lives = ref(startingLives)
  const guessedCorrectly = ref(false)
  const gameOver = ref(false)
  const currentGuess = ref<Philosopher | null>(null)
  const hints = ref<Hints | null>(null)

  const correctPhilosopher: Philosopher = {
    id: 0,
    name: dailyPhildle.philosopher_name,
    country: dailyPhildle.country,
    school: dailyPhildle.school,
    birth_date: dailyPhildle.birth_date,
    death_date: dailyPhildle.death_date,
    info: dailyPhildle.info,
    wiki_image_url: dailyPhildle.wiki_image_url,
    wiki_image_meta: dailyPhildle.wiki_image_meta
  }

  function reset() {
    lives.value = startingLives
    guessedCorrectly.value = false
    gameOver.value = false
    currentGuess.value = null
    hints.value = null
  }

  function getHints(guessPhilosopher : Philosopher, dailyPhildle : DailyPhildle) : Hints {
    const countryHint = getCountryHint(guessPhilosopher.country, dailyPhildle.country)
    const schoolHint = getSchoolHint(guessPhilosopher.school, dailyPhildle.school)
    const birthDateHint = getDateHint(guessPhilosopher.birth_date, dailyPhildle.birth_date)
    const deathDateHint = getDateHint(guessPhilosopher.death_date, dailyPhildle.death_date)

    return{
      countryHint,
      schoolHint,
      birthDateHint,
      deathDateHint
    }
  }

  function getCorrectHints() : {correctPhilosopher : Philosopher, correctHints : Hints} {
    return {
      correctPhilosopher: correctPhilosopher,
      correctHints: getHints(correctPhilosopher, dailyPhildle)
    }
  }

  async function guess(guessPhilosopherName: string) {
    const guessPhilosopher: Philosopher = await fetchPhilosopher(guessPhilosopherName)
    if (gameOver.value || guessedCorrectly.value) return

    currentGuess.value = guessPhilosopher

    if (guessPhilosopher.name === dailyPhildle.philosopher_name) {
      guessedCorrectly.value = true
      await recordPlay(dailyPhildle.phildle_id, startingLives - lives.value + 1, true) // ✅ record streak update on win
    } 
    else {
      lives.value--
      if (lives.value <= 0) {
        gameOver.value = true
        await recordPlay(dailyPhildle.phildle_id, null, false) // ❌ reset streak on loss
      }
    }
    hints.value = getHints(guessPhilosopher, dailyPhildle)
  }

  async function giveUp(){
    currentGuess.value = correctPhilosopher
    await recordPlay(dailyPhildle.phildle_id, null, false)
    hints.value = getHints(correctPhilosopher, dailyPhildle)
    gameOver.value = true
  }

  return {
    lives,
    guessedCorrectly,
    gameOver,
    currentGuess,
    hints,
    guess,
    reset,
    getCorrectHints,
    giveUp
  }
}