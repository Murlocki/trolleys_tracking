<template>
    <div class="pt-4 bg-primary-reverse">
        <Toolbar class="p-0 mx-2 bg-primary-reverse border-0">
            <template #start>
                <Button
                    v-if="store.isLogged.value"
                    icon="pi pi-bars"
                    severity="secondary"
                    text
                    class="p-button-lg"
                    @click="visibleLeft = !visibleLeft"
                ></Button>
                <wemeet-name></wemeet-name>
            </template>
            <template #end>
                <watch-logo></watch-logo>
            </template>
        </Toolbar>
        <CommonSidebar v-model:visible="visibleLeft"></CommonSidebar>
    </div>
</template>

<script setup>
import WemeetName from './CommonElements/WemeetName.vue'
import WatchLogo from './CommonElements/WatchLogo.vue'
import Toolbar from 'primevue/toolbar'
import Button from 'primevue/button'
import CommonSidebar from '../CommonSidebar/CommonSidebar.vue'
import {ref} from 'vue'
import {userSettingsStore} from "@/store/userSettingsStore.js";

const store = userSettingsStore();
const visibleLeft = ref(false);
</script>

<style></style>
