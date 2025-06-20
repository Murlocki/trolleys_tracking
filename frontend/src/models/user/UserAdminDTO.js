/**
 * Data Transfer Object (DTO) for user administration
 * @class
 */
export class UserAdminDTO {
    /**
     * Create a UserAdminDTO instance
     * @constructor
     * @param {number} id - User's unique identifier
     * @param {string} username - User's login name
     * @param {string} firstName - User's first name
     * @param {string} lastName - User's last name
     * @param {string} email - User's email address
     * @param {string} createdAt - User creation timestamp (ISO string)
     * @param {string} updatedAt - User last update timestamp (ISO string)
     * @param {boolean} isActive - Whether the user account is active
     * @param {string} role - User's system role (enum value)
     * @param {string} roleDisplay - Human-readable role name
     * @param {number} version - Data version for optimistic locking
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

    /**
     * Gets formatted creation date string
     * @returns {string|null} Formatted date string (e.g., "January 15, 2023, 02:30 PM") or null if invalid
     */
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

    /**
     * Gets formatted update date string
     * @returns {string|null} Formatted date string (e.g., "January 15, 2023, 02:30 PM") or null if invalid
     */
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