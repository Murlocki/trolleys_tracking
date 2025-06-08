<template>
    <div class="w-12 bg-primary" style="border-radius: 15px 15px 0 0">
        <div
            class="bg-primary-reverse w-12 profile-background profile-background-height"
            style="border-radius: 15px 15px 0 0; z-index: 1"
        >
            <img v-if="back" :src="back" alt="" style="border-radius: 15px 15px 0 0" />
        </div>
        <div class="flex align-items-start justify-content-between w-12 mb-2 mt-3 px-3 pb-3 pt-0">
            <div class="flex justify-content-start align-items-end w-10 md:w-7 p-0 m-0">
                <div class="flex justify-content-center align-items-center mr-3" style="margin-top: -100%">
                    <Avatar
                        :image="props.userAvatar"
                        class="border-1 border-primary bg-primary"
                        style="width: 90px; height: 90px; z-index: 2"
                        shape="circle"
                    ></Avatar>
                </div>
                <span class="font-bold text-xl" style="overflow: hidden; text-overflow: ellipsis; width: 200px">
                    {{ props.userUsername }}
                </span>
            </div>
            <Button class="border-circle bg-primary-reverse" icon="pi pi-inbox" />
        </div>
    </div>
</template>

<script setup>
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import { computed } from 'vue'

const props = defineProps({
    userProfileBack: Object,
    userAvatar: Object,
    userUsername: String,
    userId: Number,
})

const back = computed(() => {
    return props.userProfileBack
})
</script>

<style>
.profile-background {
    position: relative;
    width: 100%;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}

.profile-background img {
    width: 100%;
    height: 100%;
}

.profile-background-height {
    height: 180px;
    @media (width<992px) {
        height: 170px;
    }
    @media (width<768px) {
        height: 150px;
    }
    @media (width<576px) {
        height: 120px;
    }
}
</style>
