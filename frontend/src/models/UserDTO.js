class UserData{
    /**
     *
     * @param {string} firstName
     * @param {string} lastName
     * @param {string} email
     */
    constructor(firstName, lastName, email) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.email = email;
    }
}



/**
 @param {number} id - Идентификатор пользователя
 @param {string} username - Имя пользователя
 @param {UserData} userData - Данные пользователя - человека
 @param {string} createdAt - Дата создания пользователя
 @param {string} updatedAt - Дата обновления пользователя
 @param {boolean} isActive - Активен ли пользователь
 @param {string} role - Роль пользователя
 @param {string} roleDisplay - Отображаемая роль пользователя
 @param {number} version - Версия пользователя
 */
export class UserDTO {
    /**
     * @param {number} id - Идентификатор пользователя
     * @param {string} username - Имя пользователя
     * @param {UserData} userData - Данные пользователя - человека
     * @param {string} createdAt - Дата создания пользователя
     * @param {string} updatedAt - Дата обновления пользователя
     * @param {boolean} isActive - Активен ли пользователь
     * @param {string} role - Роль пользователя
     * @param {string} roleDisplay - Отображаемая роль пользователя
     * @param {number} version - Версия пользователя
     */
    constructor(id, username, userData, createdAt, updatedAt, isActive, role, roleDisplay, version) {
        this._createdAt = new Date(createdAt)
        this.userData = new UserData(userData.firstName, userData.lastName, userData.email)
        this.id = id
        this.isActive = isActive
        this.role = role
        this.roleDisplay = roleDisplay
        this._updatedAt = new Date(updatedAt)
        this.username = username
        this.version = version
    }

    get firstName() {
        return this.userData? this.userData.firstName : null
    }


    get lastName() {
        return this.userData? this.userData.lastName : null
    }


    get email() {
        return this.userData? this.userData.email : null
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