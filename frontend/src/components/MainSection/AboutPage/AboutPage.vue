<template>
    <div class="grid flex justify-content-center flex-wrap my-4 mx-0 md:mx-5">
        <div v-for="item in imagesData" :key="item.id" class="col-12 sm:col-9 md:col-5 flex justify-content-center">
            <Card class="w-10 lg:w-8">
                <template #header>
                    <img alt="user header" :src="item.filePath" class="w-full h-15rem border-round-top-xl" />
                </template>
                <template #title
                    ><span class="text-sm md:text-base lg:text-lg">{{ item.title }}</span></template
                >
                <template #content>
                    <p class="text-sm md:text-base lg:text-lg m-0">
                        {{ item.text }}
                    </p>
                </template>
            </Card>
        </div>
    </div>
</template>

<script setup>
import Card from 'primevue/card'
import imagesData from '@assets/aboutUsImages/aboutImages.json'
</script>

<style></style>
