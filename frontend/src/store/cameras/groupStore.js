import {defineStore} from "pinia";
import {getUsers} from "@/externalRequests/requests.js";
import {UserAdminDTO} from "@/models/user/UserAdminDTO.js";
import {SessionDTO} from "@/models/SessionDTO.js";
import {CameraGroupDTO} from "@/models/CameraGroupDTO.js";

export const groupsStore = defineStore("groupsStore", {
    state: () => ({
        groups: [],
        params: {
            page: 0,
            count: 10,
            totalPages: 1
        }
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
                page: 1,
                count: 10,
                totalPages: 1
            }
        },
        setPaginator(page, pageSize, totalPages) {
            this.params.page = page;
            this.params.count = pageSize;
            this.params.totalPages = totalPages;
            console.log(`Page: ${this.page}, Page Size: ${this.pageSize}, Total Pages: ${this.totalPages}`);
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