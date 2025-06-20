import {UserData} from "@/models/user/UserDTO.js";

/**
 @param {string} username - Имя пользователя
 @param {UserData} userData - Данные пользователя - человека
 @param {boolean} isActive - Активен ли пользователь
 @param {string} role - Роль пользователя
 @param {number} version - Версия пользователя
 */
export class UserUpdate {
    /**
     * @param {string} username - Имя пользователя
     * @param {UserData} userData - Данные пользователя - человека
     * @param {boolean} isActive - Активен ли пользователь
     * @param {string} role - Роль пользователя
     * @param {number} version - Версия пользователя
     */
    constructor(username, userData, isActive, role, version) {
        this.isActive = isActive
        this.role = role
        this.username = username
        this.userData = role !== "service" ? new UserData(userData.firstName, userData.lastName, userData.email) : null;
        this.version = version;
    }
}