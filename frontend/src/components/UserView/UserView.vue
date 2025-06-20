<script setup>
import {ref, onMounted} from "vue";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Button from "primevue/button";

import {usersStore} from "@/store/usersStore.js";
import {userSettingsStore} from "@/store/userSettingsStore.js";
import ErrorPage from "@/components/ErrorPage/ErrorPage.vue";
import SessionTable from "@/components/UserView/SessionTable.vue";
import {sessionsStore} from "@/store/sessionsStore.js";
import {deleteUserSessionList} from "@/externalRequests/requests.js";
import {logOutUser} from "@/validators/validators.js";
import Toast from "primevue/toast";
import {useToast} from "primevue/usetoast";
import {userFormStore} from "@/store/userFormStore.js";
import UserFormView from "@/components/UserView/UserFormView.vue";

const store = usersStore();
const userSettings = userSettingsStore();

const columns = [
  {field: "id", header: "ID"},
  {field: "username", header: "User Name"},
  {field: "roleDisplay", header: "Role"},
  {field: "isActive", header: "Is active"},
  {field: "email", header: "Email"},
  {field: "firstName", header: "First name"},
  {field: "lastName", header: "Last name"},
  {field: "createdAt", header: "Created at"},
  {field: "updatedAt", header: "Updated at"},
];

const itemsPerPageOptions = [10, 15, 20, 30];

const expandedRows = ref({}); // для управления раскрытием строк

// Обработка клика по строке
async function onRowClick(event) {
  const row = event.data;
  const rowId = row.id;

  if (expandedRows.value[rowId]) {
    expandedRows.value = {};
  } else {
    expandedRows.value = {[rowId]: row};
    await onRowExpand(event);
  }
}

// Обработка открытия строки
const sessions = sessionsStore()

async function onRowExpand(event) {
  const user = event.data;
  await sessions.setUserId(user.id);
}


const error = ref(false)
const errorTitle = ref("ERROR")
const errorCode = ref(0)


async function loadUsers() {
  const token = userSettings.getJwt.value;
  userSettings.setLoading(true);
  const response = await store.fetchUsers(token);
  userSettings.setJwtKey(response.token);
  if (response.status !== 200) {
    error.value = true;
    errorCode.value = response.status;
    errorTitle.value = response.message;
  }
  userSettings.setLoading(false);
}

onMounted(async () => {
  await loadUsers();
});


async function onPageChange(event) {
  store.setPaginator(event.page, event.rows, event.pageCount);
  expandedRows.value = {};
  await loadUsers();
}

async function onDeleteUser(event) {
  userSettings.setLoading(true);
  const userId = event.id;
  const response = await store.deleteUserRecordById(userId);
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
  await loadUsers();

}

function onEditUser() {
}

const toast = useToast();

async function onLogOutUser(event) {
  const token = userSettings.getJwt.value;
  userSettings.setLoading(true);
  const userId = event.id;
  const response = await deleteUserSessionList(token, userId);
  if (response.status === 401) {
    await logOutUser(response);
    return;
  }
  const responseJson = await response.json();
  userSettings.setJwtKey(responseJson.token);
  if (response.status !== 200) {
    userSettings.setLoading(false);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: `${responseJson.status}: ${responseJson.message}`,
      life: 3000
    });
    return;
  }
  if (sessions.userId === userId) {
    sessions.userId = null;
    await sessions.clearUserSessions()
    sessions.userId = userId;
    return;
  }
  userSettings.setLoading(false);
  return;
}

const userForm = userFormStore();
function onAddUser() {
  userForm.setCreatingUser(true);
  userForm.setVisible(true);

  console.log(userForm.visible);
}

function onSearch() {
}

</script>

<template>
  <div class="w-full">
    <Toast/>
    <UserFormView v-if="userForm.visible" @reload="loadUsers"/>
    <div class="flex flex-row justify-content-between mb-3">
      <Button label="Add" icon="pi pi-plus" @click="onAddUser"/>
      <Button label="Search" severity="contrast" icon="pi pi-search" @input="onSearch"/>
    </div>
    <ErrorPage v-if="error" :error-code="errorCode" :error-text="errorTitle"/>
    <DataTable
        v-else
        :value="store.$state.users"
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
                @click.stop="onEditUser(slotProps.data)"
                :aria-label="'Edit ' + slotProps.data.name"
            />
            <Button
                icon="pi pi-trash"
                class="p-button-rounded p-button-text p-button-danger"
                @click.stop="onDeleteUser(slotProps.data)"
                :aria-label="'Delete ' + slotProps.data.name"
            />
            <Button
                icon="pi pi-sign-out"
                class="p-button-rounded p-button-text p-button-danger"
                @click.stop="onLogOutUser(slotProps.data)"
                :aria-label="'Logout ' + slotProps.data.name"
            />
          </div>
        </template>
      </Column>

      <!-- Раскрывающаяся таблица с сессиями -->
      <template #expansion>
        <SessionTable
        />
      </template>

    </DataTable>
  </div>
</template>
