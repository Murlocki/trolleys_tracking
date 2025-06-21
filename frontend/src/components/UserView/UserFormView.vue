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

// Store instances initialization
const userForm = userFormStore();
const userSettings = userSettingsStore()
const roleOptions = ref([])
const toast = useToast();

// Component mounted lifecycle hook
onMounted(async () => {
  const token = userSettings.getJwt.value;
  userSettings.setLoading(true);

  // Fetch role list for dropdown
  const response = await getUserRoleList(token)

  // Handle unauthorized access
  if (response.status === 401) {
    await logOutUser(response)
    return;
  }

  const responseJson = await response.json();

  // Handle API errors
  if (response.status !== 200) {
    userSettings.setJwtKey(response.status === 503 ? token : responseJson.token);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: `${response.status}: ${response.status === 503 ? responseJson.message : responseJson.detail.data.message}`,
      life: 3000
    });
    userSettings.setLoading(false);
    await userForm.setVisible(false);
  }

  // Set role options and default value
  roleOptions.value = responseJson.data;
  userForm.role = roleOptions.value[0].option
  userSettings.setJwtKey(responseJson.token);

  // If editing existing user, fetch their data
  if (!userForm.creatingUser) {
    const userResponse = await userForm.fetchUserData(responseJson.token, userForm.id);
    console.log(userResponse);
    if (userResponse.status !== 200) {
      userSettings.setJwtKey(userResponse.status === 503 ? token : userResponse.token);
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: `${userResponse.status}: ${userResponse.status === 503 ? userResponse.message : responseJson.detail.data.message}`,
        life: 3000
      });
      userSettings.setLoading(false);
      await userForm.setVisible(false);
    }
    userSettings.setJwtKey(userResponse.token);
  }

  userSettings.setLoading(false);
})

// Close dialog handler
async function onClose() {
  userForm.clearData()
  await userForm.setVisible(false);
}

// Define component emits
const emit = defineEmits(["reload"])

// Form submission handler
async function onAccept() {
  userSettings.setLoading(true);
  const token = userSettings.getJwt.value;

  // Determine whether to create or update user
  const response = userForm.creatingUser ? await userForm.createUserRecord(token) : await userForm.updateUserRecord(token);

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
  await userForm.setVisible(false);
}
</script>

<template>
  <Toast/>
  <!-- User form dialog -->
  <Dialog
      v-model:visible="userForm.visible"
      modal
      class="md:w-5 sm:w-8 w-11"
      :closable="false"
  >
    <template #header>
      <div>
        <span class="text-2xl">User form</span>
      </div>
    </template>

    <!-- Form fields -->
    <div class="flex flex-column gap-4">
      <!-- Username field -->
      <div class="flex flex-column gap-2">
        <label for="username">Username</label>
        <InputText
            id="username"
            v-model="userForm.username"
            aria-describedby="username-help"
        />
        <small id="username-help">Enter user username.</small>
      </div>

      <!-- Password field (only shown when creating user) -->
      <div class="flex flex-column gap-2" v-if="userForm.creatingUser">
        <label for="password">Password</label>
        <Password
            id="password"
            v-model="userForm.password"
            aria-describedby="password-help"
            toggleMask
        />
        <small id="password-help">Enter user password.</small>
      </div>

      <!-- Active checkbox (only shown when editing user) -->
      <div class="flex flex-column gap-2" v-if="!userForm.creatingUser">
        <label for="active">Account active</label>
        <Checkbox
            id="active"
            v-model="userForm.isActive"
            aria-describedby="active-help"
            :binary="true"
        />
        <small id="active-help">Set user activity.</small>
      </div>

      <!-- Role dropdown -->
      <div class="flex flex-column gap-2">
        <label for="role">Role</label>
        <Dropdown
            id="role"
            v-model="userForm.role"
            :options="roleOptions"
            optionValue="option"
            optionLabel="name"
            placeholder="Select a Role"
            class="w-full md:w-14rem"
            aria-describedby="role-help"/>
        <small id="role-help">Select user role.</small>
      </div>

      <!-- First name field -->
      <div class="flex flex-column gap-2">
        <label for="firstName">First name</label>
        <InputText
            id="firstName"
            v-model="userForm.firstName"
            aria-describedby="firstName-help"
            :disabled="userForm.role === 'service'"
        />
        <small id="firstName-help">Enter user first name.</small>
      </div>

      <!-- Last name field -->
      <div class="flex flex-column gap-2">
        <label for="lastName">Last name</label>
        <InputText
            id="lastName"
            v-model="userForm.lastName"
            aria-describedby="lastName-help"
            :disabled="userForm.role === 'service'"
        />
        <small id="lastName-help">Enter user last name.</small>
      </div>

      <!-- Email field -->
      <div class="flex flex-column gap-2">
        <label for="email">Email</label>
        <InputText
            id="email"
            v-model="userForm.email"
            aria-describedby="email-help"
            :disabled="userForm.role === 'service'"
        />
        <small id="email-help">Enter user email.</small>
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