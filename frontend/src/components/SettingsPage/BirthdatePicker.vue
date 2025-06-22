<template>
    <div class="flex flex-column justify-content-between">
        <div class="mb-2 border-bottom-1" style="width: fit-content">
            <span class="text-lg lg:text-2xl">{{ props.title }}</span>
        </div>
        <div class="flex justify-content-between w-12">
            <Calendar :placeholder="inputValue" v-model="inputValue" class="w-7" :disabled="!openEditor" />
            <div :class="['flex', computedFlex, 'align-items-center w-4 sm:w-2']" style="max-width: 100px">
                <transition name="edit-appear">
                    <Button
                        v-if="!openEditor"
                        @click="openEditingMode"
                        icon="pi pi-pencil"
                        class="border-circle md:p-button-lg"
                    ></Button>
                </transition>
                <transition name="accept-appear">
                    <Button
                        @click="acceptEditingMode"
                        v-if="openEditingButtons"
                        class="border-circle custom-button md:p-button-lg"
                        icon="pi pi-check"
                    ></Button>
                </transition>
                <transition name="close-appear">
                    <Button
                        v-if="openEditingButtons"
                        @click="closeEditingMode"
                        icon="pi pi-times"
                        class="border-circle md:p-button-lg"
                    ></Button>
                </transition>
            </div>
        </div>
    </div>
</template>

<script setup>
import {ref} from 'vue'
import Calendar from 'primevue/calendar'
import Button from 'primevue/button'

const props = defineProps({
    title: String,
    acceptFunction: Function,
    originalValue: String,
})

const inputValue = ref(props.originalValue)

const computedFlex = ref('justify-content-end')

//Открытие редактирования
const openEditor = ref(false)
const openEditingButtons = ref(false)
const openEditingMode = function () {
    openEditor.value = true
    setTimeout(() => {
        openEditingButtons.value = true
        computedFlex.value = 'justify-content-between'
    }, 1000)
}

//Закрытие редактирования
const closeEditingMode = function () {
    openEditingButtons.value = false
    setTimeout(() => {
        openEditor.value = false
        computedFlex.value = 'justify-content-end'
    }, 1000)
    inputValue.value = props.originalValue
}
//Принятие редактирования
const acceptEditingMode = function () {
    openEditingButtons.value = false
    setTimeout(() => {
        openEditor.value = false
        computedFlex.value = 'justify-content-end'
    }, 1000)
    props.acceptFunction(inputValue.value)
}
</script>

<style>
/*Анимация исчезновения кнопки редактирования */
.edit-appear-enter-active {
    transition: all 1s ease;
}
.edit-appear-leave-active {
    transition: all 1s ease;
}

.edit-appear-enter-from {
    opacity: 0;
}
.edit-appear-leave-to {
    opacity: 0;
}

/*Анимация появления кнопок приниятия и отклонения */
.accept-appear-enter-active {
    transform-origin: 50% 50%;
    transition: all 1s ease;
}
.accept-appear-leave-active {
    transform-origin: 50% 50%;
    transition: all 1s ease;
}

.accept-appear-enter-from {
    transform: translateX(100%) rotate(360deg);
    opacity: 0;
}
.accept-appear-leave-to {
    transform: translateX(100%) rotate(360deg);
    opacity: 0;
}

.close-appear-enter-active {
    transform-origin: 50% 50%;
    transition: all 1s ease;
}
.close-appear-leave-active {
    transform-origin: 50% 50%;
    transition: all 1s ease;
}

.close-appear-enter-from {
    transform: translateX(100%) rotate(360deg);
    opacity: 0;
}
.close-appear-leave-to {
    transform: translateX(100%) rotate(360deg);
    opacity: 0;
}
</style>
