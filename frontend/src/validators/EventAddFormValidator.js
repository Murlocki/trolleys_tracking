class EventAddFormValidator {
    validateDate(value) {
        if (!value) {
            return false
        }
        return true
    }
    validateEndDate(startDate, endDate) {
        if (endDate && new Date(endDate) < new Date(startDate)) {
            return false
        }
        return true
    }
}
export default new EventAddFormValidator()
