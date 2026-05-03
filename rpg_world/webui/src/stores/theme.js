import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

const STORAGE_KEY = 'rpg_theme_mode'

function getSystemDark() {
  if (typeof window === 'undefined') return false
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

export const useThemeStore = defineStore('theme', () => {
  // Persisted preference: 'light' | 'dark' | 'system'
  const mode = ref(
    localStorage.getItem(STORAGE_KEY) || 'system',
  )

  // Resolved effective theme: 'light' | 'dark'
  const effective = computed(() => {
    if (mode.value === 'dark') return 'dark'
    if (mode.value === 'light') return 'light'
    return getSystemDark() ? 'dark' : 'light'
  })

  // Sync <html> data attribute for global CSS
  watch(effective, (val) => {
    document.documentElement.setAttribute('data-theme', val)
  }, { immediate: true })

  // Listen for system preference changes in 'system' mode
  let mql = null
  if (typeof window !== 'undefined') {
    mql = window.matchMedia('(prefers-color-scheme: dark)')
    mql.addEventListener('change', () => {
      if (mode.value === 'system') {
        // Force reactivity refresh
        const tmp = effective.value
        document.documentElement.setAttribute('data-theme', tmp)
      }
    })
  }

  function setMode(m) {
    mode.value = m
    localStorage.setItem(STORAGE_KEY, m)
  }

  return { mode, effective, setMode }
})
