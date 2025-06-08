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

    //Для логирования
    const currentLogin = ref('')
    const setLoggin = function (value) {
        currentLogin.value = value
    }
    const isLoggged = ref(false)
    const setLogged = function (value) {
        isLoggged.value = value
    }
    /*Короче надо как-то сделать чтобы можно было хранить ключи кучи пользователей на 1 компе */
    const userData = ref({
        userUsername: 'loginnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn',
        userFirstName: 'kir',
        userMiddleName: 'kor',
        userLastName: 'ov',
        userEmail: 'kkeekekek@gmail.com',
        companyName: '',
        phoneNumber: '',
        birthDate: '',
        address: '',
        userAvatar: '/src/assets/DefaultUser/defaultUser.svg',
        userProfileBack: '',
    })
    function setUserData(newValue, valueKey) {
        userData.value[valueKey] = newValue
    }

    //Выбор хранилища для jwt ключа
    const storageChose = localStorage.getItem('wemeet-storageChose')
    console.log(storageChose)

    const choosedStorage = ref(storageChose ? true : false)

    //Пусть оно по умолчанию будет локальным,чтобы все работало
    const storage = ref()
    function initDefaultStorage() {
        if (storageChose == 'cookie') {
            storage.value = cookieUserStorage()
            getJwt.value = computed(() => storage.value.getJwt())
            setJwtKey.value = function (newKey) {
                storage.value.setJwtKey(newKey)
            }
        } else {
            storage.value = localUserStorage()
            getJwt.value = computed(() => storage.value.getJwt())
            setJwtKey.value = function (newKey) {
                storage.value.setJwtKey(newKey)
            }
            console.log(setJwtKey.value)
        }
    }

    function chooseStorage(selectedStorage, name) {
        localStorage.setItem('wemeet-storageChose', name)
        console.log(localStorage.getItem('wemeet-storageChose'))
        choosedStorage.value = true

        storage.value = selectedStorage
        getJwt.value = computed(() => storage.value.getJwt())
        setJwtKey.value = function (newKey) {
            storage.value.setJwtKey(newKey)
        }
    }

    const getJwt = ref()
    const setJwtKey = ref()

    return {
        storage,
        getJwt,
        setJwtKey,
        initDefaultStorage,

        darkModeOn,
        setVisualMode,

        choosedStorage,
        chooseStorage,

        isLoggged,
        setLogged,
        userData,
        setUserData,

        currentLogin,
        setLoggin,
    }
})
