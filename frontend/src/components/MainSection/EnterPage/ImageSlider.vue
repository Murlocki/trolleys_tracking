<template>
    <div
        class="p-2 w-12 md:w-8"
        style="
            background-color: rgba(123, 122, 122, 0.11);
            width: fit-content;
            height: fit-content;
            border-radius: 30px;
            will-change: transform;
        "
    >
        <Galleria
            v-memo="[images]"
            :value="images"
            :numVisible="5"
            :circular="true"
            containerStyle="max-width: 1280px;min-width:280px;border-radius: 30px"
            :showItemNavigators="true"
            :showThumbnails="false"
            :showItemNavigatorsOnHover="true"
            :showIndicators="false"
            :autoPlay="true"
            :transitionInterval="40000"
        >
            <template v-if="images.length > 0" #item="slotProps">
                <transition name="fade" mode="out-in">
                    <div :key="slotProps.item.id" class="image-container">
                        <img class="gallery-image" :src="slotProps.item.filePath" alt="Картинка презентация" />
                    </div>
                </transition>
                <transition name="fade" mode="out-in">
                    <div
                        class="p-galleria-caption"
                        :key="slotProps.item.id"
                        style="border-radius: 30px; margin: 0 0 0 0px"
                    >
                        <div class="text-lx mb-2 font-bold" style="border-radius: 30px">{{ slotProps.item.title }}</div>
                        <p class="text-l text-white" style="border-radius: 30px">{{ slotProps.item.text }}</p>
                    </div>
                </transition>
            </template>
            <template #thumbnail="slotProps">
                <div :key="slotProps.item.id" class="image-container">
                    <img class="gallery-image" :src="slotProps.item.filePath" alt="Картинка презентация" />
                </div>
            </template>
        </Galleria>
    </div>
</template>

<script setup>
import Galleria from 'primevue/galleria'
import { ref } from 'vue'
import imagesData from '@assets/sliderImages/sliderImages.json'
const images = ref([])
images.value = imagesData
</script>

<style>
.image-container {
    height: 75vh; /* 80% от высоты viewport */
    width: 100%;
    max-width: 1280px; /* 65% от 1920px */
    max-height: 864px; /* 80% от 1080px */
    margin: 0 auto; /* Центрирование контейнера */
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 30px;
}
.gallery-image {
    width: 100%;
    height: 100%;
    object-fit: fill;
    object-position: center;
    border-radius: 30px;
}

.fade-enter-active,
.fade-leave-active {
    transition: all 0.45s ease;
}

.fade-enter-from {
    opacity: 0;
}
.fade-leave-to {
    opacity: 0;
}
</style>
