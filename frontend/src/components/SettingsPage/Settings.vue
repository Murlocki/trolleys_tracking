<template>
    <div class="w-12 md:w-9 lg:w-7 shadow-2 mt-4 mb-4" style="border-radius: 15px">
        <profile
            :user-profile-back="store.$state.userData.userProfileBack"
            :userUsername="store.$state.userData.userLogin"
            :user-avatar="store.$state.userData.userAvatar"
            class="mb-4"
        ></profile>
        <div class="w-full mb-6 px-3 md:px-4" v-for="elem in textValues" :key="elem.id">
            <component :is="elem.component" v-bind="elem.attributes"></component>
        </div>
        <div class="flex justify-content-between w-full mb-6 px-3 md:px-4">
            <span class="text-lg lg:text-2xl border-bottom-1">Profile avatar</span>
            <picture-picker
                :setFunction="setAvatar"
                :buttonLabel="''"
                :stencil_component="CircleStencil"
                :ratio="{ X: 1, Y: 1 }"
            ></picture-picker>
        </div>
        <div class="flex justify-content-between w-full px-3 md:px-4 mb-5">
            <span class="text-lg lg:text-2xl border-bottom-1">Profile background</span>
            <picture-picker :setFunction="setProfileBack" :buttonLabel="''" :ratio="{ X: 2, Y: 1 }"> </picture-picker>
        </div>
        <personal-validator
            v-model:vis="openValidatorEmail"
            :validateValue="emailValue"
            title="Validate email changing"
            yourObject="email"
            :acceptFunction="handleSettingEmail"
            :resendFunction="handleResendEmailCode"
        ></personal-validator>
        <personal-validator
            v-model:vis="openValidatorPhone"
            :validateValue="phoneValue"
            title="Validate phone changing"
            yourObject="phone"
            :acceptFunction="handleSettingPhone"
            :resendFunction="handleResendPhoneCode"
        ></personal-validator>
    </div>
</template>

<script setup>
import PicturePicker from './PicturePicker.vue'
import {userSettingsStore} from '../../store/userSettingsStore'
import {computed, ref} from 'vue'
import InputEditor from './InputEditor.vue'
import PersonalValidator from './PersonalValidator.vue'
import BirthdatePicker from './BirthdatePicker.vue'
import Profile from './Profile.vue'

const store = userSettingsStore()

const back = computed(() => {
    return store.$state.userData.userProfileBack
})

const settingUserName = function (newValue) {
    store.setUserData(newValue, 'userUsername')
}
const settingFirstName = function (newValue) {
    store.setUserData(newValue, 'userFirstName')
}
const settingMiddleName = function (newValue) {
    store.setUserData(newValue, 'userMiddleName')
}
const settingLastName = function (newValue) {
    store.setUserData(newValue, 'userLastName')
}

//Валидация почты
const openValidatorEmail = ref(false)
const emailValue = ref('')

const handleSettingEmail = function (submitCode) {
    //Ну короче код типо верный
    store.setUserData(emailValue.value, 'userEmail')
}
const handleResendEmailCode = function () {
    //Типо перессылка или тип того
}
const settingEmail = function (newValue) {
    emailValue.value = newValue
    openValidatorEmail.value = true
}

//Для адреса
const settingAddress = function (newValue) {
    store.setUserData(newValue, 'address')
}
//Для кампании
const settingCompany = function (newValue) {
    store.setUserData(newValue, 'companyName')
}

//Валидация телефона
const openValidatorPhone = ref(false)
const phoneValue = ref('')

const handleSettingPhone = function (submitCode) {
    //Ну короче код типо верный
    store.setUserData(phoneValue.value, 'phoneNumber')
}
const handleResendPhoneCode = function () {
    //Типо перессылка или тип того
}
const settingPhone = function (newValue) {
    phoneValue.value = newValue
    openValidatorPhone.value = true
}
//Для даты рождения
const settingBirthdate = function (newValue) {
    store.setUserData(newValue, 'birthDate')
}

//Для аватара
const setAvatar = function (newValue) {
    store.setUserData(newValue, 'userAvatar')
}
const setProfileBack = function (newValue) {
    store.setUserData(newValue, 'userProfileBack')
}
const textValues = [
    {
        id: 0,
        component: InputEditor,
        attributes: {
            title: 'Username',
            originalValue: store.$state.userData.userUsername,
            acceptFunction: settingUserName,
        },
    },
    {
        id: 1,
        component: InputEditor,
        attributes: {
            title: 'First name',
            originalValue: store.$state.userData.userFirstName,
            acceptFunction: settingFirstName,
        },
    },
    {
        id: 2,
        component: InputEditor,
        attributes: {
            title: 'Middle name',
            originalValue: store.$state.userData.userMiddleName,
            acceptFunction: settingMiddleName,
        },
    },
    {
        id: 3,
        component: InputEditor,
        attributes: {
            title: 'Last name',
            originalValue: store.$state.userData.userLastName,
            acceptFunction: settingLastName,
        },
    },
    {
        id: 4,
        component: InputEditor,
        attributes: {
            title: 'User email',
            originalValue: store.$state.userData.userEmail,
            acceptFunction: settingEmail,
        },
    },
    {
        id: 5,
        component: InputEditor,
        attributes: {
            title: 'Address',
            originalValue: store.$state.userData.address,
            acceptFunction: settingAddress,
        },
    },
    {
        id: 6,
        component: InputEditor,
        attributes: {
            title: 'Company name',
            originalValue: store.$state.userData.companyName,
            acceptFunction: settingCompany,
        },
    },
    {
        id: 7,
        component: InputEditor,
        attributes: {
            title: 'Phone nubmer',
            originalValue: store.$state.userData.phoneNumber,
            acceptFunction: settingPhone,
        },
    },
    {
        id: 8,
        component: BirthdatePicker,
        attributes: {
            title: 'Birthdate',
            originalValue: store.$state.userData.birthDate,
            acceptFunction: settingBirthdate,
        },
    },
]
</script>

<style></style>
