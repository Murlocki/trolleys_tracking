const express = require("express");
const { createServer } = require("http");
const { Server } = require("socket.io");

const app = express();
const httpServer = createServer(app);
const PORT = 3000;

// Настройка CORS
const io = new Server(httpServer, {
    cors: {
        origin: "http://ваш-фронтенд:порт", // Замените на адрес фронта
        allowedHeaders: ["Authorization", "X-Cam"],
        credentials: true,
    },
});

// Middleware для проверки токена
io.use((socket, next) => {
    const token = socket.handshake.headers.authorization?.replace("Bearer ", "");
    const cameraId = socket.handshake.headers["x-cam"];

    if (!token || !cameraId) {
        return next(new Error("Не хватает токена или ID камеры"));
    }

    // Здесь проверяем токен (например, через JWT.verify)
    console.log("Подключение камеры:", cameraId);
    next();
});

// Обработка подключений
io.on("connection", (socket) => {
    const cameraId = socket.handshake.headers["x-cam"];
    console.log(`Камера ${cameraId} подключена`);

    // Отправка тестовых данных каждые 2 секунды
    const interval = setInterval(() => {
        socket.emit("stream:data", {
            frame: "base64-encoded-image-data",
            status: "active",
            timestamp: Date.now(),
        });
    }, 2000);

    // Обработка команд от клиента
    socket.on("record:start", (data) => {
        console.log(`Запись для камеры ${cameraId} начата с настройками:`, data);
    });

    socket.on("camera_frame", () => {
        clearInterval(interval);
        console.log(`Камера ${cameraId} отключена`);
    });

    socket.on("disconnect", () => {
        clearInterval(interval);
        console.log(`Камера ${cameraId} отключена`);
    });
});

httpServer.listen(PORT, () => {
    console.log(`Сервер запущен на порту ${PORT}`);
});