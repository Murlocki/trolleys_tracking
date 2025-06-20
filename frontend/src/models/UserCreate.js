import {UserData} from "@/models/UserDTO.js";

/**
 @param {string} username - Имя пользователя
 @param {string} password - Пароль пользователя
 @param {UserData} userData - Данные пользователя - человека
 @param {boolean} isActive - Активен ли пользователь
 @param {string} role - Роль пользователя
 */
export class UserCreate {
    /**
     * @param {string} username - Имя пользователя
     * @param {string} password - Пароль пользователя
     * @param {UserData} userData - Данные пользователя - человека
     * @param {boolean} isActive - Активен ли пользователь
     * @param {string} role - Роль пользователя
     */
    constructor(username, password, userData, isActive, role) {
        this.isActive = isActive
        this.role = role
        this.username = username
        this.password = password
        this.userData = role !== "service" ? new UserData(userData.firstName, userData.lastName, userData.email) : null;
    }
}