import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import Cookies from 'js-cookie'
import { userSettingsStore } from './userSettingsStore'
export const cookieUserStorage = defineStore('cookieUserStorage', () => {
    const store = userSettingsStore()
    const jwtKey = ref('')
    function setJwtKey(newKey) {
        const currentLogin = store.$state.currentLogin
        jwtKey.value = newKey
        Cookies.set(currentLogin, newKey)
    }
    const getJwt = computed(() => jwtKey.value)
    return { jwtKey, setJwtKey, getJwt }
})
