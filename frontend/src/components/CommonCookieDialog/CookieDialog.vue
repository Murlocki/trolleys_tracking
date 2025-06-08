<template>
    <Dialog v-model:visible="showDialog" header="Cookies" :style="{ width: '25rem', height: '200px' }" position="top">
        <span class="p-text-secondary mb-5">Do you want to use cookie?</span>
        <div class="flex justify-content-between mt-5">
            <Button
                type="button"
                label="Accept"
                severity="secondary"
                @click="setStorate(cookieStorage, 'cookie')"
            ></Button>
            <Button type="button" label="Cancel" @click="setStorate(localStore, 'local')"></Button>
        </div>
    </Dialog>
</template>

<script setup>
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import { userSettingsStore } from '../../store/userSettingsStore'
import { computed } from 'vue'
import { localUserStorage } from '../../store/localUserStorage'
import { cookieUserStorage } from '../../store/cookieUserStorage'
const store = userSettingsStore()

const localStore = localUserStorage()
const cookieStorage = cookieUserStorage()

function setStorate(storage, name) {
    console.log(storage)
    store.chooseStorage(storage, name)
    console.log(storage.getJwt)
}

const showDialog = computed(() => !store.$state.choosedStorage)
</script>

<style></style>
