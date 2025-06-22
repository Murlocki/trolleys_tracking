import {defineStore} from "pinia";
import {SubscriptionDTO} from "@/models/subscription/SubscriptionDTO.js";
import {deleteSubscriptionById, getCameraSubscribersList} from "@/externalRequests/requests.js";
import {logOutUser} from "@/validators/validators.js";

export const subscriptionStore = defineStore("subscriptionStore", {
    state: () => ({
        subscriptions: [],
        cameraId: null,
        groupId: null,
        params: {
            page: 0,
            count: 10,
            totalPages: 1,
            id: "",
            username: "",
            createdFrom: null,
            createdTo: null,
            updatedFrom: null,
            updatedTo: null,
            sortBy: {
                createdAt: "desc",
                updatedAt: null,
                id: null,
                username: null,
            }
        }
    }),
    actions: {
        async fetchSubscriptions(token, groupId, cameraId) {
            try {
                if (!groupId || !cameraId) {
                    return;
                }
                const response = await getCameraSubscribersList(token, groupId, cameraId, this.$state.params);

                // Handle unauthorized access
                if (response.status === 401) {
                    return await logOutUser(response);
                }

                // Handle network errors
                if (response.status === 503) {
                    return {token: token, status: 503, message: "Network Error"};
                }

                // Process successful response
                const responseJson = await response.json();
                if (response.ok) {
                    this.setSubscriptions(responseJson.data.items);
                    this.setPaginator(
                        responseJson.data.page,
                        responseJson.data.itemsPerPage,
                        responseJson.data.pageCount
                    );
                    console.log(this.$state.subscriptions);
                    return {token: responseJson.token, status: response.status};
                }

                // Process rest of error statuses
                const details = responseJson.detail
                return {token: details.token, status: response.status, message: details.message};
            } catch (error) {
                return {token, status: 503, message: "Network Error"};
            }
        },
        setSubscriptions(subscriptions) {
            this.subscriptions = subscriptions.map(subscription => new SubscriptionDTO(
                subscription.id,
                subscription.cameraId,
                subscription.cameraName,
                subscription.userId,
                subscription.userName,
                subscription.createdAt,
                subscription.updatedAt
            ));
            console.log(this.$state.subscriptions);
        },
        setCamera(camera) {
            this.$state.groupId = camera.groupId;
            this.$state.cameraId = camera.id;
            console.log(`${this.$state.cameraId} ${this.$state.groupId}`);
        },
        clearSubscriptions() {
            this.subscriptions = [];
            this.params = {
                page: 0,
                count: 10,
                totalPages: 1,
                id: "",
                username: "",
                createdFrom: null,
                createdTo: null,
                updatedFrom: null,
                updatedTo: null,
                sortBy: {
                    createdAt: "desc",
                    updatedAt: null,
                    id: null,
                    username: null,
                }
            }
        },
        setPaginator(page, pageSize, totalPages) {
            this.params.page = page;
            this.params.count = pageSize;
            this.params.totalPages = totalPages;
            console.log(`Page: ${this.page}, Page Size: ${this.pageSize}, Total Pages: ${this.totalPages}`);
        },
        /**
         * Updates search filters
         * @param {Object} filters - New filter values
         */
        setFilters(filters) {
            this.params = { ...this.params, ...filters };
        },
        /**
         * Deletes a user session by ID.
         * @param {string} token - JWT token.
         * @param {number} subscriptionId - Subscription ID
         * @returns {Promise<{token: string, status: number, message?: string}>} - Response data.
         */
        async deleteSubscriptionById(token, subscriptionId) {
            try {

                const response = await deleteSubscriptionById(token, this.$state.groupId, this.$state.cameraId, subscriptionId);

                // Handle unauthorized access
                if (response.status === 401) {
                    return await logOutUser(response);
                }

                // Handle network error
                if (response.status === 503) {
                    return {token: token, status: 503, message: "Network Error"};
                }

                // Handle success request
                const responseJson = await response.json();
                if (response.ok) {
                    return {token: responseJson.token, status: response.status};
                }

                // Handle other errors
                const details = responseJson.detail
                console.log(responseJson)
                return {token: details.token, status: response.status, message: details.message};
            } catch (error) {
                return {token, status: 503, message: "Network Error"};
            }
        },
    },
    getters: {
        /** @returns {number} Total users count in current view */
        getSubscriptionsCount: (state) => state.subscriptions.length,

        /** @returns {number} Current page number (0-based) */
        page: (state) => state.params.page,

        /** @returns {number} Total available pages */
        totalPages: (state) => state.params.totalPages,

        /** @returns {number} Items per page */
        pageSize: (state) => state.params.count,

        /** @returns {number} Estimated total records */
        totalRecords: (state) => state.params.totalPages * state.params.count,
    }
})