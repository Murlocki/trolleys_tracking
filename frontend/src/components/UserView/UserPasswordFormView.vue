<script setup>
import Dialog from "primevue/dialog";
import Button from "primevue/button";
import Password from "primevue/password";
import {onMounted, defineEmits} from "vue";
import {userSettingsStore} from "@/store/userSettingsStore.js";
import Toast from "primevue/toast";
import {useToast} from "primevue/usetoast";
import {userPasswordFormStore} from "@/store/users/userPasswordFormStore.js";


const userPasswordForm = userPasswordFormStore();
const userSettings = userSettingsStore()
const toast = useToast();
onMounted(async () => {
  userSettings.setLoading(true);
  const token = userSettings.getJwt.value;

  const userResponse = await userPasswordForm.fetchUserData(token, userPasswordForm.id);
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
    await userPasswordForm.setVisible(false);
  }
  userSettings.setJwtKey(userResponse.token);
  userSettings.setLoading(false);
})

async function onClose() {
  userPasswordForm.clearData()
  await userPasswordForm.setVisible(false);
}

const emit = defineEmits(["reload"])

async function onAccept() {
  userSettings.setLoading(true);
  const token = userSettings.getJwt.value;

  const response = await userPasswordForm.updateUserPassword(token);

  if (response.status !== 200) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: `${response.status}: ${response.message}`,
      life: 3000
    });
    userSettings.setLoading(false);
    return;
  }
  userSettings.setJwtKey(response.token);
  userSettings.setLoading(false);
  emit("reload");
  await userPasswordForm.setVisible(false);
}

</script>

<template>
  <Toast/>
  <Dialog
      v-model:visible="userPasswordForm.visible"
      modal
      class="md:w-5 sm:w-8 w-11"
      :closable="false"
  >
    <template #header>
      <div>
        <span class="text-2xl">User password form</span>
      </div>
    </template>
    <div class="flex flex-column">
      <div class="flex flex-column gap-2">
        <label for="password">Password</label>
        <Password
            id="password"
            v-model="userPasswordForm.password"
            aria-describedby="password-help"
            toggleMask
        />
        <small id="password-help">Enter user password.</small>
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