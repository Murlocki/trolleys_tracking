import RegisterAuthService from '../services/RegisterAuthService'

class RegisterFormValidator {
    constructor() {
        this.regAuthService = RegisterAuthService
    }
    validateUsername(value) {
        if (this.regAuthService.checkUserNameExist(value)) {
            return false
        }

        const regex = new RegExp('^[A-Za-z][A-Za-z0-9_]{7,29}$')
        return regex.test(value)
    }
    validateEmail(value) {
        const regex = new RegExp(/^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/)
        return regex.test(value)
    }
    validatePassword(value) {
        const regex = new RegExp(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&+=-])[A-Za-z\d@$!%*?&+=-]{8,}$/)
        return regex.test(value)
    }
}
export default new RegisterFormValidator()
