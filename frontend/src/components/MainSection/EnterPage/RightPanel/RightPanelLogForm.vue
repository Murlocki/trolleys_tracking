<template>
    <transition name="block-transition">
        <div
            v-if="formOpen && textCl"
            class="shadow-4 bg-primary my-4"
            style="
                border-radius: 20px;
                height: fit-content;
                min-height: 360px;
                border: 3px solid black;
                min-width: 340px;
            "
        >
            <transition name="forms-create">
                <div v-if="formCreation" class="flex flex-column justify-content-center align-content-center">
                    <div class="flex justify-content-between border-bottom-2 border-primary-reverse px-3 py-2">
                        <p
                            style="font-family: 'Helvetica Neue', sans-serif"
                            class="font-bold text-l p-0 m-0 text-center mt-3 mb-2"
                        >
                            Log in
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
                    <form @submit.prevent="validateLoginForm">
                        <div v-for="item in loginFormEnters" v-bind:key="item.id" class="mx-3">
                            <p class="border-bottom-1 border-primary-reverse w-max pr-1 mb-2 ml-3">
                                {{ item.title }}
                            </p>
                            <div class="flex flex-column gap-1">
                                <component
                                    :is="item.component"
                                    v-model="item.value.value"
                                    v-bind="item.attributes"
                                    required
                                >
                                </component>
                            </div>
                            <div class="w-full border-bottom-1 border-primary-reverse w-11 mt-1"></div>
                        </div>
                      <div class="flex justify-content-center mt-4">
                        <div class="flex align-items-center">
                          <Checkbox v-model="remember" :binary="true"/>
                          <label for="ingredient1" class="ml-2"> Remember me </label>
                        </div>
                      </div>
                        <div class="flex justify-content-center mt-4">
                            <Button class="w-5 bg-primary-reverse" style="border-radius: 20px" type="submit" @click="onSubmit"
                                ><template #default>
                                    <div class="m-1 w-11 flex justify-content-between">
                                        <p class="m-0 font-medium text-lg">Log in</p>
                                        <img
                                            :src="themeIcon"
                                            alt="Custom Icon"
                                            style="width: 20px; height: 20px"
                                            class="bg-primary-reverse"
                                        />
                                    </div> </template
                            ></Button>
                        </div>
                        <div class="flex justify-content-center text-center">
                            <span class="text-xs mx-2 mt-2 text-red-500">{{ error }}</span>
                        </div>
                    </form>
                </div>
            </transition>
        </div>
    </transition>
</template>

<script setup>
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Checkbox from 'primevue/checkbox';
import { userSettingsStore } from '@/store/userSettingsStore.js'
import { ref } from 'vue'

const formOpen = defineModel('loginFormOpen')
const formCreation = defineModel('createdForm')
const textCl = defineModel('textCl')

const store = userSettingsStore()

function closeTheForm() {
    formCreation.value = false
    setTimeout(() => (textCl.value = false), 1000)
    setTimeout(() => (formOpen.value = false), 2000)
}
//Настройка компонентов формы
const userLogin = ref('test111')
const password = ref('Test2=test')
const remember = ref(false)
const ip= ref("")
const device = ref("")

const loginFormEnters = [
    {
        id: 1,
        title: 'Identifier',
        value: userLogin,
        component: InputText,
        attributes: {
            class: 'bg-primary-reverse text-base w-12',
            style: 'border-radius: 15px',
        },
    },
    {
        id: 2,
        title: 'Password',
        value: password,
        component: Password,
        attributes: {
            inputClass: 'bg-primary-reverse text-base w-12',
            inputStyle: { 'border-radius': '15px' },
            toggleMask: '',
            feedback: false,
        },
    },
]

//Настройка иконок
import { computed } from 'vue'
import { loginArrowWhite, loginArrowBlack } from '@assets/index.js'
import { backArrowBlack, backArrowWhite } from '@assets/index.js'
import {loginUser} from "@/externalRequests/requests.js";
import router from "@/router/index.js";
const themeIcon = computed(() => {
    if (!store.$state.darkModeOn) return loginArrowBlack
    return loginArrowWhite
})

const themeBackIcon = computed(() => {
    if (store.$state.darkModeOn) return backArrowBlack
    return backArrowWhite
})


/* Валидация формы */
import {UAParser} from 'ua-parser-js';
import {AuthForm} from "@/models/user/AuthForm.js"

const error = ref("");
const loading = ref(false);
const onSubmit = async () => {
  loading.value = true;
  const isValid = !!userLogin.value && !!password.value
  if (isValid) {

    const responseIp = await fetch('https://api.ipify.org?format=json')
    if (responseIp.ok) {
      const res = await responseIp.json()
      ip.value = res["ip"];
      console.log('IP пользователя:', ip.value);
    }
    const parser = new UAParser();
    device.value = parser.getResult().browser.name;
    console.log('Информация об устройстве:', device.value);


    const authForm = new AuthForm(userLogin.value, password.value, device.value, ip.value, remember.value);
    const response = await loginUser(authForm);
    const responseJson = await response.json();
    if (response.status === 200) {
      store.setJwtKey(responseJson["token"]);
      console.log(store.getJwt.value);
      store.setUserIdentifier(responseJson["identifier"]);
      closeTheForm()
      await router.push('/');
      loading.value = false;
      return;
    }

    error.value = response.status === 503? responseJson.message : responseJson['detail'];
    //console.log(response_json);
  } else {
    error.value = "Please input the password and identifier."
  }
  loading.value = false;
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
.block {
    margin-bottom: 20px;
    width: 20vh;
    min-width: 320px;
    height: 530px;
}
.block-transition-enter-active {
    transition: all 1s ease;
}
.block-transition-leave-active {
    transition: all 1s ease;
}

.block-transition-enter-from {
    transform: translateY(100%);
    opacity: 0;
}
.block-transition-leave-to {
    transform: translateY(100%);
    opacity: 0;
}
</style>
