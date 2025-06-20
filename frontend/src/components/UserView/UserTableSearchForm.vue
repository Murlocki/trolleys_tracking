<script setup>
import Dialog from "primevue/dialog";
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import Calendar from "primevue/calendar";
import Dropdown from "primevue/dropdown";
import {onMounted, ref, defineEmits} from "vue";
import {userSettingsStore} from "@/store/userSettingsStore.js";
import {userSearchFormStore} from "@/store/users/userSearchFormStore.js";
import {usersStore} from "@/store/users/usersStore.js";


const store = userSearchFormStore();
const users = usersStore();
const userSettings = userSettingsStore()
const sortOptions = [
    { label: "Asc", value: "asc" },
    { label: "Desc", value: "desc" },
    { label: "Not", value: null },
]
onMounted(async () => {
  userSettings.setLoading(true);
  await store.setParams(users.params)

  userSettings.setLoading(false);
  console.log(store.visible)
  console.log(store.params)
})

async function onClose() {
  await store.clearData();
  await store.setVisible(false);
}

const emit = defineEmits(["reload"])

async function onAccept() {
  userSettings.setLoading(true);
  await users.clearUsers()
  await users.setFilters(store.params)
  userSettings.setLoading(false);
  emit("reload");
  store.setVisible(false);
}

</script>

<template>
  <Dialog
      modal
      class="md:w-5 sm:w-8 w-11"
      :closable="false"
      :visible="store.visible"
  >
    <template #header>
      <div>
        <span class="text-2xl">Search user form</span>
      </div>
    </template>
    <div class="flex flex-column gap-4">
      <div class="flex flex-column gap-2">
        <div class="flex flex-row justify-content-between align-items-center border-bottom-1 border-primary">
          <span class="text-2xl">ID</span>
          <Dropdown :options="sortOptions" option-label="label" option-value="value"/>
        </div>
        <InputText
            id="user-id"
            aria-describedby="user-id-help"
        />
        <small id="user-id-help">Enter user ID.</small>
      </div>
      <div class="flex flex-column gap-2">
        <div class="flex flex-row justify-content-between align-items-center border-bottom-1 border-primary">
          <span class="text-2xl">Username</span>
          <Dropdown :options="sortOptions" option-label="label" option-value="value"/>
        </div>
        <InputText
            id="username"
            aria-describedby="username-help"
        />
        <small id="username-help">Enter user username.</small>
      </div>
      <div class="flex flex-column gap-2">
        <div class="flex flex-row justify-content-between align-items-center border-bottom-1 border-primary">
          <span class="text-2xl">Email</span>
          <Dropdown :options="sortOptions" option-label="label" option-value="value"/>
        </div>
        <InputText
            id="email"
            aria-describedby="username-help"
        />
        <small id="username-help">Enter user email.</small>
      </div>

      <div class="flex flex-column gap-2">
        <div class="flex flex-row justify-content-between align-items-center border-bottom-1 border-primary">
          <span class="text-2xl">First name</span>
          <Dropdown :options="sortOptions" option-label="label" option-value="value"/>
        </div>
        <InputText
            id="first-name"
            aria-describedby="first-name-help"
        />
        <small id="first-name-help">Enter user first name.</small>
      </div>

      <div class="flex flex-column gap-2">
        <div class="flex flex-row justify-content-between align-items-center border-bottom-1 border-primary">
          <span class="text-2xl">Last name</span>
          <Dropdown :options="sortOptions" option-label="label" option-value="value"/>
        </div>
        <InputText
            id="last-name"
            aria-describedby="last-name-help"
        />
        <small id="last-name-help">Enter user last name.</small>
      </div>

      <div class="flex flex-column gap-2">
        <div class="flex flex-row justify-content-between align-items-center border-bottom-1 border-primary">
          <span class="text-2xl">Role</span>
          <Dropdown :options="sortOptions" option-label="label" option-value="value"/>
        </div>
        <InputText
            id="role"
            aria-describedby="role-help"
        />
        <small id="role-help">Enter user role name.</small>
      </div>
      <div class="flex flex-column gap-4">
        <div class="flex flex-row justify-content-between align-items-center border-bottom-1 border-primary">
          <span class="text-2xl">Create date</span>
          <Dropdown :options="sortOptions" option-label="label" option-value="value"/>
        </div>
        <div class="flex flex-column gap-2">
          <label for="created-from">Created from</label>
          <Calendar
              id="created-from"
              aria-describedby="created-from-help"
          />
          <small id="created-from-help">Enter user created from date.</small>
        </div>
        <div class="flex flex-column gap-2">
          <label for="created-to">Created to</label>
          <Calendar
              id="created-to"
              aria-describedby="created-to-help"
          />
          <small id="created-to-help">Enter user created to date.</small>
        </div>
      </div>
      <div class="flex flex-column gap-4">
        <div class="flex flex-row justify-content-between align-items-center border-bottom-1 border-primary">
          <span class="text-2xl">Update date</span>
          <Dropdown :options="sortOptions" option-label="label" option-value="value"/>
        </div>
        <div class="flex flex-column gap-2">
          <label for="updated-from">Updated from</label>
          <Calendar
              id="updated-from"
              aria-describedby="updated-from-help"
          />
          <small id="updated-from-help">Enter user updated from date.</small>
        </div>
        <div class="flex flex-column gap-2">
          <label for="updated-to">Updated to</label>
          <Calendar
              id="updated-to"
              aria-describedby="updated-to-help"
          />
          <small id="updated-to-help">Enter user updated to date.</small>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="w-full flex flex-row justify-content-between align-items-center">
        <Button label="Accept" size="large" @click="onAccept"/>
        <Button label="Close" class="bg-primary-reverse" size="large" @click="onClose"/>
      </div>
    </template>
  </Dialog>
</template>

<style scoped>

</style>