<script setup>
import Button from "primevue/button";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import {userSettingsStore} from "@/store/userSettingsStore.js";
import Toast from "primevue/toast";
import {ref, watch} from "vue";
import {sessionsStore} from "@/store/users/sessionsStore.js";
import ErrorPage from "@/components/ErrorPage/ErrorPage.vue";
import {useToast} from "primevue/usetoast";

/**
 * Хранилище сессий пользователя
 * @type {import('pinia').Store}
 */
const store = sessionsStore();

/**
 * Конфигурация колонок таблицы сессий
 * @type {Array<{field: string, header: string}>}
 */
const columnsSession = [
  {field: "sessionId", header: "ID"},
  {field: "ipAddress", header: "IP-address"},
  {field: "device", header: "Device"},
  {field: "createdAt", header: "Created at"},
  {field: "expiresAt", header: "Updated at"},
];

// Хранилище настроек пользователя
const settings = userSettingsStore();

// Состояние для обработки ошибок
const error = ref(false);
const errorCode = ref(0);
const errorTitle = ref("");

/**
 * Загружает сессии пользователя
 * @async
 * @param {number} userId - ID пользователя
 * @returns {Promise<void>}
 */
async function setSessions(userId) {
  error.value = false;
  errorCode.value = 0;
  errorTitle.value = "";

  const token = settings.getJwt.value;
  settings.setLoading(true);

  // Очищаем предыдущие сессии
  await store.clearUserSessions();

  // Загружаем новые сессии
  const response = await store.fetchSessions(token, userId);
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
watch(() => store.$state.userId, async (newVal) => {
  if (newVal) {
    await setSessions(newVal);
  }
}, {immediate: true});

// Инициализация Toast-уведомлений
const toast = useToast();

/**
 * Удаляет сессию пользователя
 * @async
 * @param {Object} data - Данные сессии
 * @param {string} data.sessionId - ID сессии
 * @param {number} data.userId - ID пользователя
 * @returns {Promise<void>}
 */
async function onDeleteSession(data) {
  settings.setLoading(true);

  // Отправляем запрос на удаление сессии
  const response = await store.deleteUserSessionById(
      settings.getJwt.value,
      data.userId,
      data.sessionId
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

  // Обновляем список сессий после удаления
  await setSessions(data.userId);
}
</script>

<template>
  <!-- Компонент для Toast-уведомлений -->
  <Toast />

  <!-- Страница ошибки (отображается при ошибке) -->
  <ErrorPage
      v-if="error"
      :error-code="errorCode"
      :error-text="errorTitle"
  />

  <!-- Сообщение при отсутствии сессий -->
  <div
      class="w-full flex justify-content-center"
      v-else-if="store.sessions.length===0"
  >
    <span class="text-2xl">No sessions</span>
  </div>

  <!-- Таблица сессий -->
  <DataTable
      v-else
      :value="store.sessions || []"
      size="small"
      class="w-full nested-table"
      :scrollable="true"
      stripedRows
  >
    <!-- Динамическое создание колонок -->
    <Column
        v-for="col in columnsSession"
        :key="col.field"
        :field="col.field"
        :header="col.header"
    />

    <!-- Колонка с действиями -->
    <Column header="Actions" style="width: 140px">
      <template #body="slotProps">
        <div class="w-full flex justify-content-center align-content-center">
          <!-- Кнопка удаления сессии -->
          <Button
              icon="pi pi-trash"
              class="p-button-rounded p-button-text p-button-danger"
              @click.stop="onDeleteSession(slotProps.data)"
              :aria-label="'Delete ' + slotProps.data.name"
          />
        </div>
      </template>
    </Column>
  </DataTable>
</template>

<style scoped>
/* Стили компонента */
</style>