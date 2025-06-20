/**
 * Data Transfer Object for user auth information
 * @class
 */
export class AuthForm {
    /**
     * @param {string} identifier - Идентификатор пользователя
     * @param {string} password - Пароль пользователя
     * @param {string} device - Устройство пользователя
     * @param {string} ip_address - Адрес устройства пользователя
     * @param {boolean} remember_me - Нужно ли запоминать сессиию пользователя
     */
    constructor(identifier, password, device, ip_address, remember_me = false) {
        this.identifier = identifier
        this.password = password
        this.device = device
        this.ip_address = ip_address
        this.remember_me = remember_me
    }

}