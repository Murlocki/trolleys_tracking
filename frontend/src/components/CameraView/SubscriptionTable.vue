<script setup>
import {ref, watch} from "vue";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Button from "primevue/button";
import {userSettingsStore} from "@/store/userSettingsStore.js";
import {subscriptionStore} from "@/store/cameras/subscriptionStore.js";
import ErrorPage from "@/components/ErrorPage/ErrorPage.vue";

const settings = userSettingsStore();

const itemsPerPageOptions = [1, 10, 15, 20, 30];

const store = subscriptionStore()
const error = ref(false)
const errorTitle = ref("ERROR")
const errorCode = ref(0)

async function setSubscriptions(groupId, cameraId) {
  error.value = false;
  errorCode.value = 0;
  errorTitle.value = "";

  const token = settings.getJwt.value;
  settings.setLoading(true);

  const response = await store.fetchSubscriptions(token, groupId, cameraId);
  settings.setJwtKey(response.token);

  // Обработка ошибок
  if (response.status !== 200) {
    error.value = true;
    errorCode.value = response.status;
    errorTitle.value = response.message;
  }

  settings.setLoading(false);
}

/**
 * Отслеживаем изменение ID пользователя для автоматической загрузки сессий
 */
watch(() => store.$state.cameraId, async (newVal) => {
  if (newVal) {
    await setSubscriptions(store.$state.groupId, newVal);
  }
}, {immediate: true});

// Функции для обработки событий ПОДПИСОК
const columns = [
  {field: "id", header: "ID"},
  {field: "cameraName", header: "Camera Name"},
  {field: "userName", header: "User name"},
  {field: "createdAt", header: "Created at"},
  {field: "updatedAt", header: "Updated at"},
];

function onAddSubscription(event) {
}

function onEditSubscription(event) {
}

function onDeleteSubscription(event) {
}

function onSubscriptionSearch(event) {
}

async function onPageSubscriptionChange(event) {
  console.log(event);
  store.setPaginator(event.page, event.rows, event.pageCount);
  await setSubscriptions(store.groupId, store.cameraId);
}

</script>

<template>
  <div class="flex flex-row justify-content-between mb-3">
    <Button label="Add" icon="pi pi-plus" @click="onAddSubscription"/>
    <Button label="Search" severity="contrast" icon="pi pi-search" @click="onSubscriptionSearch"/>
  </div>
  <ErrorPage v-if="error" :error-code="errorCode" :error-text="errorTitle"/>
  <div class="w-full flex justify-content-center" v-else-if="store.subscriptions.length===0">
    <span class="text-2xl">No subscribers</span>
  </div>
  <DataTable
      v-else
      :value="store.subscriptions || []"
      size="small"
      class="w-full nested-table"
      :scrollable="true"
      stripedRows
      :lazy="true"
      dataKey="id"
      :paginator="true"
      :rows="store.pageSize"
      :totalRecords="store.totalRecords"
      @page="onPageSubscriptionChange"
      :rowsPerPageOptions="itemsPerPageOptions"
      :showCurrentPageReport="true"
  >
    <Column
        v-for="col in columns"
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
              @click.stop="onDeleteSubscription(slotProps.data)"
              :aria-label="'Delete ' + slotProps.data.name"
          />
          <Button
              icon="pi pi-edit"
              class="p-button-rounded p-button-text p-button-danger"
              @click.stop="onEditSubscription(slotProps.data)"
              :aria-label="'Edit ' + slotProps.data.name"
          />
        </div>
      </template>
    </Column>
  </DataTable>
</template>