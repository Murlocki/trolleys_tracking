import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { userSettingsStore } from './userSettingsStore'
export const localUserStorage = defineStore('localUserStorage', () => {
    function setJwtKey(newKey) {
        localStorage.setItem("wewatch-token", newKey)
    }
    const getJwt = computed(() => localStorage.getItem("wewatch-token"))
    const clearJWT = () => {
        localStorage.removeItem("wewatch-token")
    }
    const isLogged = computed(() => {
        return !!getJwt.value
    })
    return { setJwtKey, getJwt, clearJWT, isLogged }
})
