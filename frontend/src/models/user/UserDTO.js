/**
 * Represents personal user information
 * @class
 */
export class UserData {
    /**
     * Create a UserData instance
     * @constructor
     * @param {string} firstName - User's first name
     * @param {string} lastName - User's last name
     * @param {string} email - User's email address
     */
    constructor(firstName, lastName, email) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.email = email;
    }
}

/**
 * Data Transfer Object for basic user information
 * @class
 */
export class UserDTO {
    /**
     * Create a UserDTO instance
     * @constructor
     * @param {number} id - Unique user identifier
     * @param {string} username - User's login name
     * @param {UserData|null} userData - Personal user information
     * @param {boolean} isActive - Indicates if the user account is active
     * @param {string} role - User's system role
     * @param {number} version - Version number for optimistic concurrency control
     */
    constructor(id, username, userData, isActive, role, version) {
        this.userData = userData ? new UserData(userData.firstName, userData.lastName, userData.email) : null;
        this.id = id;
        this.isActive = isActive;
        this.role = role;
        this.username = username;
        this.version = version;
    }

    /**
     * Gets the user's first name
     * @returns {string|null} First name if available
     */
    get firstName() {
        return this.userData ? this.userData.firstName : null;
    }

    /**
     * Gets the user's last name
     * @returns {string|null} Last name if available
     */
    get lastName() {
        return this.userData ? this.userData.lastName : null;
    }

    /**
     * Gets the user's email address
     * @returns {string|null} Email address if available
     */
    get email() {
        return this.userData ? this.userData.email : null;
    }
}