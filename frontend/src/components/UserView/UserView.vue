<script setup>
import {ref, onMounted} from "vue";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Button from "primevue/button";
import {usersStore} from "@/store/users/usersStore.js";
import {userSettingsStore} from "@/store/userSettingsStore.js";
import ErrorPage from "@/components/ErrorPage/ErrorPage.vue";
import SessionTable from "@/components/UserView/SessionTable.vue";
import {sessionsStore} from "@/store/users/sessionsStore.js";
import {deleteUserSessionList} from "@/externalRequests/requests.js";
import {logOutUser} from "@/validators/validators.js";
import Toast from "primevue/toast";
import {useToast} from "primevue/usetoast";
import {userFormStore} from "@/store/users/userFormStore.js";
import UserFormView from "@/components/UserView/UserFormView.vue";
import UserPasswordFormView from "@/components/UserView/UserPasswordFormView.vue";
import {userPasswordFormStore} from "@/store/users/userPasswordFormStore.js";
import UserTableSearchForm from "@/components/UserView/UserTableSearchForm.vue";
import {userSearchFormStore} from "@/store/users/userSearchFormStore.js";

// Store instances initialization
const store = usersStore();
const userSettings = userSettingsStore();

// Table column definitions
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

// Pagination options
const itemsPerPageOptions = [
  10,
  15,
  20,
  25
];

// Expanded rows management
const expandedRows = ref({});

// Handle row click to expand/collapse
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

// Handle row expansion to load sessions
const sessions = sessionsStore()

async function onRowExpand(event) {
  const user = event.data;
  await sessions.setUserId(user.id);
}

// Error handling variables
const error = ref(false)
const errorTitle = ref("ERROR")
const errorCode = ref(0)

// Load users data
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

// Load users when component mounts
onMounted(async () => {
  await loadUsers();
});

// Handle pagination changes
async function onPageChange(event) {
  console.log(event);
  store.setPaginator(
      event.page,
      event.row,
      event.pageCount);
  expandedRows.value = {};
  await loadUsers();
}

// Handle user deletion
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

// Handle user edit
function onEditUser(event) {
  userForm.setCreatingUser(false);
  userForm.setVisible(true);
  userForm.setUserId(event.id);
}

// Toast notification setup
const toast = useToast();

// Handle user logout (terminate all sessions)
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
  if (response.status !== 200) {
    userSettings.setLoading(false);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: `${response.status}: ${response.status === 503 ? responseJson.message : responseJson.detail.data.message}`,
      life: 3000
    });
    userSettings.setJwtKey(response.status === 503 ? token : responseJson.detail.token);
    return;
  }
  userSettings.setJwtKey(responseJson.token);
  if (sessions.userId === userId) {
    sessions.userId = null;
    await sessions.clearUserSessions()
    sessions.userId = userId;
    return;
  }
  userSettings.setLoading(false);
  return;
}

// User form handling
const userForm = userFormStore();

function onAddUser() {
  userForm.setCreatingUser(true);
  userForm.setVisible(true);
}

// Password form handling
const userPasswordForm = userPasswordFormStore();

function onEditUserPassword(event) {
  userPasswordForm.setVisible(true);
  userPasswordForm.setUserId(event.id);
}

// Search form handling
const userSearchForm = userSearchFormStore();

function onSearch() {
  userSearchForm.setVisible(true);
}

</script>

<template>
  <div class="w-full">
    <Toast/>
    <!-- Form components that appear conditionally -->
    <UserFormView v-if="userForm.visible" @reload="loadUsers"/>
    <UserPasswordFormView v-if="userPasswordForm.visible" @reload="loadUsers"/>
    <UserTableSearchForm v-if="userSearchForm.visible" @reload="loadUsers"/>

    <!-- Action buttons -->
    <div class="flex flex-row justify-content-between mb-3">
      <Button label="Add" icon="pi pi-plus" @click="onAddUser"/>
      <Button label="Search" severity="contrast" icon="pi pi-search" @click="onSearch"/>
    </div>

    <!-- Error display or main table -->
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
      <!-- Expander column -->
      <Column
          expander
          style="width: 3em"
      ></Column>

      <!-- Dynamic columns from columns array -->
      <Column
          v-for="col in columns"
          :key="col.field"
          :field="col.field"
          :header="col.header"
      ></Column>

      <!-- Action buttons column -->
      <Column header="Actions" style="width: 140px">
        <template #body="slotProps">
          <div class="flex flex-row">
            <Button
                icon="pi pi-key"
                class="p-button-rounded p-button-text p-button-info"
                @click.stop="onEditUserPassword(slotProps.data)"
                :aria-label="`Edit password`"
                v-tooltip="`Edit password`"
            />
            <Button
                icon="pi pi-pencil"
                class="p-button-rounded p-button-text p-button-info"
                @click.stop="onEditUser(slotProps.data)"
                :aria-label="'Edit user'"
                v-tooltip="'Edit user'"
            />
            <Button
                icon="pi pi-trash"
                class="p-button-rounded p-button-text p-button-danger"
                @click.stop="onDeleteUser(slotProps.data)"
                :aria-label="'Delete user'"
                v-tooltip="'Delete user'"
            />
            <Button
                icon="pi pi-sign-out"
                class="p-button-rounded p-button-text p-button-danger"
                @click.stop="onLogOutUser(slotProps.data)"
                :aria-label="'Logout user'"
                v-tooltip="'Logout user'"
            />
          </div>
        </template>
      </Column>
      <!-- Expanded content template (sessions table) -->
      <template #expansion>
        <SessionTable
        />
      </template>

    </DataTable>
  </div>
</template>