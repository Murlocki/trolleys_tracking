export class UserData {
    /**
     *
     * @param {string} firstName
     * @param {string} lastName
     * @param {string} email
     */
    constructor(firstName, lastName, email) {
        this.firstName = firstName || null;
        this.lastName = lastName || null;
        this.email = email || null;
    }
}


/**
 @param {number} id - Идентификатор пользователя
 @param {string} username - Имя пользователя
 @param {UserData} userData - Данные пользователя - человека
 @param {boolean} isActive - Активен ли пользователь
 @param {string} role - Роль пользователя
 @param {number} version - Версия пользователя
 */
export class UserDTO {
    /**
     * @param {number} id - Идентификатор пользователя
     * @param {string} username - Имя пользователя
     * @param {UserData} userData - Данные пользователя - человека
     * @param {boolean} isActive - Активен ли пользователь
     * @param {string} role - Роль пользователя
     * @param {number} version - Версия пользователя
     */
    constructor(id, username, userData, isActive, role, version) {
        this.userData = userData? new UserData(userData.firstName, userData.lastName, userData.email) : null;
        this.id = id
        this.isActive = isActive
        this.role = role
        this.username = username
        this.version = version
    }

    get firstName() {
        return this.userData ? this.userData.firstName : null
    }


    get lastName() {
        return this.userData ? this.userData.lastName : null
    }


    get email() {
        return this.userData ? this.userData.email : null
    }
}