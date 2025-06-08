import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { userSettingsStore } from './userSettingsStore'
export const localUserStorage = defineStore('localUserStorage', () => {
    const store = userSettingsStore()
    const jwtKey = ref('')
    function setJwtKey(newKey) {
        const currentLogin = store.$state.currentLogin
        jwtKey.value = newKey
        localStorage.setItem(currentLogin, jwtKey.value)
    }
    const getJwt = computed(() => jwtKey.value)
    return { jwtKey, setJwtKey, getJwt }
})
