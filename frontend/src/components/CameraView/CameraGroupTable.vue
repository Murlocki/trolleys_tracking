<script setup>
import {ref, onMounted} from "vue";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import Image from "primevue/image";

import {groupsStore} from "@/store/cameras/groupStore.js";
import {userSettingsStore} from "@/store/userSettingsStore.js";
import {
  getCameraGroupsList,
  getCamerasList,
  getCameraSubscribersList,
} from "@/externalRequests/requests.js";
import {camerasStore} from "@/store/cameras/cameraStore.js";
import {subscriptionStore} from "@/store/cameras/subscriptionStore.js";
import {imagePath, testCart} from "@assets";
import ErrorPage from "@/components/ErrorPage/ErrorPage.vue";
import SubscriptionTable from "@/components/CameraView/SubscriptionTable.vue";

const store = groupsStore();
const userSettings = userSettingsStore();

const columns = [
  {field: "id", header: "ID"},
  {field: "name", header: "Name"},
  {field: "address", header: "Address"},
  {field: "description", header: "Description"},
  {field: "createdAt", header: "Created at"},
  {field: "updatedAt", header: "Updated at"},
];

const itemsPerPageOptions = [10, 15, 20, 30];

const expandedRows = ref({}); // для управления раскрытием строк

async function onRowClick(event) {
  const row = event.data;
  const rowId = row.id;

  if (expandedRows.value[rowId]) {
    expandedRows.value = {};
    await onRowCollapse(event);
  } else {
    expandedRows.value = {[rowId]: row};
    await onRowExpand(event);
  }
}

const error = ref(false)
const errorTitle = ref("ERROR")
const errorCode = ref(0)


onMounted(async () => {
  const token = userSettings.getJwt.value;
  userSettings.setLoading(true);

  const response = await getCameraGroupsList(token);
  if (response.status === 200) {
    const response_json = await response.json();
    userSettings.setJwtKey(response_json.token);
    await store.setGroups(response_json.data.items);
    await store.setPaginator(
        response_json.data.page,
        response_json.data.itemsPerPage,
        response_json.data.pageCount
    );
  } else {
    console.log("Failed to fetch groups:", response.statusText);
  }
  userSettings.setLoading(false);
});

function onPageChange(event) {
  store.setPaginator(event.first / event.rows, event.rows, event.pageCount);
}

const camStore = camerasStore()

async function onRowExpand(event) {
  const group = event.data;
  console.log(camStore.cameras);
  const token = userSettings.getJwt.value;
  userSettings.setLoading(true);

  const response = await getCamerasList(token, group.id);
  if (response.status === 200) {
    const response_json = await response.json();
    console.log(response_json)
    userSettings.setJwtKey(response_json.token);
    if (response_json.data.items.length > 0) {
      await camStore.setCameras(response_json.data.items);
    }
  } else {
    console.error("Failed to fetch sessions:", response.statusText);
  }

  userSettings.setLoading(false);
}

function onRowCollapse(event) {
  const group = event.data
  console.log("Строка закрыта:", group.id);
  camStore.clearCameras()
}

function onAddGroup(event) {
}

function onEditGroup(event) {
}

function onGroupSearch(event) {
}

function onDeleteGroup(event) {
}

// Функции для обработки событий КАМЕР
const columnsCameras = [
  {field: "id", header: "ID"},
  {field: "name", header: "Name"},
  {field: "addressLink", header: "addressLink"},
  {field: "createdAt", header: "Created at"},
  {field: "updatedAt", header: "Updated at"},
];
const cameraExpandedRows = ref({});


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

function onAddCamera(evenent) {
}

function onEditCamera(event) {
}

function onDeleteCamera(event) {
}

function onCameraSearch(event) {
}

function onPageCameraChange(event) {
}

const subStore = subscriptionStore()

async function onCameraRowExpand(event) {
  const camera = event.data;
  subStore.setCamera(camera);
}

async function onCameraRowCollapse(event) {
  const camera = event.data
  console.log("Строка закрыта:", camera.id);
  subStore.clearSubscriptions()
}

// Функции для обработки событий ПОДПИСОК
const columnsSubscriptions = [
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

function onPageSubscriptionChange(event) {
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
  <div class="w-full">
    <!-- Панель сверху: кнопка Добавить + поиск -->
    <div class="flex flex-row justify-content-between mb-3">
      <Button label="Add" icon="pi pi-plus" @click="onAddGroup"/>
      <Button label="Search" severity="contrast" icon="pi pi-search" @input="onGroupSearch"/>
    </div>

    <ErrorPage v-if="error" :error-code="errorCode" :error-text="errorTitle"/>
    <DataTable
        v-else
        :value="store.groups"
        tableStyle="min-width: 50rem"
        size="large"
        :scrollable="true"
        stripedRows
        class="w-full mt-4"
        :paginator="true"
        :rows="store.pageSize"
        :totalRecords="store.totalRecords"
        :lazy="true"
        @page="onPageChange"
        :rowsPerPageOptions="itemsPerPageOptions"
        :showCurrentPageReport="true"

        dataKey="id"
        :expandedRows="expandedRows"
        @row-click="onRowClick"
        rowExpansion
    >
      <!-- Колонка для раскрытия -->
      <Column
          expander
          style="width: 3em"
      ></Column>

      <!-- Колонки из вашего массива -->
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
                @click.stop="onEditGroup(slotProps.data)"
                :aria-label="'Edit ' + slotProps.data.name"
            />
            <Button
                icon="pi pi-trash"
                class="p-button-rounded p-button-text p-button-danger"
                @click.stop="onDeleteGroup(slotProps.data)"
                :aria-label="'Delete ' + slotProps.data.name"
            />
          </div>
        </template>
      </Column>


      <template #expansion="slotProps">
        <div>
          <h3 class="text-2xl mb-3">Cameras for group: {{ slotProps.data.name }}</h3>
        </div>
        <div class="w-full flex justify-content-center" v-if="camStore.cameras.length===0">
          <span class="text-2xl">No cameras</span>
        </div>
        <div v-else>
          <div class="flex flex-row justify-content-between mb-3">
            <Button label="Add" icon="pi pi-plus" @click="onAddCamera"/>
            <Button label="Search" severity="contrast" icon="pi pi-search" @input="onCameraSearch"/>
          </div>
          <DataTable
              :value="camStore.cameras || []"
              size="small"
              class="w-full nested-table"
              :scrollable="true"
              stripedRows
              :paginator="true"
              :rows="camStore.pageSize"
              :totalRecords="camStore.pageSize * camStore.totalPages"
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
                v-for="col in columnsCameras"
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
              <SubscriptionTable />
            </template>
          </DataTable>
        </div>
      </template>
    </DataTable>
  </div>
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


</template>
