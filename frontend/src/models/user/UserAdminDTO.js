/**
 @param {number} id - Идентификатор пользователя
 @param {string} username - Имя пользователя
 @param {string} firstName - Имя пользователя
 @param {string} lastName - Фамилия пользователя
 @param {string} email - Электронная почта пользователя
 @param {string} createdAt - Дата создания пользователя
 @param {string} updatedAt - Дата обновления пользователя
 @param {boolean} isActive - Активен ли пользователь
 @param {string} role - Роль пользователя
 @param {string} roleDisplay - Отображаемая роль пользователя
 @param {number} version - Версия пользователя
 */
export class UserAdminDTO {
    /**
     * @param {number} id - Идентификатор пользователя
     * @param {string} username - Имя пользователя
     * @param {string} firstName - Имя пользователя
     * @param {string} lastName - Фамилия пользователя
     * @param {string} email - Электронная почта пользователя
     * @param {string} createdAt - Дата создания пользователя
     * @param {string} updatedAt - Дата обновления пользователя
     * @param {boolean} isActive - Активен ли пользователь
     * @param {string} role - Роль пользователя
     * @param {string} roleDisplay - Отображаемая роль пользователя
     * @param {number} version - Версия пользователя
     */
    constructor(id, username, firstName, lastName, email, createdAt, updatedAt, isActive, role, roleDisplay, version) {
        this._createdAt = new Date(createdAt)
        this.email = email
        this.firstName = firstName
        this.id = id
        this.isActive = isActive
        this.lastName = lastName
        this.role = role
        this.roleDisplay = roleDisplay
        this._updatedAt = new Date(updatedAt)
        this.username = username
        this.version = version
    }

    get createdAt() {
        if (this._createdAt instanceof Date) {
            return this._createdAt.toLocaleString('en-EN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
            });
        }
        return null;
    }

    get updatedAt() {
        if (this._updatedAt instanceof Date) {
            return this._updatedAt.toLocaleString('en-EN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
            });
        }
        return null;
    }
}