import { userSettingsStore } from '../store/userSettingsStore'

class RegisterAuthService {
    constructor() {
        /*Заглушка Url */
        this.baseUrl = ''
    }
    checkUserNameExist(valueToCheck) {
        /*Заглушка типо есть юзер с таким именем */
        return false
    }
    loginUser(userLogin, userPassword) {
        //Тут типо еще проверка верности пароля и логина будет
        this.store = userSettingsStore()
        this.store.setLoggin(userLogin)
        this.store.setLogged(true)
        //Тут еще типо ключ этот поставили
        this.store.$state.setJwtKey('Заглушка ключ')
        return true
    }
}

export default new RegisterAuthService()
