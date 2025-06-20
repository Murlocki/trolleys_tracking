import {UserData} from "@/models/user/UserDTO.js";

/**
 @param {string} username - Имя пользователя
 @param {string} password - Пароль пользователя
 @param {UserData} userData - Данные пользователя - человека
 @param {string} role - Роль пользователя
 */
export class UserCreate {
    /**
     * @param {string} username - Имя пользователя
     * @param {string} password - Пароль пользователя
     * @param {UserData} userData - Данные пользователя - человека
     * @param {string} role - Роль пользователя
     */
    constructor(username, password, userData, role) {
        this.role = role
        this.username = username
        this.password = password
        this.userData = role !== "service" ? new UserData(userData.firstName, userData.lastName, userData.email) : null;
    }
}