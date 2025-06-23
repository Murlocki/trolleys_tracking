<script setup>
import Dialog from "primevue/dialog";
import Button from "primevue/button";
import {ref, watch} from "vue";
import {userSettingsStore} from "@/store/userSettingsStore.js";
import Toast from "primevue/toast";
import {useToast} from "primevue/usetoast";
import {io} from "socket.io-client";
import {connectSocket} from "@/externalRequests/endpoints.js";
import {cameraControlStore} from "@/store/cameras/cameraControlStore.js";
import Image from "primevue/image";

// Stores
const userSettings = userSettingsStore();
const cameraControl = cameraControlStore();
const toast = useToast();

// Socket.IO
const socket = ref(null);
const imageRef = ref(null);
// Подключение к камере
const connectToCamera = async () => {
  const token = userSettings.getJwt.value;
  const cameraId = cameraControl.cameraId; // ID из store

  if (!cameraId) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No selected camera',
      life: 3000
    });
    return;
  }

  socket.value = io(connectSocket, {
    transports: ["websocket"],
    transportOptions: {
      websocket: {
        extraHeaders: {
          "Authorization": `Bearer ${token}`,
          "X-Cam": cameraId,
          "X-API-Key": token,
        }
      }
    },
  });

  // Обработчики событий
  socket.value.on("connect", () => {
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: `Connected to camera : ${cameraId}`,
      life: 3000
    });
  });


  socket.value.on("error", (err) => {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: `Connection error: ${err.message}`,
      life: 3000
    });
  });

  socket.value.on("camera_frame", (data) => {
    if (data.image) {
      // Формируем Data URL для изображения
      imageRef.value = `data:image/jpeg;base64,${data.frame}`;
    }
  })
};

// Отключение от камеры
const disconnectFromCamera = () => {
  if (socket.value) {
    socket.value.disconnect();
    socket.value = null;
    cameraControl.clearStreamData();
    console.log("Соединение с камерой закрыто");
  }
};

// Закрытие формы
const onClose = async () => {
  await cameraControl.setWatchVisible(false);
};


// Подключение к камере при открытии формы
watch(() => cameraControl.visible, async (isVisible) => {
  if (isVisible) {
    await connectToCamera();
  } else {
    disconnectFromCamera();
  }
},{immediate: true});

</script>

<template>
  <Toast />
  <Dialog
      v-model:visible="cameraControl.watchVisible"
      modal
      :show-header="false"
      class="md:w-8 sm:w-10 w-full pt-4 px-4"
      contentStyle="padding: 0"
  >
    <div class="flex-grow-1 w-full h-full relative overflow-hidden">
      <div class="w-full">
        <span class="text-3xl font-bold">Camera watching</span>
      </div>
      <Image :src="imageRef" :preview="false" containerClass="w-full h-full">
        <template #image>
          <img
              :src="imageRef"
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
            @click="onClose"

        />
      </div>
    </template>
  </Dialog>
</template>

<style scoped>
.stream-preview {
  margin-top: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}
.stream-preview img {
  width: 100%;
  height: auto;
}
</style>