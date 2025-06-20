<script setup>
import Dialog from "primevue/dialog";
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import Dropdown from "primevue/dropdown";
import Checkbox from "primevue/checkbox";
import Password from "primevue/password";
import {userFormStore} from "@/store/userFormStore.js";
import {onMounted, ref, defineEmits} from "vue";
import {getUserRoleList} from "@/externalRequests/requests.js";
import {userSettingsStore} from "@/store/userSettingsStore.js";
import {logOutUser} from "@/validators/validators.js";
import Toast from "primevue/toast";
import {useToast} from "primevue/usetoast";


const userForm = userFormStore();
const userSettings = userSettingsStore()
const roleOptions = ref([])
const toast = useToast();
onMounted(async () => {
  const token = userSettings.getJwt.value;
  userSettings.setLoading(true);
  const response = await getUserRoleList(token)
  if (response.status === 401) {
    await logOutUser(response)
    return;
  }
  const responseJson = await response.json();
  if (response.status === 200) {
    roleOptions.value = responseJson.data;
    userForm.role = roleOptions.value[0].option
    userSettings.setJwtKey(responseJson.token);
    userSettings.setLoading(false);
    return;
  }
  userSettings.setJwtKey(response.status === 503 ? token : responseJson.token);
  toast.add({
    severity: 'error',
    summary: 'Error',
    detail: `${response.status}: ${response.status === 503 ? responseJson.message : responseJson.detail.data.message}`,
    life: 3000
  });
  userSettings.setLoading(false);
  await userForm.setVisible(false);
})

async function onClose() {
  userForm.clearData()
  await userForm.setVisible(false);
}
const emit = defineEmits(["reload"])

async function onAccept() {
  userSettings.setLoading(true);
  const token = userSettings.getJwt.value;
  const response = await userForm.createUserRecord(token);
  if (response.status !== 201) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: `${response.status}: ${response.message}`,
      life: 3000
    });
    userSettings.setLoading(false);
    return;
  }
  userSettings.setLoading(false);
  emit("reload");
  await userForm.setVisible(false);

}

</script>

<template>
  <Toast/>
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
    <div class="flex flex-column gap-4">
      <div class="flex flex-column gap-2">
        <label for="username">Username</label>
        <InputText
            id="username"
            v-model="userForm.username"
            aria-describedby="username-help"
        />
        <small id="username-help">Enter user username.</small>
      </div>
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

    <template #footer>
      <div class="w-full flex flex-row justify-content-between align-items-center">
        <Button label="Accept" size="large" @click="onAccept"/>
        <Button label="Close" class="bg-primary-reverse" size="large" @click="onClose"/>
      </div>
    </template>
  </Dialog>
</template>

<style scoped>

</style>