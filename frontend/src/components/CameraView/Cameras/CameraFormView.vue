<script setup>
import Dialog from "primevue/dialog";
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import {defineEmits, onMounted} from "vue";
import {userSettingsStore} from "@/store/userSettingsStore.js";
import Toast from "primevue/toast";
import {useToast} from "primevue/usetoast";
import {cameraFormStore} from "@/store/cameras/cameraFormStore.js";

// Store instances initialization
const cameraForm = cameraFormStore();
const userSettings = userSettingsStore()
const toast = useToast();

// Component mounted lifecycle hook
onMounted(async () => {
  const token = userSettings.getJwt.value;
  userSettings.setLoading(true);

  // If editing existing user, fetch their data
  if (!cameraForm.creatingCamera) {
    const cameraResponse = await cameraForm.fetchCameraData(token, cameraForm.groupId, cameraForm.id);
    console.log(cameraResponse);
    if (cameraResponse.status !== 200) {
      userSettings.setJwtKey(cameraResponse.token);
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: `${cameraResponse.status}: ${cameraResponse.message}`,
        life: 3000
      });
      userSettings.setLoading(false);
      await cameraForm.setVisible(false);
    }
    userSettings.setJwtKey(cameraResponse.token);
  }
  userSettings.setLoading(false);
})

// Close dialog handler
async function onClose() {
  cameraForm.clearData()
  await cameraForm.setVisible(false);
}

// Define component emits
const emit = defineEmits(["reload"])

// Form submission handler
async function onAccept() {
  userSettings.setLoading(true);
  const token = userSettings.getJwt.value;
  // Determine whether to create or update user
  const response = cameraForm.creatingCamera ? await cameraForm.createCameraRecord(token) : await cameraForm.updateCameraRecord(token);

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
  cameraForm.clearData()
  userSettings.setLoading(false);
  emit("reload");
  await cameraForm.setVisible(false);
}
</script>

<template>
  <Toast/>
  <!-- User form dialog -->
  <Dialog
      v-model:visible="cameraForm.visible"
      modal
      class="md:w-5 sm:w-8 w-11"
      :closable="false"
  >
    <template #header>
      <div>
        <span class="text-2xl">Camera form</span>
      </div>
    </template>

    <div class="flex flex-column gap-4">
      <div class="flex flex-column gap-2">
        <label for="username">Name</label>
        <InputText
            id="username"
            v-model="cameraForm.name"
            aria-describedby="username-help"
        />
        <small id="username-help">Enter camera name.</small>
      </div>
    </div>
    <div class="flex flex-column gap-4">
      <div class="flex flex-column gap-2">
        <label for="address">Address link</label>
        <InputText
            id="address"
            v-model="cameraForm.addressLink"
            aria-describedby="address-help"
        />
        <small id="address-help">Enter camera address link.</small>
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