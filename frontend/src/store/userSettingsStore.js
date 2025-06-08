import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import Cookies from 'js-cookie'
import { localUserStorage } from './localUserStorage'
import { cookieUserStorage } from './cookieUserStorage'
export const userSettingsStore = defineStore('userSettingsStore', () => {
    //Выбор темы
    const darkModeOn = ref(false)
    function setVisualMode() {
        darkModeOn.value = !darkModeOn.value
    }

    function changeTheme(currentTheme, newTheme, callback) {
        const themeElement = document.getElementById('theme-css');

        if (themeElement) {
            const newHref = themeElement.getAttribute('href').replace(currentTheme, newTheme);
            const cloneLink = themeElement.cloneNode(true);
            cloneLink.setAttribute('href', newHref);
            cloneLink.setAttribute('id', 'theme-css-clone');

            cloneLink.addEventListener('load', () => {
                themeElement.remove();
                cloneLink.setAttribute('id', 'theme-css');
                if (callback) callback();
            });

            themeElement.parentNode.insertBefore(cloneLink, themeElement.nextSibling);
        }
    }

    //Выбор хранилища для jwt ключа
    const storageChose = localStorage.getItem('wewatch-storageChose')
    //localStorage.clear()
    console.log(storageChose)

    const choosedStorage = ref(!!storageChose)

    //Пусть оно по умолчанию будет локальным,чтобы все работало
    const storage = ref()
    function initDefaultStorage() {
        if (storageChose === 'cookie') {
            storage.value = cookieUserStorage()
            getJwt.value = computed(() => storage.value.getJwt)
            setJwtKey.value = function (newKey) {
                storage.value.setJwtKey(newKey)
            }
        } else {
            storage.value = localUserStorage()
            getJwt.value = computed(() => storage.value.getJwt)
            setJwtKey.value = function (newKey) {
                storage.value.setJwtKey(newKey)
            }
            console.log(getJwt.value)
            console.log(setJwtKey.value)
        }
    }

    function chooseStorage(selectedStorage, name) {
        localStorage.setItem('wewatch-storageChose', name)
        console.log(localStorage.getItem('wewatch-storageChose'))
        choosedStorage.value = true

        storage.value = selectedStorage
        getJwt.value = computed(() => storage.value.getJwt())
        setJwtKey.value = function (newKey) {
            storage.value.setJwtKey(newKey)
        }
    }

    const isLogged = computed(() => !!getJwt.value)

    const getJwt = ref()
    const setJwtKey = ref()

    const userIdentifier = ref('')
    function setUserIdentifier(identifier) {
        userIdentifier.value = identifier
    }
    return {
        storage,
        getJwt,
        setJwtKey,
        initDefaultStorage,

        darkModeOn,
        setVisualMode,
        changeTheme,

        choosedStorage,
        chooseStorage,

        isLogged,
        userIdentifier,
        setUserIdentifier
    }
})
