<script setup>
import {ref, watch} from "vue";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Button from "primevue/button";
import {userSettingsStore} from "@/store/userSettingsStore.js";
import {subscriptionStore} from "@/store/subscriptions/subscriptionStore.js";
import ErrorPage from "@/components/ErrorPage/ErrorPage.vue";
import {subscriptionFormStore} from "@/store/subscriptions/subscriptionFormStore.js";
import SubscriptionFormView from "@/components/CameraView/Subscriptions/SubscriptionFormView.vue";
import {subscriptionSearchFormStore} from "@/store/subscriptions/subscriptionSearchFormStore.js";
import SubscriptionTableSearchForm from "@/components/CameraView/Subscriptions/SubscriptionTableSearchForm.vue";
import SubscriptionTable from "@/components/CameraView/Subscriptions/SubscriptionTable.vue";
import {camerasStore} from "@/store/cameras/cameraStore.js";
import {testCart} from "@assets";
import Dialog from "primevue/dialog";
import Image from "primevue/image";
import CameraTableSearchForm from "@/components/CameraView/Cameras/CameraTableSearchForm.vue";
import {cameraSearchFormStore} from "@/store/cameras/cameraSearchFormStore.js";

const settings = userSettingsStore();

const itemsPerPageOptions = [1, 10, 15, 20, 30];

const store = camerasStore();
const error = ref(false)
const errorTitle = ref("ERROR")
const errorCode = ref(0)

const cameraExpandedRows = ref({});
async function setCameras(groupId) {
  error.value = false;
  errorCode.value = 0;
  errorTitle.value = "";

  const token = settings.getJwt.value;
  settings.setLoading(true);

  const response = await store.fetchCameras(token, groupId);
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
watch(() => store.$state.groupId, async (newVal) => {
  if (newVal) {
    await setCameras(newVal);
  }
}, {immediate: true});

// Функции для обработки событий ПОДПИСОК
const columns = [
  {field: "id", header: "ID"},
  {field: "name", header: "Name"},
  {field: "addressLink", header: "addressLink"},
  {field: "createdAt", header: "Created at"},
  {field: "updatedAt", header: "Updated at"},
];

const subscriptionForm = subscriptionFormStore();
function onAddCamera(event) {
  subscriptionForm.setVisible(true);
  subscriptionForm.setCamera(store.cameraId, store.groupId)
}

async function onDeleteCamera(event) {
  settings.setLoading(true);
  // Отправляем запрос на удаление сессии
  const response = await store.deleteCameraById(
      settings.getJwt.value,
      event.id
  );

  settings.setJwtKey(response.token);

  // Обработка ошибок
  if (response.status !== 200) {
    settings.setLoading(false);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: `${response.status}: ${response.message}`,
      life: 3000
    });
    return;
  }

  // Обновляем список камер после удаления
  await setCameras(store.groupId);
}

const cameraSearchForm = cameraSearchFormStore();
function onCameraSearch(event) {
  cameraSearchForm.setVisible(true);
}

function onEditCamera(event) {

}

async function onPageCameraChange(event) {
  store.setPaginator(event.page, event.rows, event.pageCount);
  await setCameras(store.groupId);
}


async function onCameraRowClick(event) {
  const row = event.data;
  const rowId = row.id;

  if (cameraExpandedRows.value[rowId]) {
    cameraExpandedRows.value = {};
    await onCameraRowCollapse(event);
  } else {
    cameraExpandedRows.value = {[rowId]: row};
    await onCameraRowExpand(event);
  }
}


const subStore = subscriptionStore()

async function onCameraRowExpand(event) {
  const camera = event.data;
  subStore.setCamera(camera);
}

async function onCameraRowCollapse(event) {
  settings.setLoading(true);
  const camera = event.data
  console.log("Строка закрыта:", camera.id);
  subStore.clearSubscriptions()
  settings.setLoading(false);
}

function onCameraStart(event) {

}

const openCameraWatch = ref(false);

function onCameraWatch(event) {
  openCameraWatch.value = true;
}

function onCameraStatusUpdate(event) {

}

</script>

<template>
  <div>
    <SubscriptionFormView
        v-if="subscriptionForm.visible"
        @reload="setCameras(store.groupId)"
    />
    <CameraTableSearchForm
        v-if="cameraSearchForm.visible"
        @reload="setCameras(store.groupId)"
    />
    <div class="flex flex-row justify-content-between mb-3">
      <Button label="Add" icon="pi pi-plus" @click="onAddCamera"/>
      <Button label="Search" severity="contrast" icon="pi pi-search" @click="onCameraSearch"/>
    </div>
    <ErrorPage v-if="error" :error-code="errorCode" :error-text="errorTitle"/>
    <div class="w-full flex justify-content-center" v-else-if="store.cameras.length===0">
      <span class="text-2xl">No cameras</span>
    </div>
    <DataTable
        :value="store.cameras || []"
        size="small"
        class="w-full nested-table"
        :scrollable="true"
        stripedRows
        :paginator="true"
        :rows="store.pageSize"
        :totalRecords="store.totalRecords"
        :lazy="true"
        @page="onPageCameraChange"
        :rowsPerPageOptions="itemsPerPageOptions"
        :showCurrentPageReport="true"

        dataKey="id"
        :expandedRows="cameraExpandedRows"
        @row-click="onCameraRowClick"
        rowExpansion
    >
      <Column
          expander
          style="width: 3em"
      ></Column>
      <Column
          v-for="col in columns"
          :key="col.field"
          :field="col.field"
          :header="col.header"
      ></Column>
      <Column header="Actions" style="width: 140px">
        <template #body="slotProps">
          <div class="flex flex-row">
            <Button
                icon="pi pi-pencil"
                class="p-button-rounded p-button-text p-button-info"
                @click.stop="onEditCamera(slotProps.data)"
                :aria-label="'Edit ' + slotProps.data.name"
            />
            <Button
                icon="pi pi-trash"
                class="p-button-rounded p-button-text p-button-danger"
                @click.stop="onDeleteCamera(slotProps.data)"
                :aria-label="'Delete ' + slotProps.data.name"
            />
          </div>
        </template>
      </Column>
      <template #expansion="slotProps">
        <div class="flex w-full flex-column align-items-start">
          <div>
            <h3 class="text-2xl mb-3">Control camera</h3>
          </div>
          <div class="flex gap-4">
            <Button label="Start" severity="contrast" icon="pi pi-circle-off" @click="onCameraStart"/>
            <Button label="Watch" severity="contrast" icon="pi pi-eye" @click="onCameraWatch"/>
            <Button label="Status Update" severity="contrast" icon="pi pi-sync" @click="onCameraStatusUpdate"/>
          </div>
        </div>
        <div>
          <h3 class="text-2xl mb-3">Subscribers for camera: {{ slotProps.data.name }}</h3>
        </div>
        <SubscriptionTable/>
      </template>
    </DataTable>
    <Dialog
        v-model:visible="openCameraWatch"
        modal
        :show-header="false"
        class="md:w-8 sm:w-10 w-full pt-4 px-4"
        contentStyle="padding: 0"
    >
      <!-- Контейнер с изображением, занимает всё доступное пространство -->
      <div class="flex-grow-1 w-full h-full relative overflow-hidden">
        <div class="w-full">
          <span class="text-3xl font-bold">Camera watching</span>
        </div>
        <Image :src="testCart" :preview="false" containerClass="w-full h-full">
          <template #image>
            <img
                :src="testCart"
                alt="Camera View"
                class="w-full h-full"
                style="object-fit: fill;"
            />
          </template>
        </Image>
      </div>

      <template #footer>
        <div
            class="flex flex-row justify-content-center align-items-center p-2 border-top-1 surface-border bg-white w-full"
            style="min-height: auto;">
          <Button
              label="Close"
              icon="pi pi-times"
              class="p-button-danger py-4 px-6"
              @click="openCameraWatch = false"

          />
        </div>
      </template>
    </Dialog>
  </div>
</template>