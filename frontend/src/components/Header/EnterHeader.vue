<template>
    <div class="pt-4 bg-primary-reverse">
        <Toolbar class="p-0 mx-2 bg-primary-reverse border-0">
            <template #start>
                <Button
                    v-if="store.$state.isLoggged"
                    icon="pi pi-bars"
                    severity="secondary"
                    text
                    class="p-button-lg"
                    @click="visibleLeft = !visibleLeft"
                ></Button>
                <wemeet-name></wemeet-name>
            </template>
            <template #end>
                <wemeet-logo></wemeet-logo>
            </template>
        </Toolbar>
        <CommonSidebar v-model:visible="visibleLeft"></CommonSidebar>
    </div>
</template>

<script setup>
import WemeetName from './CommonElements/WemeetName.vue'
import WemeetLogo from './CommonElements/WemeetLogo.vue'
import Toolbar from 'primevue/toolbar'
import Button from 'primevue/button'
import { userSettingsStore } from '../../store/userSettingsStore'
import CommonSidebar from '../CommonSidebar/CommonSidebar.vue'

const store = userSettingsStore()
import { ref } from 'vue'
const visibleLeft = ref(false)
</script>

<style></style>
