import {defineStore} from "pinia";
import {
    createCamera,
    getCameraById,
    getCameraStatusById, startCameraById,
    stopCameraById,
    updateCameraById
} from "@/externalRequests/requests.js";
import {logOutUser, unprocessableEntity} from "@/validators/validators.js";
import {CameraDTO} from "@/models/CameraDTO.js";

/**
 * @module stores/cameras/cameraControlStore
 */
export const cameraControlStore = defineStore("cameraControlStore", {
    state: () => ({
        groupId: null,
        cameraId: null,
        status: null,
        detectionRegime: null,
        classificationRegime: null,
        trackingRegime: null,
        visible: false,
    }),
    actions: {
        /**
         * Sets the current camera's ID
         * @param {number} groupId - The group ID to set
         * @param {number} cameraId - The camera ID to set
         */
        setCameraId(groupId, cameraId) {
            this.$state.groupId = groupId;
            this.$state.cameraId = cameraId;
        },
        setVisible(visible) {
            this.$state.visible = visible;
        },
        /**
         * Fetches camera status by ID
         * @param {string} token - Authentication token
         * @param {number} groupId - ID of camera's group
         * @param {number} cameraId - ID of the camera to fetch
         * @returns {Promise<{token: string, status: number, message?: string}>} Response object with token, status and optional message
         */
        async fetchCameraStatus(token, groupId, cameraId) {
            try {
                const response = await getCameraStatusById(token, groupId, cameraId);

                if (response.status === 401) {
                    return await logOutUser(response);
                }

                if (response.status === 503) {
                    return {token: token, status: 503, message: "Network Error"};
                }

                const responseJson = await response.json();
                if (response.ok) {
                    await this.setStatus(responseJson.data.status);
                    return {token: responseJson.token, status: response.status};
                }

                const details = responseJson.detail;
                return {token: details.token, status: response.status, message: details.data.message};
            } catch (error) {
                console.error(error);
                return {token, status: 503, message: "Network Error"};
            }
        },
        setStatus(status) {
            this.status = status;
        },
        async stopCameraProcess(token, groupId, cameraId) {
            try {
                const response = await stopCameraById(token, groupId, cameraId);

                if (response.status === 401) {
                    return await logOutUser(response);
                }

                if (response.status === 503) {
                    return {token: token, status: 503, message: "Network Error"};
                }

                const responseJson = await response.json();
                if (response.ok) {
                    await this.setStatus(responseJson.data.status);
                    return {token: responseJson.token, status: response.status};
                }

                const details = responseJson.detail;
                return {token: details.token, status: response.status, message: details.data.message};
            } catch (error) {
                console.error(error);
                return {token, status: 503, message: "Network Error"};
            }
        },
        async startCameraProcess(token) {
            try {
                const params = {
                    detectionRegime:this.detectionRegime,
                    classificationRegime:this.classificationRegime,
                    trackingRegime:this.trackingRegime,
                }
                const response = await startCameraById(token, this.groupId, this.cameraId, params);

                if (response.status === 401) {
                    return await logOutUser(response);
                }

                if (response.status === 503) {
                    return {token: token, status: 503, message: "Network Error"};
                }

                const responseJson = await response.json();
                if (response.ok) {
                    await this.setStatus("active");
                    return {token: responseJson.token, status: response.status};
                }

                const details = responseJson.detail;
                return {token: details.token, status: response.status, message: details.data.message};
            } catch (error) {
                console.error(error);
                return {token, status: 503, message: "Network Error"};
            }
        },

    },
    getters: {
        isActive: (state) => state.status !== "not_active",
    }
});