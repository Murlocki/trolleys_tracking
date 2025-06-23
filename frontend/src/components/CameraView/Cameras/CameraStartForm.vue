<script setup>
import Dialog from "primevue/dialog";
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import {defineEmits, onMounted} from "vue";
import Dropdown from "primevue/dropdown";
import {userSettingsStore} from "@/store/userSettingsStore.js";
import Toast from "primevue/toast";
import {useToast} from "primevue/usetoast";
import {cameraFormStore} from "@/store/cameras/cameraFormStore.js";
import {cameraControlStore} from "@/store/cameras/cameraControlStore.js";

// Store instances initialization
const cameraControl = cameraControlStore();
const userSettings = userSettingsStore()
const toast = useToast();

const detectionOptions = [
  {"label":"Yolo8", value:"yoloV8x"},
]
const classificationOptions = [
  {"label":"ResNet", value:"ResNet"},
]
const trackinOptions = [
  {"label":"deepsort", value:"deepsort"},
]

// Close dialog handler
async function onClose() {
  cameraControl.setVisible(false);
}



// Form submission handler
async function onAccept() {
  userSettings.setLoading(true);
  const token = userSettings.getJwt.value;
  // Determine whether to create or update user
  const response = await cameraControl.startCameraProcess(token);
  // Handle API errors
  if (!(response.status === 201 || response.status === 200)) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: `${response.status}: ${response.message}`,
      life: 3000
    });
    userSettings.setLoading(false);
    return;
  }

  // Update token and reload parent component
  userSettings.setJwtKey(response.token);
  userSettings.setLoading(false);
  cameraControl.setVisible(false);
}
</script>

<template>
  <Toast/>
  <!-- User form dialog -->
  <Dialog
      v-model:visible="cameraControl.visible"
      modal
      class="md:w-5 sm:w-8 w-11"
      :closable="false"
  >
    <template #header>
      <div>
        <span class="text-2xl">Camera process form</span>
      </div>
    </template>

    <div class="flex flex-column gap-4">
      <div class="flex flex-column gap-2">
        <label for="address">Detection regime</label>
        <Dropdown
            id="address"
            v-model="cameraControl.detectionRegime"
            :options="detectionOptions"
            option-label="label"
            option-value="value"
            aria-describedby="address-help"
        />
        <small id="address-help">Choose camera detection regime.</small>
      </div>
    </div>
    <div class="flex flex-column gap-4">
      <div class="flex flex-column gap-2">
        <label for="address">Classification regime</label>
        <Dropdown
            id="address"
            v-model="cameraControl.classificationRegime"
            :options="classificationOptions"
            option-label="label"
            option-value="value"
            aria-describedby="address-help"
        />
        <small id="address-help">Choose camera classification regime.</small>
      </div>
    </div>
    <div class="flex flex-column gap-4">
      <div class="flex flex-column gap-2">
        <label for="address">Tracking regime</label>
        <Dropdown
            id="address"
            v-model="cameraControl.trackingRegime"
            :options="trackinOptions"
            option-label="label"
            option-value="value"
            aria-describedby="address-help"
        />
        <small id="address-help">Choose camera tracking regime.</small>
      </div>
    </div>

    <!-- Dialog footer with action buttons -->
    <template #footer>
      <div class="w-full flex flex-row justify-content-between align-items-center">
        <Button label="Accept" size="large" @click="onAccept"/>
        <Button label="Close" class="bg-primary-reverse" size="large" @click="onClose"/>
      </div>
    </template>
  </Dialog>
</template>

<style scoped>
/* Component-specific styles would go here */
</style>