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

  let correctPhilosopher: Philosopher = {
    id: 0,
    name: dailyPhildle.philosopher_name,
    ...dailyPhildle
  }

  function getHints(guessPhilosopher : Philosopher, dailyPhildle : DailyPhildle) : Hints {
    const nameHint = guessPhilosopher.name === dailyPhildle.philosopher_name
    const countryHint = getCountryHint(guessPhilosopher.country, dailyPhildle.country)
    const schoolHint = getSchoolHint(guessPhilosopher.school, dailyPhildle.school)
    const birthDateHint = getDateHint(guessPhilosopher.birth_date, dailyPhildle.birth_date)
    const deathDateHint = getDateHint(guessPhilosopher.death_date, dailyPhildle.death_date)

    return{
      nameHint,
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
      lives.value--
      await recordPlay(dailyPhildle.phildle_id, startingLives - lives.value, true)
    } 
    else {
      lives.value--
      if (lives.value <= 0) {
        gameOver.value = true
        await recordPlay(dailyPhildle.phildle_id, null, false) // we don't care about attempts on loss, so we give null
      }
    }
    hints.value = getHints(guessPhilosopher, dailyPhildle)
  }

  async function giveUp(){
    await recordPlay(dailyPhildle.phildle_id, null, false)
  }

  function reset(newDailyPhildle: DailyPhildle) {
    lives.value = 5
    guessedCorrectly.value = false
    gameOver.value = false
    currentGuess.value = null
    hints.value = null
    correctPhilosopher = {
      id: 0,
      name: newDailyPhildle.philosopher_name,
      ...newDailyPhildle
    }
  }

  return {
    lives,
    guessedCorrectly,
    gameOver,
    currentGuess,
    hints,
    guess,
    getCorrectHints,
    giveUp,
    reset
  }
}