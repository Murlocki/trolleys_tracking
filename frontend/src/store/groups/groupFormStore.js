import {defineStore} from "pinia";
import {
    createCamera, createGroup,
    createUserRecord,
    getCameraById, getGroupById,
    getUserById, updateCameraById, updateGroup,
    updateUserRecord
} from "@/externalRequests/requests.js";
import {logOutUser, unprocessableEntity} from "@/validators/validators.js";
import {UserData, UserDTO} from "@/models/user/UserDTO.js";
import {UserCreate} from "@/models/user/UserCreate.js";
import {UserUpdate} from "@/models/user/UserUpdate.js";
import {CameraDTO} from "@/models/CameraDTO.js";
import {CameraGroupDTO} from "@/models/CameraGroupDTO.js";

/**
 * Pinia store for managing user form data and operations
 * @module stores/cameras/cameraFormStore
 */
export const groupFormStore = defineStore("groupFormStore", {
    state: () => ({
        group: null,
        id: null,
        name: "",
        address: "",
        description: "",
        version: 0,
        visible: false,
        creatingGroup: false,
    }),

    actions: {
        /**
         * Sets the current group's ID
         * @param {number} groupId - The group ID to set
         */
        async setGroupId(groupId) {
            this.$state.id = groupId;
        },

        /**
         * Fetches group data by ID
         * @param {string} token - Authentication token
         * @param {number} groupId - ID of camera's group
         * @returns {Promise<{token: string, status: number, message?: string}>} Response object with token, status and optional message
         */
        async fetchGroupData(token, groupId) {
            try {
                const response = await getGroupById(token, groupId);

                if (response.status === 401) {
                    return await logOutUser(response);
                }

                if (response.status === 503) {
                    return {token: token, status: 503, message: "Network Error"};
                }

                const responseJson = await response.json();
                if (response.ok) {
                    await this.setGroup(responseJson.data);
                    await this.setGroupFields(this.$state.group);
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
         * Sets the current group object
         * @param {CameraGroupDTO} group - Group data object
         */
        async setGroup(group) {
            this.group = new CameraGroupDTO(
                group.id,
                group.name,
                group.address,
                group.description,
                group.version,
                group.createdAt,
                group.updatedAt
            );
        },

        /**
         * Sets form visibility state
         * @param {boolean} visible - Whether the form should be visible
         */
        setVisible(visible) {
            this.$state.visible = visible;
        },

        /**
         * Sets camera creation mode
         * @param {boolean} value - True if creating a new user
         */
        setCreatingGroup(value) {
            this.$state.creatingGroup = value;
        },

        /**
         * Populates form fields from group data
         * @param {CameraGroupDTO} group - Group data object
         */
        async setGroupFields(group) {
            this.$state.id = group.id;
            this.$state.name = group.name;
            this.$state.description = group.description;
            this.$state.address = group.address;
            this.$state.version = group.version;
            this.$state.createdAt = group.createdAt;
            this.$state.updatedAt = group.updatedAt;
        },

        /**
         * Restores form fields from stored user data
         */
        restoreFields() {
            if (this.$state.group) {
                this.$state.id = this.$state.group.id;
                this.$state.name = this.$state.group.name;
                this.$state.description = this.$state.group.description;
                this.$state.address = this.$state.group.address;
                this.$state.version = this.$state.group.version;
                this.$state.createdAt = this.$state.group.createdAt;
                this.$state.updatedAt = this.$state.group.updatedAt;
            } else {
                this.clearData();
            }
        },

        /**
         * Clears all form data
         */
        clearData() {
            this.$state.id = null;
            this.$state.name = "";
            this.$state.description = "";
            this.$state.address = "";
            this.$state.version = 0;
            this.$state.createdAt = null;
            this.$state.updatedAt = null;
            this.$state.group = null;
        },

        /**
         * Creates a new group record
         * @param {string} token - Authentication token
         * @returns @returns {Promise<{token: string, status: number, message?: string}>} Response object with token, status and optional message
         */
        async createGroupRecord(token) {
            try {
                const group = new CameraGroupDTO(
                    this.$state.id,
                    this.$state.name,
                    this.$state.address,
                    this.$state.description,
                    this.$state.version,
                    this.$state.createdAt,
                    this.$state.updatedAt
                );

                const response = await createGroup(token, group);

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
        async updateGroupRecord(token) {
            try {
                const group = new CameraGroupDTO(
                    this.$state.id,
                    this.$state.name,
                    this.$state.address,
                    this.$state.description,
                    this.$state.version,
                    this.$state.createdAt,
                    this.$state.updatedAt
                );

                const response = await updateGroup(token, this.$state.id, group);

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