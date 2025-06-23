<script setup>
import Dialog from "primevue/dialog";
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import {defineEmits, onMounted} from "vue";
import {userSettingsStore} from "@/store/userSettingsStore.js";
import Toast from "primevue/toast";
import {useToast} from "primevue/usetoast";
import {groupFormStore} from "@/store/groups/groupFormStore.js";

// Store instances initialization
const groupForm = groupFormStore();
const userSettings = userSettingsStore()
const toast = useToast();

// Component mounted lifecycle hook
onMounted(async () => {
  const token = userSettings.getJwt.value;
  userSettings.setLoading(true);


  // If editing existing user, fetch their data
  if (!groupForm.creatingGroup) {
    const groupResponse = await groupForm.fetchGroupData(token, groupForm.id);
    console.log(groupResponse);
    if (groupResponse.status !== 200) {
      userSettings.setJwtKey(groupResponse.token);
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: `${groupResponse.status}: ${groupResponse.message}`,
        life: 3000
      });
      userSettings.setLoading(false);
      await groupForm.setVisible(false);
    }
    userSettings.setJwtKey(groupResponse.token);
  }

  userSettings.setLoading(false);
})

// Close dialog handler
async function onClose() {
  groupForm.clearData()
  await groupForm.setVisible(false);
}

// Define component emits
const emit = defineEmits(["reload"])

// Form submission handler
async function onAccept() {
  userSettings.setLoading(true);
  const token = userSettings.getJwt.value;

  // Determine whether to create or update user
  const response = groupForm.creatingGroup ? await groupForm.createGroupRecord(token) : await groupForm.updateGroupRecord(token);

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
  groupForm.clearData()
  userSettings.setLoading(false);
  emit("reload");
  await groupForm.setVisible(false);
}
</script>

<template>
  <Toast/>
  <!-- User form dialog -->
  <Dialog
      v-model:visible="groupForm.visible"
      modal
      class="md:w-5 sm:w-8 w-11"
      :closable="false"
  >
    <template #header>
      <div>
        <span class="text-2xl">Group form</span>
      </div>
    </template>

    <!-- Form fields -->
    <div class="flex flex-column gap-4">
      <div class="flex flex-column gap-2">
        <label for="username">Name</label>
        <InputText
            id="name"
            v-model="groupForm.name"
            aria-describedby="name-help"
        />
        <small id="name-help">Enter group name.</small>
      </div>

      <div class="flex flex-column gap-2">
        <label for="address">Address</label>
        <InputText
            id="address"
            v-model="groupForm.address"
            aria-describedby="address-help"
        />
        <small id="address-help">Enter group address.</small>
      </div>

      <div class="flex flex-column gap-2">
        <label for="description">Description</label>
        <InputText
            id="description"
            v-model="groupForm.description"
            aria-describedby="description-help"
        />
        <small id="description-help">Enter group description.</small>
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