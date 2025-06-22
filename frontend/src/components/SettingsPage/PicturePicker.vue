<template>
    <div style="width: fit-content">
        <div style="width: fit-content">
            <FileUpload
                url="/api/upload"
                accept="image/*"
                mode="basic"
                :maxFileSize="1000000"
                :auto="true"
                customUpload
                @select="onSelect"
                :chooseLabel="props.buttonLabel"
                :multiple="false"
            ></FileUpload>
        </div>
        <Dialog v-model:visible="openCropper" modal header="Edit avatar picture" class="w-full sm:w-10 md:w-8 lg:w-6">
            <div class="flex flex-column align-items-center justify-content-center w-12">
                <div class="flex justify-content-between mt-4 w-10">
                    <Button
                        icon="pi pi-check"
                        label="Accept"
                        @click="handleAccept"
                        style="border-radius: 20px"
                    ></Button>
                    <Button
                        icon="pi pi-times"
                        label="Cancel"
                        @click="handleCancel"
                        style="border-radius: 20px"
                    ></Button>
                </div>
            </div>
        </Dialog>
    </div>
</template>

<script setup>
import FileUpload from 'primevue/fileupload'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import {ref} from 'vue'


const props = defineProps({
    setFunction: Function,
    buttonLabel: String,
    stencil_component: Object,
    ratio: {
        X: Number,
        Y: Number,
    },
})

const selectedPicBlob = ref('')
const openCropper = ref(false)

const onSelect = (event) => {
    selectedPicBlob.value = event.files[0].objectURL
    console.log(event.files[0])
    //console.log(selectedPicBlob.value)
    openCropper.value = true
}

const res = ref('')
const change = function ({ coordinates, canvas }) {
    //console.log(coordinates, canvas)
    res.value = canvas.toDataURL()
}

//Обработка принятия
const handleAccept = function () {
    props.setFunction(res.value)
    openCropper.value = false
}
/*Обработка отказа */
const handleCancel = function () {
    selectedPicBlob.value = null
    openCropper.value = false
}
</script>

<style></style>
