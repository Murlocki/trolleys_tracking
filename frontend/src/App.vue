<script setup>
import CookieDialog from './components/CommonCookieDialog/CookieDialog.vue'
import EnterHeader from './components/Header/EnterHeader.vue'
import FooterPage from './components/CommonFooter/FooterPage.vue'
import LoadingScreen from "@/components/LoadingScreen/LoadingScreen.vue";
import {userSettingsStore} from "@/store/userSettingsStore.js";

const store = userSettingsStore()
store.initDefaultStorage()
</script>

<template>
  <div class="flex flex-column" style="min-height: 100vh; height: 100%">
    <cookie-dialog></cookie-dialog>
    <loading-screen/>
    <div style="position: sticky; top: 0; z-index: 99">
      <enter-header class="h-full"></enter-header>
    </div>
    <div class="flex justify-content-center">
      <router-view></router-view>
    </div>
    <footer-page></footer-page>
  </div>
</template>

<style scoped></style>
