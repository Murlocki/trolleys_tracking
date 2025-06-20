/**
 * Data Transfer Object for user password information
 * @class
 */
export class PasswordDTO{
    /**
     * @param {string} newPassword - Новый пароль пользователя
     * @param {number} userVersion - Версия пользователя
     */
    constructor(newPassword, userVersion) {
        this.newPassword = newPassword;
        this.userVersion = userVersion;
    }
}
