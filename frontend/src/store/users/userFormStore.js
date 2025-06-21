import {defineStore} from "pinia";
import {createUserRecord, getUserById, updateUserRecord} from "@/externalRequests/requests.js";
import {logOutUser, unprocessableEntity} from "@/validators/validators.js";
import {UserData, UserDTO} from "@/models/user/UserDTO.js";
import {UserCreate} from "@/models/user/UserCreate.js";
import {UserUpdate} from "@/models/user/UserUpdate.js";

/**
 * Pinia store for managing user form data and operations
 * @module stores/users/userFormStore
 */
export const userFormStore = defineStore("userFormStore", {
    state: () => ({
        /** @type {UserDTO|null} - Current user DTO instance */
        user: null,
        /** @type {number|null} - User ID */
        id: null,
        /** @type {string|null} - Username */
        username: null,
        /** @type {string|null} - Password (plaintext, temporary) */
        password: null,
        /** @type {string|null} - User's first name */
        firstName: null,
        /** @type {string|null} - User's last name */
        lastName: null,
        /** @type {string|null} - User's email address */
        email: null,
        /** @type {boolean} - Whether the user account is active */
        isActive: false,
        /** @type {string|null} - User's system role */
        role: null,
        /** @type {number} - Data version for optimistic concurrency */
        version: 0,
        /** @type {boolean} - Visibility state of the user form */
        visible: false,
        /** @type {boolean} - Flag indicating creation mode */
        creatingUser: false,
    }),

    actions: {
        /**
         * Sets the current user ID
         * @param {number} userId - The user ID to set
         */
        async setUserId(userId) {
            this.$state.id = userId;
        },

        /**
         * Fetches user data by ID
         * @param {string} token - Authentication token
         * @param {number} userId - ID of the user to fetch
         * @returns {Promise<{token: string, status: number, message?: string}>} Response object with token, status and optional message
         */
        async fetchUserData(token, userId) {
            try {
                const response = await getUserById(token, userId);

                if (response.status === 401) {
                    return await logOutUser(response);
                }

                if (response.status === 503) {
                    return {token: token, status: 503, message: "Network Error"};
                }

                const responseJson = await response.json();
                if (response.ok) {
                    await this.setUser(responseJson.data);
                    await this.setUserFields(this.$state.user);
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
         * Sets the current user object
         * @param {UserDTO} user - User data object
         */
        async setUser(user) {
            this.user = new UserDTO(
                user.id,
                user.username,
                user.userData,
                user.isActive,
                user.role,
                user.version
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
         * Sets user creation mode
         * @param {boolean} value - True if creating a new user
         */
        async setCreatingUser(value) {
            this.$state.creatingUser = value;
        },

        /**
         * Populates form fields from user data
         * @param {UserDTO} user - User data object
         */
        async setUserFields(user) {
            this.$state.id = user.id;
            this.$state.username = user.username;
            if (user.userData) {
                this.$state.firstName = user.userData.firstName;
                this.$state.lastName = user.userData.lastName;
                this.$state.email = user.userData.email;
            }
            this.$state.isActive = user.isActive;
            this.$state.role = user.role;
            this.$state.version = user.version;
        },

        /**
         * Restores form fields from stored user data
         */
        restoreFields() {
            if (this.$state.user) {
                this.$state.id = this.$state.user.id;
                this.$state.username = this.$state.user.username;
                this.$state.firstName = this.$state.user.firstName;
                this.$state.lastName = this.$state.user.lastName;
                this.$state.email = this.$state.user.email;
                this.$state.isActive = this.$state.user.isActive;
                this.$state.role = this.$state.user.role;
            } else {
                this.clearData();
            }
        },

        /**
         * Clears all form data
         */
        clearData() {
            this.$state.id = null;
            this.$state.username = "";
            this.$state.firstName = "";
            this.$state.lastName = "";
            this.$state.email = "";
            this.$state.isActive = false;
            this.$state.password = "";
            this.$state.role = "";
            this.$state.version = 0;
            this.$state.user = null;
        },

        /**
         * Creates a new user record
         * @param {string} token - Authentication token
         * @returns @returns {Promise<{token: string, status: number, message?: string}>} Response object with token, status and optional message
         */
        async createUserRecord(token) {
            try {
                const user = new UserCreate(
                    this.$state.username,
                    this.$state.password,
                    this.$state.role !== "service"
                        ? new UserData(
                            this.$state.firstName,
                            this.$state.lastName,
                            this.$state.email
                        )
                        : null,
                    this.$state.role
                );

                const response = await createUserRecord(token, user);

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
         * Updates an existing user record
         * @param {string} token - Authentication token
         * @returns {Promise<{token: string, status: number, message?: string}>} Response object with token, status and optional message
         */
        async updateUserRecord(token) {
            try {
                const user = new UserUpdate(
                    this.$state.username,
                    this.$state.role !== "service"
                        ? new UserData(
                            this.$state.firstName,
                            this.$state.lastName,
                            this.$state.email
                        )
                        : null,
                    this.$state.isActive,
                    this.$state.role,
                    this.$state.version
                );

                const response = await updateUserRecord(token, this.$state.id, user);

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