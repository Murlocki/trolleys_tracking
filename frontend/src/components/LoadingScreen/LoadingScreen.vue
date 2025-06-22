<script setup>
import BlockUI from 'primevue/blockui'
import ProgressSpinner from 'primevue/progressspinner'
import {userSettingsStore} from "@/store/userSettingsStore.js";

const store = userSettingsStore()
console.log(store.isLoading)
</script>

<template>
  <BlockUI :blocked="store.isLoading" fullScreen>
      <div class="loading-wrapper" v-if="store.isLoading">
        <ProgressSpinner strokeWidth="8"/>
        <p class="text-2xl">Loading...</p>
      </div>
  </BlockUI>
</template>

<style scoped>
/* Сделать фон оверлея почти прозрачным */
.p-blockui-overlay {
  background-color: rgba(0, 0, 0, 0.1) !important;
  /* или background-color: transparent !important; */
  pointer-events: auto; /* чтобы блокировать клики */
}

/* Разместить спиннер внизу экрана */
.loading-wrapper {
  position: fixed;
  bottom: 50%;  /* расстояние от низа */
  left: 50%;
  transform: translateX(-50%);
  z-index: 10000;
  display: flex;
  align-items: center;
  gap: 10px;
  color: white;
}

</style>