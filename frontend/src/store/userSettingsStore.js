import {defineStore} from 'pinia'
import {computed, ref} from 'vue'
import {localUserStorage} from './localUserStorage'
import {cookieUserStorage} from './cookieUserStorage'

export const userSettingsStore = defineStore('userSettingsStore', () => {
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

    const storageChose = localStorage.getItem('wewatch-storageChose')
    console.log(storageChose)
    const choosedStorage = ref(!!storageChose)
    const storage = ref()
    function initDefaultStorage() {
        if (storageChose === 'cookie') {
            storage.value = cookieUserStorage()
        } else {
            storage.value = localUserStorage()
        }
        getJwt.value = computed(() => storage.value.getJwt)
        setJwtKey.value = function (newKey) {
            storage.value.setJwtKey(newKey)
        }
        isLogged.value = computed(() => storage.value.isLogged)
        clearJwt.value = storage.value.clearJwt;
    }


    function chooseStorage(selectedStorage, name) {
        localStorage.setItem('wewatch-storageChose', name)
        choosedStorage.value = true

        storage.value = selectedStorage
        getJwt.value = computed(() => storage.value.getJwt)
        setJwtKey.value = function (newKey) {
            storage.value.setJwtKey(newKey)
        }
        clearJwt.value = function () {
            storage.value.clearJWT()
        }
        isLogged.value = computed(() => storage.value.isLoggedIn)
    }


    const getJwt = ref()
    const setJwtKey = ref()
    const clearJwt = ref()
    const isLogged = ref()

    const userIdentifier = ref('')
    function setUserIdentifier(identifier) {
        userIdentifier.value = identifier
    }

    const loading = ref(false)
    function setLoading(load) {
        loading.value = load
    }
    const isLoading = computed(() => loading.value)

    return {
        storage,
        getJwt,
        setJwtKey,
        clearJwt,
        initDefaultStorage,

        darkModeOn,
        setVisualMode,
        changeTheme,

        choosedStorage,
        chooseStorage,

        isLogged,
        userIdentifier,
        setUserIdentifier,

        isLoading,
        setLoading
    }
})
