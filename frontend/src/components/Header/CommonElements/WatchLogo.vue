<template>
  <div class="m-0 mr-3">
    <Button @click="changeTheme" severity="secondary" text class="p-0" rounded style="width: fit-content">
      <Image width="60" :src="themeIcon"></Image>
    </Button>
  </div>
</template>

<script setup>
import Image from 'primevue/image'
import Button from 'primevue/button'
import {imagePath, wemeetLogoWhite} from '@assets/index.js'
import {userSettingsStore} from '@/store/userSettingsStore.js'
import {usePrimeVue} from 'primevue/config'
import {computed} from 'vue'


const primevue = usePrimeVue()
const store = userSettingsStore()
const changeTheme = () => {
  const currentTheme = store.darkModeOn ? 'aura-dark-noir' : 'aura-light-noir'
  const newTheme = store.darkModeOn ? 'aura-light-noir' : 'aura-dark-noir'
  console.log(primevue)
  primevue?.changeTheme(currentTheme, newTheme, 'theme-link', () => {
    console.log(`Смена темы: ${currentTheme} → ${newTheme}`)
  })

  store.setVisualMode()
}

const themeIcon = computed(() => {
  if (!store.$state.darkModeOn) return imagePath
  return wemeetLogoWhite
})
</script>

<style></style>
