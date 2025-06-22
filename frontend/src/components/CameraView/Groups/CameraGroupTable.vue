<script setup>
import {onMounted, ref} from "vue";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import Image from "primevue/image";

import {groupsStore} from "@/store/groups/groupStore.js";
import {userSettingsStore} from "@/store/userSettingsStore.js";
import {getCameraGroupsList, getCamerasList,} from "@/externalRequests/requests.js";
import {camerasStore} from "@/store/cameras/cameraStore.js";
import {subscriptionStore} from "@/store/subscriptions/subscriptionStore.js";
import {testCart} from "@assets";
import ErrorPage from "@/components/ErrorPage/ErrorPage.vue";
import SubscriptionTable from "@/components/CameraView/Subscriptions/SubscriptionTable.vue";
import CameraTable from "@/components/CameraView/Cameras/CameraTable.vue";
import GroupTableSearchForm from "@/components/CameraView/Groups/GroupTableSearchForm.vue";
import {groupSearchFormStore} from "@/store/groups/groupSearchFormStore.js";
import GroupFormView from "@/components/CameraView/Groups/GroupFormView.vue";
import {groupFormStore} from "@/store/groups/groupFormStore.js";
import {useToast} from "primevue/usetoast";
import Toast from "primevue/toast";

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

const itemsPerPageOptions = [1, 10, 15, 20, 30];

const expandedRows = ref({}); // для управления раскрытием строк

// Toast notification setup
const toast = useToast();

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

async function loadGroups(){
  expandedRows.value = {};
  const token = userSettings.getJwt.token;
  userSettings.setLoading(true);
  const response = await store.fetchGroups(token);
  userSettings.setJwtKey(response.token);
  if (response.status !== 200) {
    error.value = true;
    errorCode.value = response.status;
    errorTitle.value = response.message;
  }
  userSettings.setLoading(false);
}

onMounted(async () => {
  await loadGroups();
});

async function onPageChange(event) {
  console.log(event);
  store.setPaginator(
      event.page,
      event.rows,
      event.pageCount);
  await loadGroups();
}

const camStore = camerasStore()

async function onRowExpand(event) {
  const group = event.data;
  await camStore.setGroupId(group.id);
}

function onRowCollapse(event) {
  const group = event.data
  console.log("Строка закрыта:", group.id);
  camStore.clearCameras()
}

const groupForm = groupFormStore()
async function onAddGroup(event) {
  groupForm.setCreatingGroup(true);
  groupForm.setVisible(true);

}

function onEditGroup(event) {
  groupForm.setGroupId(event.id);
  groupForm.setCreatingGroup(false);
  groupForm.setVisible(true);
}
const groupSearchForm = groupSearchFormStore()
function onGroupSearch(event) {
  groupSearchForm.setVisible(true)
}

async function onDeleteGroup(event) {
  userSettings.setLoading(true);
  const groupId = event.id;
  const token = userSettings.getJwt.value;
  const response = await store.deleteGroupById(token, groupId);
  userSettings.setJwtKey(response.token);
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
  await loadGroups();
}



</script>

<template>
  <div class="w-full">
    <Toast/>
    <!-- Панель сверху: кнопка Добавить + поиск -->
    <div class="flex flex-row justify-content-between mb-3">
      <Button label="Add" icon="pi pi-plus" @click="onAddGroup"/>
      <Button label="Search" severity="contrast" icon="pi pi-search" @click="onGroupSearch"/>
    </div>
    <GroupTableSearchForm v-if="groupSearchForm.visible" @reload="loadGroups"/>
    <GroupFormView v-if="groupForm.visible" @reload="loadGroups"/>
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
        <CameraTable />
      </template>
    </DataTable>
  </div>
</template>
