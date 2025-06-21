import { defineStore } from "pinia";
import { deleteUserById, getUsers } from "@/externalRequests/requests.js";
import { UserAdminDTO } from "@/models/user/UserAdminDTO.js";
import { logOutUser } from "@/validators/validators.js";

/**
 * Pinia store for managing users data
 * @module stores/users/usersStore
 */
export const usersStore = defineStore("usersStore", {
    state: () => ({
        /** @type {Array[UserAdminDTO]} users - Array of UserAdminDTO objects */
        users: [],
        /** @type {Object} params - Dictionary of all search and pagination parameters */
        params: {
            /** @type {number} page - Current page (0-based index) */
            page: 0,
            /** @type {number} count - Items per page */
            count: 10,
            /** @type {number} totalPages - Total available pages */
            totalPages: 1,

            // Filter fields
            /** @type {string} id - User ID filter */
            id: "",
            /** @type {string} username - User username filter */
            username: "",
            /** @type {string} firstName - User first name filter */
            firstName: "",
            /** @type {string} lastName - User last name filter */
            lastName: "",
            /** @type {string} email - User email filter */
            email: "",
            /** @type {boolean || null} isActive - User activity filter */
            isActive: null,
            /** @type {Date || null} createdFrom - User createdFrom filter */
            createdFrom: null,
            /** @type {Date || null} createdTo - User createdTo filter */
            createdTo: null,
            /** @type {Date || null} updatedFrom - User updatedFrom filter */
            updatedFrom: null,
            /** @type {Date || null} updatedTo - User updatedTo filter */
            updatedTo: null,
            /** @type {Array[string]} role - Array of roles filter */
            role: [],

            // Sorting configuration
            sortBy: {
                /** @type {string || null} id - User id sort */
                id: null,
                /** @type {string || null} email - User email sort */
                email: null,
                /** @type {string || null} username - User username sort */
                username: null,
                /** @type {string || null} firstName - User first name sort */
                firstName: null,
                /** @type {string || null} lastName - User last name sort */
                lastName: null,
                /** @type {string || null} role - User role sort */
                role: null,
                /** @type {string || null} isActive - User activity sort */
                isActive: null,
                /** @type {string || null} createdAt - User created at sort */
                createdAt: "desc", // Default sort
                /** @type {string || null} updatedAt - User updatedAt sort */
                updatedAt: null,
            }
        },
    }),

    actions: {
        /**
         * Fetches users from API with current params
         * @param {string} token - Authentication token
         * @returns {Promise<{token: string, status: number, message?: string}>}
         */
        async fetchUsers(token) {
            try {
                const response = await getUsers(token, this.params);

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
                    await this.setUsers(responseJson.data.items);
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
         * Deletes user by ID
         * @param {string} token - Authentication token
         * @param {number} userId - User ID to delete
         * @returns {Promise<{token: string, status: number, message?: string}>}
         */
        async deleteUserRecordById(token, userId) {
            try {
                const response = await deleteUserById(token, userId);

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

        /**
         * Transforms and sets users array
         * @param {Array} users - Raw users data from API
         */
        async setUsers(users) {
            this.users = users.map(user => new UserAdminDTO(
                user.id,
                user.username,
                user.userData?.firstName,
                user.userData?.lastName,
                user.userData?.email,
                user.createdAt,
                user.updatedAt,
                user.isActive,
                user.role,
                user.roleDisplay,
                user.version
            ));
        },

        /**
         * Resets store to initial state
         */
        clearUsers() {
            this.users = [];
            this.params = {
                page: 0,
                count: 10,
                totalPages: 1,
                id: "",
                username: "",
                firstName: "",
                lastName: "",
                email: "",
                isActive: null,
                createdFrom: null,
                createdTo: null,
                updatedFrom: null,
                updatedTo: null,
                role: "",
                sortBy: {
                    createdAt: "desc",
                    updatedAt: null,
                    id: null,
                    username: null,
                    firstName: null,
                    lastName: null,
                    email: null,
                    role: null,
                    isActive: null,
                }
            };
        },

        /**
         * Updates pagination parameters
         * @param {number} page - Current page (0-based)
         * @param {number} pageSize - Items per page
         * @param {number} totalPages - Total available pages
         */
        setPaginator(page, pageSize, totalPages) {
            this.params.page = page;
            this.params.count = pageSize;
            this.params.totalPages = totalPages;
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
        /** @returns {number} Total users count in current view */
        getUsersCount: (state) => state.users.length,

        /** @returns {string} Current user's name if available */
        getCurrentUserName: (state) => state.currentUser?.name || '',

        /** @returns {number} Current page number (0-based) */
        page: (state) => state.params.page,

        /** @returns {number} Total available pages */
        totalPages: (state) => state.params.totalPages,

        /** @returns {number} Items per page */
        pageSize: (state) => state.params.count,

        /** @returns {number} Estimated total records */
        totalRecords: (state) => state.params.totalPages * state.params.count,
    }
});