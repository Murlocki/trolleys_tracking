<template>
    <div
        class="grid-background mt-5 flex align-items-center justify-content-center flex-wrap md:flex-nowrap bg-primary-reverse"
        style="height: fit-content"
    >
        <image-slider class="md:mr-4 lg:mr-4"></image-slider>
        <right-panel-enter class="md:ml-4 lg:ml-4"></right-panel-enter>
    </div>
</template>

<script setup>
import ImageSlider from './ImageSlider.vue'
import RightPanelEnter from './RightPanel/RightPanelEnter.vue'
</script>

<style>
.grid-background {
    width: 100%;
    height: 100vh;
    background-color: white;
    background-image: linear-gradient(to right, #e0e0e05e 1px, transparent 1px),
        linear-gradient(to bottom, #e0e0e05e 1px, transparent 1px);
    background-size: 200px 130px;
    background-position: -1px -1px;
}
</style>
