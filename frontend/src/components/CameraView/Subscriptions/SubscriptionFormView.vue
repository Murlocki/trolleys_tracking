<script setup>
import Dialog from "primevue/dialog";
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import Dropdown from "primevue/dropdown";
import Checkbox from "primevue/checkbox";
import Password from "primevue/password";
import {userFormStore} from "@/store/users/userFormStore.js";
import {onMounted, ref, defineEmits} from "vue";
import {getUserRoleList} from "@/externalRequests/requests.js";
import {userSettingsStore} from "@/store/userSettingsStore.js";
import {logOutUser} from "@/validators/validators.js";
import Toast from "primevue/toast";
import {useToast} from "primevue/usetoast";
import {subscriptionFormStore} from "@/store/subscriptions/subscriptionFormStore.js";

// Store instances initialization
const subscriptionForm = subscriptionFormStore();
const userSettings = userSettingsStore()
const roleOptions = ref([])
const toast = useToast();

// Component mounted lifecycle hook
onMounted(async () => {
  const token = userSettings.getJwt.value;
  userSettings.setLoading(true);

  // Fetch role list for dropdown
  const response = await subscriptionForm.fetchUsers(token);

  if (response.status === 401) {
    return;
  }

  // Handle API errors
  if (response.status !== 200) {
    userSettings.setJwtKey(response.token);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: `${response.status}: ${response.message}`,
      life: 3000
    });
    userSettings.setLoading(false);
    await subscriptionForm.setVisible(false);
  }
  userSettings.setJwtKey(response.token);
  userSettings.setLoading(false);
})

// Close dialog handler
async function onClose() {
  subscriptionForm.clearData()
  await subscriptionForm.setVisible(false);
}

// Define component emits
const emit = defineEmits(["reload"])

// Form submission handler
async function onAccept() {
  userSettings.setLoading(true);
  const token = userSettings.getJwt.value;

  // Determine whether to create or update user
  const response = await subscriptionForm.createSubscriptionRecord(token);
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
  emit("reload");
  await subscriptionForm.setVisible(false);
}
</script>

<template>
  <Toast/>
  <!-- User form dialog -->
  <Dialog
      v-model:visible="subscriptionForm.visible"
      modal
      class="md:w-5 sm:w-8 w-11"
      :closable="false"
  >
    <template #header>
      <div>
        <span class="text-2xl">User form</span>
      </div>
    </template>
    <!-- Role dropdown -->
    <div class="flex flex-column gap-2">
      <label for="user">User</label>
      <Dropdown
          id="user"
          v-model="subscriptionForm.userId"
          :options="subscriptionForm.usersOptions"
          optionValue="id"
          optionLabel="name"
          placeholder="Select a User"
          class="w-full md:w-14rem"
          aria-describedby="user-help"/>
      <small id="user-help">Select user.</small>
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