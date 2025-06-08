<template>
    <div class="m-0 flex flex-column bg-primary-reverse" style="height: fit-content">
        <div class="flex justify-content-center w-screen bg-primary-reverse" style="flex: 1">
            <div
                class="flex w-11 justify-content-center align-content-center bg-primary-reverse mb-2"
                style="height: fit-content"
            >
                <div
                    class="flex flex-column align-items-center w-12 md:w-9 lg:w-7 shadow-2 mt-4 mb-4"
                    style="border-radius: 15px"
                >
                    <profile
                        :userProfileBack="userInfo.userProfileBack"
                        :userUsername="userInfo.userUsername"
                        :userAvatar="userInfo.userAvatar"
                        class="mb-4"
                    ></profile>
                    <div
                        class="mr-2 ml-2 flex flex-column justify-content-between w-11 mb-6 px-3 md:px-4 text-lg md:text-xl bg-primary border-round-2xl py-2"
                        v-for="elem in textValues"
                        :key="elem.id"
                    >
                        <span class="border-bottom-1">{{ elem.title }}</span>
                        <p style="word-wrap: break-word; overflow-wrap: break-word">{{ elem.val }}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import Profile from '../../SettingsPage/Profile.vue'
import { onBeforeMount, ref } from 'vue'
import UserGetService from '../../../services/UserGetService'
import { onBeforeRouteUpdate } from 'vue-router'
import { useRoute } from 'vue-router'
import Inplace from 'primevue/inplace'

const userInfo = ref({})
const userGet = new UserGetService()
onBeforeRouteUpdate(async (to, from) => {
    // обработка изменения параметров маршрута...
    userInfo.value = userGet.getUser(to.params.id)
    console.log(userInfo.value)
})

const router = useRoute()

const textValues = ref([])

onBeforeMount(async () => {
    // обработка изменения параметров маршрута...
    console.log(router)
    userInfo.value = userGet.getUser(router.params.id)
    console.log(userInfo.value)
    console.log(textValues.value[0])
    textValues.value = [
        {
            id: 0,
            title: 'Username',
            val: userInfo.value.userUsername,
        },
        {
            id: 1,
            title: 'First name',
            val: userInfo.value.userFirstName,
        },
        {
            id: 2,
            title: 'Middle name',
            val: userInfo.value.userMiddleName,
        },
        {
            id: 3,
            title: 'Last name',
            val: userInfo.value.userLastName,
        },
        {
            id: 4,
            title: 'User email',
            val: userInfo.value.userEmail,
        },
        {
            id: 5,
            title: 'Address',
            val: userInfo.value.address,
        },
        {
            id: 6,
            title: 'Company name',
            val: userInfo.value.companyName,
        },
        {
            id: 7,
            title: 'Phone number',
            val: userInfo.value.phoneNumber,
        },
        {
            id: 8,
            title: 'Birthdate',
            val: userInfo.value.birthDate,
        },
    ]
})
</script>

<style></style>
