<script setup>
import Dialog from "primevue/dialog";
import Button from "primevue/button";
import Password from "primevue/password";
import {onMounted, defineEmits} from "vue";
import {userSettingsStore} from "@/store/userSettingsStore.js";
import Toast from "primevue/toast";
import {useToast} from "primevue/usetoast";
import {userPasswordFormStore} from "@/store/users/userPasswordFormStore.js";

// Initialize Pinia stores
const userPasswordForm = userPasswordFormStore(); // Password form state
const userSettings = userSettingsStore(); // User settings store
const toast = useToast(); // Toast notification service

/**
 * Component mounted lifecycle hook
 * Loads user data when form becomes visible
 */
onMounted(async () => {
  userSettings.setLoading(true);
  const token = userSettings.getJwt.value;

  // Fetch user data for password form
  const userResponse = await userPasswordForm.fetchUserData(token, userPasswordForm.id);

  // Handle API errors
  if (userResponse.status !== 200) {
    userSettings.setJwtKey(userResponse.status === 503 ? token : userResponse.token);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: `${userResponse.status}: ${userResponse.status === 503 ?
          userResponse.message :
          userResponse.detail?.data?.message || 'Unknown error'}`,
      life: 3000
    });
    userSettings.setLoading(false);
    await userPasswordForm.setVisible(false);
    return;
  }

  // Update token and finish loading
  userSettings.setJwtKey(userResponse.token);
  userSettings.setLoading(false);
});

/**
 * Closes the password form and clears form data
 */
async function onClose() {
  userPasswordForm.clearData();
  await userPasswordForm.setVisible(false);
}

// Define component events
const emit = defineEmits(["reload"]);

/**
 * Handles password form submission
 * Updates user password and closes the form on success
 */
async function onAccept() {
  userSettings.setLoading(true);
  const token = userSettings.getJwt.value;

  // Send password update request
  const response = await userPasswordForm.updateUserPassword(token);

  // Handle errors
  if (response.status !== 200) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: `${response.status}: ${response.message}`,
      life: 3000
    });
    userSettings.setLoading(false);
    userPasswordForm.clearData();
    return;
  }

  // Success case
  userSettings.setJwtKey(response.token);
  userSettings.setLoading(false);
  userPasswordForm.clearData();
  emit("reload"); // Notify parent to refresh data
  await userPasswordForm.setVisible(false); // Close form
}
</script>

<template>
  <!-- Toast notification container -->
  <Toast/>

  <!-- Password Form Dialog -->
  <Dialog
      v-model:visible="userPasswordForm.visible"
      modal
      class="md:w-5 sm:w-8 w-11"
      :closable="false"
  >
    <!-- Dialog Header -->
    <template #header>
      <div>
        <span class="text-2xl">User password form</span>
      </div>
    </template>

    <!-- Form Content -->
    <div class="flex flex-column">
      <div class="flex flex-column gap-2">
        <label for="password">Password</label>
        <!-- Password input with toggle mask -->
        <Password
            id="password"
            v-model="userPasswordForm.password"
            aria-describedby="password-help"
            toggleMask
        />
        <small id="password-help">Enter new user password.</small>
      </div>
    </div>

    <!-- Dialog Footer with Action Buttons -->
    <template #footer>
      <div class="w-full flex flex-row justify-content-between align-items-center">
        <!-- Submit button -->
        <Button
            label="Accept"
            size="large"
            @click="onAccept"
        />
        <!-- Cancel button -->
        <Button
            label="Close"
            class="bg-primary-reverse"
            size="large"
            @click="onClose"
        />
      </div>
    </template>
  </Dialog>
</template>

<style scoped>
</style>