import {defineStore} from "pinia";
import {deleteGroup, getCameraGroupsList} from "@/externalRequests/requests.js";
import {CameraGroupDTO} from "@/models/CameraGroupDTO.js";
import {logOutUser} from "@/validators/validators.js";

export const groupsStore = defineStore("groupsStore", {
    state: () => ({
        groups: [],
        params: {
            page: 0,
            count: 10,
            totalPages: 1,
            // Filter fields
            /** @type {string} id - Group ID filter */
            id: "",
            /** @type {string} address - Group address filter */
            address: "",
            /** @type {string} name - Group name filter */
            name: "",
            /** @type {string} description - Group description filter */
            description: "",
            /** @type {Date || null} createdFrom - User createdFrom filter */
            createdFrom: null,
            /** @type {Date || null} createdTo - User createdTo filter */
            createdTo: null,
            /** @type {Date || null} updatedFrom - User updatedFrom filter */
            updatedFrom: null,
            /** @type {Date || null} updatedTo - User updatedTo filter */
            updatedTo: null,

            // Sorting configuration
            sortBy: {
                id: null,
                name: null,
                address: null,
                description: null,
                /** @type {string || null} createdAt - User created at sort */
                createdAt: "desc", // Default sort
                /** @type {string || null} updatedAt - User updatedAt sort */
                updatedAt: null,
            }
        }
    }),
    actions: {
        /**
         * Fetches users from API with current params
         * @param {string} token - Authentication token
         * @returns {Promise<{token: string, status: number, message?: string}>}
         */
        async fetchGroups(token) {
            try {
                const response = await getCameraGroupsList(token, this.params);

                // Handle unauthorized access
                if (response.status === 401) {
                    return await logOutUser(response);
                }

                // Handle network error
                if (response.status === 503) {
                    return { token: token, status: 503, message: "Network Error" };
                }

                const responseJson = await response.json();

                // Process successful response
                if (response.ok) {
                    await this.setGroups(responseJson.data.items);
                    await this.setPaginator(
                        responseJson.data.page,
                        responseJson.data.itemsPerPage,
                        responseJson.data.pageCount
                    );
                    return { token: responseJson.token, status: response.status };
                }

                // Handle API errors
                const details = responseJson.detail;
                return {
                    token: details.token,
                    status: response.status,
                    message: details.data.message
                };

            } catch (error) {
                console.error("Users fetch error:", error);
                return { token, status: 503, message: "Network Error" };
            }
        },
        /**
         * Deletes Group by ID
         * @param {string} token - Authentication token
         * @param {number} groupId - Group ID to delete
         * @returns {Promise<{token: string, status: number, message?: string}>}
         */
        async deleteGroupById(token, groupId) {
            try {
                const response = await deleteGroup(token, groupId);

                // Handle unauthorized access
                if (response.status === 401) {
                    return await logOutUser(response);
                }

                // Handle network error
                if (response.status === 503) {
                    return { token: token, status: 503, message: "Network Error" };
                }

                const responseJson = await response.json();

                // Process successful response
                if (response.ok) {
                    return { token: responseJson.token, status: response.status };
                }

                // Handle API errors
                const details = responseJson.detail;
                return {
                    token: details.token,
                    status: response.status,
                    message: details.data.message
                };

            } catch (error) {
                console.error("User deletion error:", error);
                return { token, status: 503, message: "Network Error" };
            }
        },

        async setGroups(groups) {
            this.groups = groups.map(group => new CameraGroupDTO(
                group.id,
                group.name,
                group.address,
                group.description,
                group.version,
                group.createdAt,
                group.updatedAt
            ));
            console.log(this.$state.groups);
        },
        clearGroups() {
            this.groups = [];
            this.params = {
                page: 0,
                count: 10,
                totalPages: 1,
                id: "",
                address: "",
                name: "",
                description: "",
                createdFrom: null,
                createdTo: null,
                updatedFrom: null,
                updatedTo: null,

                // Sorting configuration
                sortBy: {
                    id: null,
                    name: null,
                    address: null,
                    description: null,
                    createdAt: "desc", // Default sort
                    updatedAt: null,
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
        }
    },
    getters: {
        /** @returns {number} Total group count in current view */
        getGroupsCount: (state) => state.groups.length,

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