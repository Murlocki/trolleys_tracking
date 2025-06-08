<template>
    <div class="m-0 ml-2">
        <Button severity="secondary" text class="p-0" rounded style="width: fit-content" @click="navigateToLink">
            <Image width="150" :src="themeIcon"> </Image>
        </Button>
    </div>
</template>

<script setup>
import Image from 'primevue/image'
import Button from 'primevue/button'
import { textLogoPath, textLogoPathWhite } from '@assets/index.js'
import { userSettingsStore } from '../../../store/userSettingsStore'
import { computed } from 'vue'

const store = userSettingsStore()
const themeIcon = computed(() => {
    if (!store.$state.darkModeOn) return textLogoPath
    return textLogoPathWhite
})

import { useRouter } from 'vue-router'
const router = useRouter()
const navigateToLink = () => {
    router.push('/')
}
</script>

<style></style>
