<script setup>

import Button from "primevue/button";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import {usersStore} from "@/store/usersStore.js";
import {userSettingsStore} from "@/store/userSettingsStore.js";
import {deleteUserSession, getUserSessionList} from "@/externalRequests/requests.js";
import router from "@/router/index.js";
import {onMounted, watch} from "vue";


const store = usersStore();
const columnsSession = [
  {field: "sessionId", header: "ID"},
  {field: "ipAddress", header: "IP-address"},
  {field: "device", header: "Device"},
  {field: "createdAt", header: "Created at"},
  {field: "expiresAt", header: "Updated at"},
];

const props = defineProps({
  userId: Number,
})


const settings = userSettingsStore();

async function setSessions() {
  const token = settings.getJwt.value;
  settings.setLoading(true);

  const response = await getUserSessionList(token, props.userId);
  if (response.status === 200) {
    const response_json = await response.json();
    settings.setJwtKey(response_json.token);
    await store.setUserSessions(response_json.data, props.userId);
  } else {
    console.error("Failed to fetch sessions:", response.statusText);
  }

  settings.setLoading(false);
}


watch(() => props.userId, async (newVal) => {
  if (newVal) {
    await setSessions();
  }
}, {immediate: true});

async function onDeleteSession(data) {
  settings.setLoading(true);
  console.log(data.sessionId);
  const response = await deleteUserSession(settings.getJwt.value, data.userId, data.sessionId);

  if (response.status === 401 || response.status === 403) {
    await settings.clearJwt()
    await router.push('/');
    console.log("Logged out")
    settings.setLoading(false);
    return
  }


  const response_json = await response.json();
  if (response.status === 200) {
    settings.setJwtKey(response_json.token)
    await setSessions()
    settings.setLoading(false);
    return;
  }
  settings.setJwtKey(response_json.token)
}

</script>

<template>
  <DataTable
      :value="store.userSessions || []"
      size="small"
      class="w-full nested-table"
      :scrollable="true"
      stripedRows

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