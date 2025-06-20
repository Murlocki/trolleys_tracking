import { UserData } from "@/models/user/UserDTO.js";

/**
 * Data Transfer Object (DTO) for user creation
 * @class
 */
export class UserCreate {
    /**
     * Create a UserCreate DTO instance
     * @constructor
     * @param {string} username - User's login name (must be unique)
     * @param {string} password - User's password (will be hashed)
     * @param {UserData} userData - Personal data of the user (optional for service accounts)
     * @param {string} role - System role of the user (e.g., 'admin', 'user', 'service')
     */
    constructor(username, password, userData, role) {
        this.role = role;
        this.username = username;
        this.password = password;
        this.userData = role !== "service"
            ? new UserData(userData.firstName, userData.lastName, userData.email)
            : null;
    }
}