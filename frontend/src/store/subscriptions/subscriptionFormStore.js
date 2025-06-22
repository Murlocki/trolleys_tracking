import {defineStore} from "pinia";
import {createSubscription, getUsers} from "@/externalRequests/requests.js";
import {logOutUser, unprocessableEntity} from "@/validators/validators.js";
import {SubscriptionCreateDTO} from "@/models/subscription/SubscriptionCreateDTO.js";

/**
 * Pinia store for managing user form data and operations
 * @module stores/users/subscriptionFormStore
 */
export const subscriptionFormStore = defineStore("subscriptionFormStore", {
    state: () => ({
        /** @type {number|null} - User ID */
        userId: null,
        /** @type {number|null} - Camera ID */
        cameraId: null,
        /** @type {number|null} - Group ID */
        groupId: null,
        /** @type {boolean} - Flag indicating visible mode */
        visible: false,
        /** @type {Array} - User option list */
        usersOptions: []
    }),

    actions: {
        /**
         * Fetches users data by ID
         * @param {string} token - Authentication token
         * @returns {Promise<{token: string, status: number, message?: string}>} Response object with token, status and optional message
         */
        async fetchUsers(token) {
            try {
                const response = await getUsers(token, {count:0});

                if (response.status === 401) {
                    return await logOutUser(response);
                }

                if (response.status === 503) {
                    return {token: token, status: 503, message: "Network Error"};
                }

                const responseJson = await response.json();
                if (response.ok) {
                    this.$state.usersOptions = responseJson.data.items.map((user) =>{
                        return {
                            id: user.id,
                            name: user.username,
                        }
                    });
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
         * Sets form visibility state
         * @param {boolean} visible - Whether the form should be visible
         */
        async setVisible(visible) {
            this.$state.visible = visible;
        },
        /**
         * Sets form visibility state
         * @param {number} cameraId - Camera ID
         * @param {number} groupId - Group ID
         */
        async setCamera(cameraId, groupId) {
            this.$state.cameraId = cameraId;
            this.$state.groupId = groupId;
        },

        /**
         * Clears all form data
         */
        clearData() {
            this.$state.usersOptions = [];
            this.$state.userId = null;
            this.$state.cameraId = null;
        },

        /**
         * Creates a new subscription record
         * @param {string} token - Authentication token
         * @returns @returns {Promise<{token: string, status: number, message?: string}>} Response object with token, status and optional message
         */
        async createSubscriptionRecord(token) {
            try {
                const subscription = new SubscriptionCreateDTO(
                    this.$state.cameraId,
                    this.$state.userId,
                );

                const response = await createSubscription(token, this.groupId, this.cameraId, subscription);

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
    }
});