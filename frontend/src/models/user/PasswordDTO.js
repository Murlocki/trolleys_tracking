/**
 * @param {string} newPassword - Новый пароль пользователя
 * @param {number} userVersion - Версия пользователя
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
