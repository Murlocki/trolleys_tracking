/**
 * @param {number} id
 * @param {string} name
 * @param {string} address
 * @param {string} description
 * @param {number} version
 * @param {string} createdAt
 * @param {string} updatedAt
 */
export class SubscriptionDTO {
    /**
     * @param {number} id
     * @param {number} cameraId
     * @param {string} cameraName
     * @param {number} userId
     * @param {userName} userName
     * @param {string} createdAt
     * @param {string} updatedAt
     */
    constructor(id, cameraId, cameraName, userId, userName, createdAt, updatedAt) {
        this.id = id
        this.cameraId = cameraId
        this.cameraName = cameraName
        this.userId = userId
        this.userName = userName
        this._createdAt = new Date(createdAt)
        this._updatedAt = new Date(updatedAt)


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