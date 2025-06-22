<template>
    <Dialog v-model:visible="showDialog" header="Cookies" :style="{ width: '25rem', height: '200px' }" position="top">
        <span class="p-text-secondary mb-5">Do you want to use cookie?</span>
        <div class="flex justify-content-between mt-5">
            <Button
                type="button"
                label="Accept"
                severity="secondary"
                @click="setStorage(cookieStorage, 'cookie')"
            ></Button>
            <Button type="button" label="Cancel" @click="setStorage(localStore, 'local')"></Button>
        </div>
    </Dialog>
</template>

<script setup>
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import {userSettingsStore} from '@/store/userSettingsStore.js'
import {computed} from 'vue'
import {localUserStorage} from '@/store/localUserStorage.js'
import {cookieUserStorage} from '@/store/cookieUserStorage.js'

const store = userSettingsStore()

const localStore = localUserStorage()
const cookieStorage = cookieUserStorage()

function setStorage(storage, name) {
    store.chooseStorage(storage, name)
}
const showDialog = computed(() => !store.isLogged)
</script>

<style></style>
