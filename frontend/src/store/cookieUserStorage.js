import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import Cookies from 'js-cookie'
import { userSettingsStore } from './userSettingsStore'
export const cookieUserStorage = defineStore('cookieUserStorage', () => {
    function setJwtKey(newKey) {
        Cookies.set('wewatch-token', newKey)
        console.log('setJwtKey', newKey)
    }
    const getJwt = computed(() => Cookies.get('wewatch-token'))
    const clearJwt = () => {
        Cookies.remove('wewatch-token')
    }
    return { setJwtKey, getJwt, clearJwt }
})
