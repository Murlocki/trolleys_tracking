<template>
    <transition name="block-transition">
        <div
            v-if="formOpen && textCl"
            class="shadow-4 my-4 pb-2 bg-primary-reverse flex w-8"
            style="
                border-radius: 20px;
                min-height: 540px;
                height: fit-content;
                border: 3px solid white;
                min-width: 300px;
            "
        >
            <transition name="forms-create">
                <div v-if="formCreation" class="flex flex-column justify-content-center align-content-center w-full">
                    <div class="flex justify-content-between border-bottom-2 border-primary px-3 py-2">
                        <p
                            style="font-family: 'Helvetica Neue', sans-serif"
                            class="font-bold text-base md:text-l p-0 m-0 text-center mt-3 mb-2"
                        >
                            sigh up
                        </p>
                        <Button
                            @click="closeTheForm"
                            severity="secondary"
                            rounded
                            style="width: fit-content"
                            class="px-2"
                            text
                        >
                            <img :src="themeBackIcon" alt="Custom Icon" style="width: 20px; height: 20px" />
                        </Button>
                    </div>
                    <div class="flex justify-content-center">
                        <form @submit.prevent="validateRegisterForm" class="w-11">
                            <div v-for="item in registerFormEnters" v-bind:key="item.id">
                                <p class="border-bottom-1 border-primary w-max pr-1 mb-2 ml-3">{{ item.title }}</p>
                                <div class="flex flex-column gap-1">
                                    <component
                                        :is="item.component"
                                        v-model="item.value.value"
                                        v-bind="item.attributes"
                                        :invalid="item.id == incorrectField ? true : false"
                                        required
                                    >
                                    </component>
                                </div>
                                <div class="w-full border-bottom-1 border-primary w-11 mt-1"></div>
                            </div>
                            <div class="flex justify-content-center mt-4">
                                <Button type="submit" class="w-6" style="border-radius: 20px"
                                    ><template #default>
                                        <div class="m-1 flex justify-content-between w-full">
                                            <p class="m-0 font-medium text-lg">Register</p>
                                            <div>
                                                <img
                                                    :src="themeIcon"
                                                    alt="Custom Icon"
                                                    style="width: 20px; height: 20px"
                                                />
                                            </div>
                                        </div> </template
                                ></Button>
                            </div>
                            <div class="flex justify-content-center text-xs text-500">
                                <span class="mr-1">By registering you agree to</span
                                ><router-link class="active-link text-500 underline" to="/treat" target="_blank"
                                    >terms of use</router-link
                                >
                            </div>
                            <div class="flex justify-content-center text-center">
                                <span class="text-xs mx-2 mt-2 text-red-500">{{ errorMessage }}</span>
                            </div>
                        </form>
                    </div>
                </div>
            </transition>
        </div>
    </transition>
</template>

<script setup>
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import { ref } from 'vue'
const formOpen = defineModel('registerFormOpen')
const formCreation = defineModel('createdForm')
const textCl = defineModel('textCl')

function closeTheForm() {
    formCreation.value = false
    setTimeout(() => (textCl.value = false), 1000)
    setTimeout(() => (formOpen.value = false), 2000)
}

const email = ref('')
const userName = ref('')
const password1 = ref('')
const password2 = ref('')
const registerFormEnters = [
    {
        id: 0,
        title: 'Email',
        value: email,
        component: InputText,
        attributes: {
            class: 'bg-primary text-base w-12',
            style: 'border-radius: 15px',
        },
    },
    {
        id: 1,
        title: 'UserName',
        value: userName,
        component: InputText,
        attributes: {
            class: 'bg-primary text-base w-12',
            style: 'border-radius: 15px',
        },
    },
    {
        id: 2,
        title: 'Password',
        value: password1,
        component: Password,
        attributes: {
            inputClass: 'bg-primary text-base w-12',
            inputStyle: { 'border-radius': '15px' },
            toggleMask: '',
        },
    },
    {
        id: 3,
        title: 'Repeat password',
        value: password2,
        component: Password,
        attributes: {
            inputClass: 'bg-primary text-base w-12',
            inputStyle: { 'border-radius': '15px' },
            toggleMask: '',
        },
    },
]
const incorrectField = ref(-1)

import { computed } from 'vue'
import { loginArrowWhite, loginArrowBlack } from '@assets/index.js'
import { backArrowBlack, backArrowWhite } from '@assets/index.js'
import { userSettingsStore } from '../../../../store/userSettingsStore'
import RegisterFormValidator from '/src/validators/RegisterFormValidator.js'
const store = userSettingsStore()
const themeIcon = computed(() => {
    if (store.$state.darkModeOn) return loginArrowBlack
    return loginArrowWhite
})

const themeBackIcon = computed(() => {
    if (!store.$state.darkModeOn) return backArrowBlack
    return backArrowWhite
})

/* Валидация формы */
const errorMessage = ref('')
function validateRegisterForm() {
    const regFormValidator = RegisterFormValidator
    errorMessage.value = ''
    if (!regFormValidator.validateEmail(email.value)) {
        errorMessage.value = 'Incorrect email'
        incorrectField.value = 0
        return
    }
    if (!regFormValidator.validateUsername(userName.value)) {
        errorMessage.value = 'Incorrect userName'
        incorrectField.value = 1
        return
    }
    if (!regFormValidator.validatePassword(password1.value)) {
        errorMessage.value =
            'Password must consist 1 number,1 capital and 1 small letter, 1 special symbol @$!%*?&+=-, have length at least 8 symbols'
        incorrectField.value = 2
        return
    }
    if (password1.value != password2.value) {
        errorMessage.value = 'Passwords must be the same'
        incorrectField.value = 3
        return
    }
    incorrectField.value = -1
    return true
}
</script>
<style>
.forms-create-enter-active {
    transition: all 1s ease-out;
}

.forms-create-leave-active {
    transition: all 1s cubic-bezier(1, 0.5, 0.8, 1);
}

.forms-create-enter-from,
.forms-create-leave-to {
    transform: translateX(-20px);
    opacity: 0;
}

/*Анимация появления формы */
.block-transition-enter-active {
    transition: all 2s ease;
}
.block-transition-leave-active {
    transition: all 2s ease;
}

.block-transition-enter-from {
    transform: translateY(100%);
    opacity: 0;
}
.block-transition-leave-to {
    transform: translateY(100%);
    opacity: 0;
}

.active-link {
    text-decoration: none;
}

.active-link:hover {
    text-decoration: none;
}
</style>
