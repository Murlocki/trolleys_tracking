<script setup>
import {error, errorWhite, imagePath, wemeetLogoWhite} from "@/assets/index.js"
import Image from "primevue/image";
import {computed} from "vue";
import {userSettingsStore} from "@/store/userSettingsStore.js";
const props = defineProps({
  errorText: String,
  errorCode: Number
})
const errorTitle = props.errorCode ? `Code: ${props.errorCode} Text: ${props.errorText}` : `Text: ${props.errorText}`

const store = userSettingsStore()
const errorIcon = computed(() => {
  if (!store.$state.darkModeOn) return error
  return errorWhite
})
</script>

<template>
  <div class="flex flex-column justify-content-center align-items-center mt-5 border-top-2 border-bottom-2 border-black-alpha-10 gap-2">
    <Image :src="errorIcon" :preview="false" image-style="max-width:100vw" width="400"/>
    <span class="font-bold text-3xl">ERROR:</span>
    <span class="font-bold text-3xl" v-if="props.errorCode">Code: {{props.errorCode}}</span>
    <span class="font-bold text-3xl mb-4">{{props.errorText}}</span>
  </div>
</template>

<style scoped>

</style>