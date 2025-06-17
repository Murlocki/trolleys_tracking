<script setup>
import {ref, onMounted} from "vue";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Button from "primevue/button";

import {usersStore} from "@/store/usersStore.js";
import {userSettingsStore} from "@/store/userSettingsStore.js";
import {getUsers, getUserSessionList} from "@/externalRequests/requests.js";
import router from "@/router/index.js";
import ErrorPage from "@/components/ErrorPage/ErrorPage.vue";
import SessionTable from "@/components/UserView/SessionTable.vue";

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
    expandedRows.value = { [rowId]: row };
    await onRowExpand(event);
  }
}

// Обработка открытия строки
const userId = ref(-1);
async function onRowExpand(event) {
  const user = event.data;
  await store.deleteUserSession()
  console.log(store.userSessions);
  userId.value = user.id;
  console.log(userId.value);
}



const error = ref(false)
const errorTitle = ref("ERROR")
const errorCode = ref(0)

onMounted(async () => {
  const token = userSettings.getJwt.value;
  userSettings.setLoading(true);
  error.value = false;
  const response = await getUsers(token);

  if (response.status === 401 || response.status === 403) {
    userSettings.clearJwt()
    await router.push("/")
    userSettings.setLoading(false);
    return;
  }


  const response_json = await response.json();
  if (response.status === 200) {
    await store.setUsers(response_json.data.items);
    await store.setPaginator(
        response_json.data.page,
        response_json.data.itemsPerPage,
        response_json.data.pageCount
    );
    userSettings.setJwtKey(response_json.token);
    userSettings.setLoading(false);
    return;
  }

  if (response.status === 0) {
    error.value = response.error;
    console.log(response.error);
    userSettings.setLoading(false);
    return;
  }

  const details = response_json.detail;
  userSettings.setJwtKey(details.token);
  error.value = true;
  errorCode.value = response.status;
  errorTitle.value = details.data.message;
  console.log(error.value);
  userSettings.setLoading(false);

});

function onPageChange(event) {
  store.setPaginator(event.first / event.rows, event.rows, event.pageCount);
}

function onDeleteUser(){}
function onEditUser(){}
function onLogOutUser(){}
function onAddUser(){}
function onSearch(){}

</script>

<template>
  <div class="w-full">
    <!-- Панель сверху: кнопка Добавить + поиск -->
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
        :rows="store.$state.pageSize"
        :totalRecords="store.pageSize * store.totalPages"
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
      <template #expansion="slotProps">
        <SessionTable
            :user-id="userId"
        />
      </template>

    </DataTable>
  </div>
</template>
