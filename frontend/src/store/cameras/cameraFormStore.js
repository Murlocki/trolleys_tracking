import {defineStore} from "pinia";
import {createCamera, getCameraById, updateCameraById} from "@/externalRequests/requests.js";
import {logOutUser, unprocessableEntity} from "@/validators/validators.js";
import {CameraDTO} from "@/models/CameraDTO.js";

/**
 * Pinia store for managing user form data and operations
 * @module stores/cameras/cameraFormStore
 */
export const cameraFormStore = defineStore("cameraFormStore", {
    state: () => ({
        /** @type {CameraDTO|null} - Current user DTO instance */
        camera: null,
        /** @type {number|null} - Camera's ID */
        id: null,
        /** @type {number|null} - Camera's group ID */
        groupId: null,
        /** @type {string|null} - Camera's name */
        name: null,
        /** @type {string|null} - Camera's address link */
        addressLink: null,
        /** @type {number} - Data version for optimistic concurrency */
        version: 0,
        /** @type {boolean} - Visibility state of the user form */
        visible: false,
        /** @type {boolean} - Flag indicating creation mode */
        creatingCamera: false,
    }),

    actions: {
        /**
         * Sets the current camera's ID
         * @param {number} groupId - The group ID to set
         * @param {number} cameraId - The camera ID to set
         */
        async setCameraId(groupId, cameraId) {
            this.$state.groupId = groupId;
            this.$state.id = cameraId;
        },

        /**
         * Fetches camera data by ID
         * @param {string} token - Authentication token
         * @param {number} groupId - ID of camera's group
         * @param {number} cameraId - ID of the camera to fetch
         * @returns {Promise<{token: string, status: number, message?: string}>} Response object with token, status and optional message
         */
        async fetchCameraData(token, groupId, cameraId) {
            try {
                const response = await getCameraById(token, groupId, cameraId);

                if (response.status === 401) {
                    return await logOutUser(response);
                }

                if (response.status === 503) {
                    return {token: token, status: 503, message: "Network Error"};
                }

                const responseJson = await response.json();
                if (response.ok) {
                    await this.setCamera(responseJson.data);
                    await this.setCameraFields(this.$state.camera);
                    return {token: responseJson.token, status: response.status};
                }

                const details = responseJson.detail;
                return {token: details.token, status: response.status, message: details.data.message};
            } catch (error) {
                console.error(error);
                return {token, status: 503, message: "Network Error"};
            }
        },

        /**
         * Sets the current camera object
         * @param {CameraDTO} camera - Camera data object
         */
        async setCamera(camera) {
            this.camera = new CameraDTO(
                camera.id,
                camera.name,
                camera.addressLink,
                camera.groupId,
                camera.version,
                camera.createdAt,
                camera.updatedAt
            );
        },

        /**
         * Sets form visibility state
         * @param {boolean} visible - Whether the form should be visible
         */
        async setVisible(visible) {
            this.$state.visible = visible;
        },

        /**
         * Sets camera creation mode
         * @param {boolean} value - True if creating a new user
         */
        async setCreatingCamera(value) {
            this.$state.creatingCamera = value;
        },

        /**
         * Populates form fields from camera data
         * @param {CameraDTO} camera - User data object
         */
        async setCameraFields(camera) {
            this.$state.id = camera.id;
            this.$state.groupId = camera.groupId;
            this.$state.name = camera.name;
            this.$state.addressLink = camera.addressLink;
            this.$state.version = camera.version;
            this.$state.createdAt = camera.createdAt;
            this.$state.updatedAt = camera.updatedAt;
        },

        /**
         * Restores form fields from stored user data
         */
        restoreFields() {
            if (this.$state.camera) {
                this.$state.id = this.$state.camera.id;
                this.$state.groupId = this.$state.camera.groupId;
                this.$state.name = this.$state.camera.name;
                this.$state.addressLink = this.$state.camera.addressLink;
                this.$state.version = this.$state.camera.version;
                this.$state.createdAt = this.$state.camera.createdAt;
                this.$state.updatedAt = this.$state.camera.updatedAt;
            } else {
                this.clearData();
            }
        },

        /**
         * Clears all form data
         */
        clearData() {
            this.$state.id = null;
            this.$state.groupId = null;
            this.$state.name = "";
            this.$state.addressLink = "";
            this.$state.version = 0;
            this.$state.createdAt = null;
            this.$state.updatedAt = null;
            this.$state.user = null;
        },

        /**
         * Creates a new camera record
         * @param {string} token - Authentication token
         * @returns @returns {Promise<{token: string, status: number, message?: string}>} Response object with token, status and optional message
         */
        async createCameraRecord(token) {
            try {
                const camera = new CameraDTO(
                    this.$state.id,
                    this.$state.name,
                    this.$state.addressLink,
                    this.$state.groupId,
                    this.$state.version,
                    this.$state.createdAt,
                    this.$state.updatedAt
                );

                const response = await createCamera(token, this.$state.groupId, camera);

                if (response.status === 422) {
                    const unprocessResponse = await unprocessableEntity(response);
                    const unprocessResponseJson = await unprocessResponse.json();
                    return {
                        token: token,
                        status: response.status,
                        message: unprocessResponseJson.message
                    };
                }

                if (response.status === 401) {
                    return await logOutUser(response);
                }

                if (response.status === 503) {
                    return {token: token, status: 503, message: "Network Error"};
                }

                const responseJson = await response.json();
                if (response.ok) {
                    return {token: responseJson.token, status: response.status};
                }

                const details = responseJson.detail;
                return {
                    token: details.token,
                    status: response.status,
                    message: details.data.message
                };
            } catch (error) {
                console.error(error);
                return {token, status: 503, message: "Network Error"};
            }
        },

        /**
         * Updates an existing camera record
         * @param {string} token - Authentication token
         * @returns {Promise<{token: string, status: number, message?: string}>} Response object with token, status and optional message
         */
        async updateCameraRecord(token) {
            try {
                const camera = new CameraDTO(
                    this.$state.id,
                    this.$state.name,
                    this.$state.addressLink,
                    this.$state.groupId,
                    this.$state.version,
                    this.$state.createdAt,
                    this.$state.updatedAt
                );

                const response = await updateCameraById(token, this.$state.groupId, this.$state.id, camera);

                if (response.status === 422) {
                    const unprocessResponse = await unprocessableEntity(response);
                    const unprocessResponseJson = await unprocessResponse.json();
                    return {
                        token: token,
                        status: response.status,
                        message: unprocessResponseJson.message
                    };
                }

                if (response.status === 401) {
                    return await logOutUser(response);
                }

                if (response.status === 503) {
                    return {token: token, status: 503, message: "Network Error"};
                }

                const responseJson = await response.json();
                if (response.ok) {
                    return {token: responseJson.token, status: response.status};
                }

                const details = responseJson.detail;
                return {
                    token: details.token,
                    status: response.status,
                    message: details.data.message
                };
            } catch (error) {
                console.error(error);
                return {token, status: 503, message: "Network Error"};
            }
        }
    }
});