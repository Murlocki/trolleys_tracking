<script setup>

import Button from "primevue/button";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import {userSettingsStore} from "@/store/userSettingsStore.js";
import Toast from "primevue/toast";
import {ref, watch} from "vue";
import {sessionsStore} from "@/store/sessionsStore.js";
import ErrorPage from "@/components/ErrorPage/ErrorPage.vue";
import {useToast} from "primevue/usetoast";


const store = sessionsStore();
const columnsSession = [
  {field: "sessionId", header: "ID"},
  {field: "ipAddress", header: "IP-address"},
  {field: "device", header: "Device"},
  {field: "createdAt", header: "Created at"},
  {field: "expiresAt", header: "Updated at"},
];



const settings = userSettingsStore();
const error = ref(false)
const errorCode = ref(0)
const errorTitle = ref("")
async function setSessions(userId) {
  error.value = false;
  errorCode.value = 0;
  errorTitle.value = "";

  const token = settings.getJwt.value;
  settings.setLoading(true);

  await store.clearUserSessions()
  const response = await store.fetchSessions(token, userId);
  settings.setJwtKey(response.token);
  if (response.status !== 200) {
    error.value = true;
    errorCode.value = response.status;
    errorTitle.value = response.message;
  }
  settings.setLoading(false);
}


watch(() => store.$state.userId, async (newVal) => {
  if (newVal) {
    await setSessions(newVal);
  }
}, {immediate: true});


const toast = useToast();
async function onDeleteSession(data) {
  settings.setLoading(true);
  console.log(data.sessionId);
  const response = await store.deleteUserSessionById(settings.getJwt.value, data.userId, data.sessionId);
  console.log(response);
  settings.setJwtKey(response.token);
  if (response.status !== 200) {
    settings.setLoading(false);
    toast.add({ severity: 'error', summary: 'Error', detail: `${response.status}: ${response.message}`, life: 3000 });
    return;
  }
  await setSessions(data.userId);
}

</script>

<template>
  <Toast />
  <ErrorPage v-if="error" :error-code="errorCode" :error-text="errorTitle"/>
  <div class="w-full flex justify-content-center" v-else-if="store.sessions.length===0">
    <span class="text-2xl">No sessions</span>
  </div>
  <DataTable
      :value="store.sessions || []"
      size="small"
      class="w-full nested-table"
      :scrollable="true"
      stripedRows
      v-else
  >
    <Column
        v-for="col in columnsSession"
        :key="col.field"
        :field="col.field"
        :header="col.header"
    ></Column>
    <Column header="Actions" style="width: 140px">
      <template #body="slotProps">
        <div class="w-full flex justify-content-center align-content-center">
          <Button
              icon="pi pi-trash"
              class="p-button-rounded p-button-text p-button-danger"
              @click.stop="onDeleteSession(slotProps.data)"
              :aria-label="'Delete ' + slotProps.data.name"
          />
        </div>
      </template>
    </Column>
  </DataTable>
</template>

<style scoped>

</style>