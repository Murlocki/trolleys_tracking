<script setup>
import Dialog from "primevue/dialog";
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import Calendar from "primevue/calendar";
import Dropdown from "primevue/dropdown";
import MultiSelect from "primevue/multiselect";
import {defineEmits, onMounted, ref} from "vue";
import {userSettingsStore} from "@/store/userSettingsStore.js";
import {userSearchFormStore} from "@/store/users/userSearchFormStore.js";
import {usersStore} from "@/store/users/usersStore.js";
import {getUserRoleList} from "@/externalRequests/requests.js";
import {logOutUser} from "@/validators/validators.js";

// Initialize Pinia stores
const store = userSearchFormStore(); // Search form state and actions
const users = usersStore(); // Users data store
const userSettings = userSettingsStore(); // User settings store

// Sort direction options for dropdowns
const sortOptions = [
  {label: "Asc", value: "asc"},
  {label: "Desc", value: "desc"},
  {label: "Not", value: null}, // No sorting
];

// User active status filter options
const isActiveOptions = [
  {label: "Yes", value: true},
  {label: "No", value: false},
  {label: "Undefined", value: null}, // No filter
];

// User roles (loaded asynchronously)
const roleOptions = ref([]);

/**
 * Component mounted lifecycle hook
 * Loads user roles and initializes form state
 */
onMounted(async () => {
  userSettings.setLoading(true);

  // Sync search params between stores
  await store.setParams(users.params);

  // Fetch available user roles from API
  const token = userSettings.getJwt.value;
  const response = await getUserRoleList(token);

  // Handle unauthorized access
  if (response.status === 401) {
    await logOutUser(response);
    return;
  }

  const responseJson = await response.json();

  // Handle API errors
  if (response.status !== 200) {
    userSettings.setJwtKey(response.status === 503 ? token : responseJson.token);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: `${response.status}: ${response.status === 503 ? responseJson.message : responseJson.detail.data.message}`,
      life: 3000
    });
    store.setVisible(false);
    userSettings.setLoading(false);
    return;
  }

  // Set available roles
  roleOptions.value = responseJson.data;

  // Initialize role filter if empty
  if (store.params.role.length === 0) {
    store.params.role = roleOptions.value.map(it => it.option);
  }

  userSettings.setLoading(false);
});

/**
 * Closes the search form and resets form data
 */
async function onClose() {
  await store.setVisible(false);
  await store.clearData();
}

// Define component events
const emit = defineEmits(["reload"]);

/**
 * Applies the current search filters
 * Clears existing user data and reloads with new filters
 */
async function onAccept() {
  userSettings.setLoading(true);
  await users.clearUsers(); // Clear current user list
  await users.setFilters(store.params); // Apply new filters
  userSettings.setLoading(false);
  emit("reload"); // Emit reload event to parent
  store.setVisible(false); // Close the form
}
</script>

<template>
  <!-- Search Form Dialog -->
  <Dialog
      modal
      class="md:w-5 sm:w-8 w-11"
      :closable="false"
      :visible="store.visible"
  >
    <!-- Dialog Header -->
    <template #header>
      <div>
        <span class="text-2xl">Search user form</span>
      </div>
    </template>

    <!-- Form Content -->
    <div class="flex flex-column gap-4">
      <!-- ID Filter Section -->
      <div class="flex flex-column gap-2">
        <div class="flex flex-row justify-content-between align-items-center border-bottom-1 border-primary">
          <span class="text-2xl">ID</span>
          <Dropdown
              :options="sortOptions"
              option-label="label"
              option-value="value"
              v-model="store.params.sortBy.id"
              placeholder="Not"
          />
        </div>
        <InputText
            id="user-id"
            aria-describedby="user-id-help"
            v-model="store.params.id"
        />
        <small id="user-id-help">Enter user ID.</small>
      </div>

      <!-- Username Filter Section -->
      <div class="flex flex-column gap-2">
        <div class="flex flex-row justify-content-between align-items-center border-bottom-1 border-primary">
          <span class="text-2xl">Username</span>
          <Dropdown
              :options="sortOptions"
              option-label="label"
              option-value="value"
              v-model="store.params.sortBy.username"
              placeholder="Not"
          />
        </div>
        <InputText
            id="username"
            aria-describedby="username-help"
            v-model="store.params.username"
        />
        <small id="username-help">Enter user username.</small>
      </div>

      <!-- Email Filter Section -->
      <div class="flex flex-column gap-2">
        <div class="flex flex-row justify-content-between align-items-center border-bottom-1 border-primary">
          <span class="text-2xl">Email</span>
          <Dropdown
              :options="sortOptions"
              option-label="label"
              option-value="value"
              v-model="store.params.sortBy.email"
              placeholder="Not"
          />
        </div>
        <InputText
            id="email"
            aria-describedby="username-help"
            v-model="store.params.email"
        />
        <small id="username-help">Enter user email.</small>
      </div>

      <!-- First Name Filter Section -->
      <div class="flex flex-column gap-2">
        <div class="flex flex-row justify-content-between align-items-center border-bottom-1 border-primary">
          <span class="text-2xl">First name</span>
          <Dropdown
              :options="sortOptions"
              option-label="label"
              option-value="value"
              v-model="store.params.sortBy.firstName"
              placeholder="Not"
          />
        </div>
        <InputText
            id="first-name"
            aria-describedby="first-name-help"
            v-model="store.params.firstName"
        />
        <small id="first-name-help">Enter user first name.</small>
      </div>

      <!-- Last Name Filter Section -->
      <div class="flex flex-column gap-2">
        <div class="flex flex-row justify-content-between align-items-center border-bottom-1 border-primary">
          <span class="text-2xl">Last name</span>
          <Dropdown
              :options="sortOptions"
              option-label="label"
              option-value="value"
              v-model="store.params.sortBy.lastName"
              placeholder="Not"
          />
        </div>
        <InputText
            id="last-name"
            aria-describedby="last-name-help"
            v-model="store.params.lastName"
        />
        <small id="last-name-help">Enter user last name.</small>
      </div>

      <!-- Role Filter Section -->
      <div class="flex flex-column gap-2">
        <div class="flex flex-row justify-content-between align-items-center border-bottom-1 border-primary">
          <span class="text-2xl">Role</span>
          <Dropdown
              :options="sortOptions"
              option-label="label"
              option-value="value"
              v-model="store.params.sortBy.role"
              placeholder="Not"
          />
        </div>
        <MultiSelect
            id="role"
            aria-describedby="role-help"
            :options="roleOptions"
            v-model="store.params.role"
            option-value="option"
            option-label="name"
        />
        <small id="role-help">Select user roles to filter by.</small>
      </div>

      <!-- Active Status Filter Section -->
      <div class="flex flex-column gap-2">
        <div class="flex flex-row justify-content-between align-items-center border-bottom-1 border-primary">
          <span class="text-2xl">Is active</span>
          <Dropdown
              :options="sortOptions"
              option-label="label"
              option-value="value"
              v-model="store.params.sortBy.isActive"
              placeholder="Not"
          />
        </div>
        <Dropdown
            id="is-active"
            aria-describedby="is-active-help"
            v-model="store.params.isActive"
            :options="isActiveOptions"
            option-label="label"
            option-value="value"
            placeholder="Undefined"
        />
        <small id="is-active-help">Filter by active status.</small>
      </div>

      <!-- Creation Date Filter Section -->
      <div class="flex flex-column gap-4">
        <div class="flex flex-row justify-content-between align-items-center border-bottom-1 border-primary">
          <span class="text-2xl">Create date</span>
          <Dropdown
              :options="sortOptions"
              option-label="label"
              option-value="value"
              v-model="store.params.sortBy.createdAt"
              placeholder="Not"
          />
        </div>
        <div class="flex flex-column gap-2">
          <label for="created-from">Created from</label>
          <Calendar
              id="created-from"
              aria-describedby="created-from-help"
              v-model="store.params.createdFrom"
              showTime
              hourFormat="12"
              showButtonBar
          />
          <small id="created-from-help">Filter users created after this date.</small>
        </div>
        <div class="flex flex-column gap-2">
          <label for="created-to">Created to</label>
          <Calendar
              id="created-to"
              aria-describedby="created-to-help"
              v-model="store.params.createdTo"
              showTime
              hourFormat="12"
              showButtonBar
          />
          <small id="created-to-help">Filter users created before this date.</small>
        </div>
      </div>

      <!-- Update Date Filter Section -->
      <div class="flex flex-column gap-4">
        <div class="flex flex-row justify-content-between align-items-center border-bottom-1 border-primary">
          <span class="text-2xl">Update date</span>
          <Dropdown
              :options="sortOptions"
              option-label="label"
              option-value="value"
              v-model="store.params.sortBy.updatedAt"
              placeholder="Not"
          />
        </div>
        <div class="flex flex-column gap-2">
          <label for="updated-from">Updated from</label>
          <Calendar
              id="updated-from"
              aria-describedby="updated-from-help"
              v-model="store.params.updatedFrom"
              showTime
              hourFormat="12"
              showButtonBar
          />
          <small id="updated-from-help">Filter users updated after this date.</small>
        </div>
        <div class="flex flex-column gap-2">
          <label for="updated-to">Updated to</label>
          <Calendar
              id="updated-to"
              aria-describedby="updated-to-help"
              v-model="store.params.updatedTo"
              showTime
              hourFormat="12"
              showButtonBar
          />
          <small id="updated-to-help">Filter users updated before this date.</small>
        </div>
      </div>
    </div>

    <!-- Dialog Footer with Action Buttons -->
    <template #footer>
      <div class="w-full flex flex-row justify-content-between align-items-center">
        <Button label="Accept" size="large" @click="onAccept"/>
        <Button label="Close" class="bg-primary-reverse" size="large" @click="onClose"/>
      </div>
    </template>
  </Dialog>
</template>

<style scoped>
/* Component-specific styles */
</style>