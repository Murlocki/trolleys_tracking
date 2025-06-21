/**
 * @param {number} cameraId
 * @param {number} userId
 */
export class SubscriptionCreateDTO {
    /**
     * @param {number} cameraId
     * @param {number} userId
     */

    constructor(cameraId, userId) {
        this.cameraId = cameraId
        this.userId = userId
    }
}