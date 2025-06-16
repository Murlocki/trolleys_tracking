/**
 * @param {number} id
 * @param {string} name
 * @param {string} address
 * @param {string} description
 * @param {number} version
 * @param {string} createdAt
 * @param {string} updatedAt
 */
export class CameraDTO {
    /**
     * @param {number} id
     * @param {string} name
     * @param {string} addressLink
     * @param {number} groupId
     * @param {number} version
     * @param {string} createdAt
     * @param {string} updatedAt
     */
    constructor(id, name, addressLink, groupId , version , createdAt, updatedAt) {
        this.id = id
        this.name = name
        this.addressLink = addressLink
        this.groupId = groupId
        this.version = version
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