import {defineStore} from "pinia";
import {
    createUserRecord,
    deleteUserById,
    getUserById,
    getUsers,
    updateUserPasswordRecord,
    updateUserRecord
} from "@/externalRequests/requests.js";
import {UserAdminDTO} from "@/models/user/UserAdminDTO.js";
import {SessionDTO} from "@/models/SessionDTO.js";
import {logOutUser, unprocessableEntity} from "@/validators/validators.js";
import {UserData, UserDTO} from "@/models/user/UserDTO.js";
import {UserCreate} from "@/models/user/UserCreate.js";
import {UserUpdate} from "@/models/user/UserUpdate.js";
import {PasswordDTO} from "@/models/user/PasswordDTO.js";

/**
 * Pinia store for managing user password forms
 * @module stores/users/userPasswordFormStore
 */
export const userPasswordFormStore = defineStore("userPasswordFormStore", {
    state: () => ({
        /** @type {number || null} id - ID of the user being edited */
        id: null,
        /** @type {string || null} password - New password value */
        password: null,
        /** @type {number} version - Version for optimistic concurrency control */
        version: 0,
        /** @type {boolean} visible - Visibility state of the password form */
        visible: false,
    }),

    actions: {
        /**
         * Sets the user ID for password update
         * @param {number} userId - ID of the user
         */
        async setUserId(userId) {
            this.$state.id = userId;
        },

        /**
         * Fetches user data for password update form
         * @param {string} token - Authentication token
         * @param {number} userId - ID of the user
         * @returns {Promise<{token: string, status: number, message?: string}>}
         */
        async fetchUserData(token, userId) {
            try {
                const response = await getUserById(token, userId);

                // Handle unauthorized access
                if (response.status === 401) {
                    return await logOutUser(response);
                }

                // Handle network error
                if (response.status === 503) {
                    return {token: token, status: 503, message: "Network Error"};
                }

                // Process successful response
                const responseJson = await response.json();
                if (response.ok) {
                    await this.setUserFields(responseJson.data);
                    return {token: responseJson.token, status: response.status};
                }

                // Handle API errors
                const details = responseJson.detail;
                return {token: details.token, status: response.status, message: details.message};

            } catch (error) {
                console.error(error);
                return {token, status: 503, message: "Network Error"};
            }
        },

        /**
         * Controls visibility of the password form
         * @param {boolean} visible - Whether form should be visible
         */
        async setVisible(visible) {
            this.$state.visible = visible;
        },

        /**
         * Sets user fields for password update
         * @param {UserDTO} user - User data object
         */
        async setUserFields(user) {
            this.id = user.id;
            this.version = user.version;
        },

        /**
         * Clears all form data
         */
        clearData() {
            this.$state.id = null;
            this.$state.password = null;
            this.$state.version = 0;
        },

        /**
         * Updates user password
         * @param {string} token - Authentication token
         * @returns {Promise<{token: string, status: number, message?: string}>}
         */
        async updateUserPassword(token) {
            try {
                // Create password DTO for API request
                const userPasswordForm = new PasswordDTO(
                    this.$state.password,
                    this.$state.version
                );

                const response = await updateUserPasswordRecord(token, this.$state.id, userPasswordForm);

                // Handle validation errors
                if (response.status === 422) {
                    const unprocessResponse = await unprocessableEntity(response);
                    const unprocessResponseJson = await unprocessResponse.json();
                    return {
                        token: token,
                        status: response.status,
                        message: unprocessResponseJson.message
                    };
                }

                // Handle unauthorized access
                if (response.status === 401) {
                    return await logOutUser(response);
                }

                // Handle network error
                if (response.status === 503) {
                    return {token: token, status: 503, message: "Network Error"};
                }

                // Process successful response
                const responseJson = await response.json();
                if (response.ok) {
                    return {token: responseJson.token, status: response.status};
                }

                // Handle other API errors
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