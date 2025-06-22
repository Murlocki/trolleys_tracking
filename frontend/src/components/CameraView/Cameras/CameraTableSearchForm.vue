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
import {cameraSearchFormStore} from "@/store/cameras/cameraSearchFormStore.js";
import {camerasStore} from "@/store/cameras/cameraStore.js";

// Initialize Pinia stores
const store = cameraSearchFormStore(); // Search form state and actions
const cameras = camerasStore(); // Users data store
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

/**
 * Component mounted lifecycle hook
 * Loads user roles and initializes form state
 */
onMounted(async () => {
  userSettings.setLoading(true);
  await store.setParams(cameras.params);
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
  await cameras.clearCameras(); // Clear current user list
  await cameras.setFilters(store.params); // Apply new filters
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
        <span class="text-2xl">Search camera form</span>
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
            id="id"
            aria-describedby="id-help"
            v-model="store.params.id"
        />
        <small id="id-help">Enter camera ID.</small>
      </div>

      <!-- Username Filter Section -->
      <div class="flex flex-column gap-2">
        <div class="flex flex-row justify-content-between align-items-center border-bottom-1 border-primary">
          <span class="text-2xl">Name</span>
          <Dropdown
              :options="sortOptions"
              option-label="label"
              option-value="value"
              v-model="store.params.sortBy.name"
              placeholder="Not"
          />
        </div>
        <InputText
            id="name"
            aria-describedby="name-help"
            v-model="store.params.name"
        />
        <small id="name-help">Enter camera name.</small>
      </div>

      <!-- Email Filter Section -->
      <div class="flex flex-column gap-2">
        <div class="flex flex-row justify-content-between align-items-center border-bottom-1 border-primary">
          <span class="text-2xl">Address link</span>
          <Dropdown
              :options="sortOptions"
              option-label="label"
              option-value="value"
              v-model="store.params.sortBy.addressLink"
              placeholder="Not"
          />
        </div>
        <InputText
            id="address"
            aria-describedby="address-help"
            v-model="store.params.addressLink"
        />
        <small id="address-help">Enter camera address link.</small>
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