/**
 @param {string} sessionId
 @param {number} userId
 @param {string} accessToken
 @param {string} refreshToken
 @param {device} device
 @param {string} ipAddress
 @param {string} createdAt
 @param {string} expiresAt
 */
export class SessionDTO {
    /**
        @param {string} sessionId
        @param {number} userId
        @param {string} accessToken
        @param {string} refreshToken
        @param {device} device
        @param {string} ipAddress
        @param {string} createdAt
        @param {string} expiresAt
     */
    constructor(sessionId, userId, accessToken, refreshToken, device, ipAddress, createdAt, expiresAt) {
        this.sessionId = sessionId
        this.userId = userId
        this.accessToken = accessToken
        this.refreshToken = refreshToken
        this.device = device
        this.ipAddress = ipAddress
        this._createdAt = new Date(createdAt)
        this._expiresAt = new Date(expiresAt)

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
    get expiresAt() {
        if (this._expiresAt instanceof Date) {
            return this._expiresAt.toLocaleString('en-EN', {
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