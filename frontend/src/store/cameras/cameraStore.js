import {defineStore} from "pinia";
import {CameraDTO} from "@/models/CameraDTO.js";
import {deleteCameraById, getCamerasList, getCameraSubscribersList} from "@/externalRequests/requests.js";
import {logOutUser} from "@/validators/validators.js";

export const camerasStore = defineStore("camerasStore", {
    state: () => ({
        cameras: [],
        groupId: null,
        params: {
            page: 0,
            count: 10,
            totalPages: 1,
            id: "",
            name: "",
            addressLink: "",
            createdFrom: null,
            createdTo: null,
            updatedFrom: null,
            updatedTo: null,
            sortBy: {
                createdAt: "desc",
                updatedAt: null,
                id: null,
                name: null,
                addressLink: null,
            }
        }
    }),
    actions: {
        setGroupId(groupId) {
            this.groupId = groupId;
        },
        async fetchCameras(token, groupId) {
            try {
                if (!groupId) {
                    return;
                }
                const response = await getCamerasList(token, groupId, this.$state.params);

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
                    this.setCameras(responseJson.data.items);
                    this.setPaginator(
                        responseJson.data.page,
                        responseJson.data.itemsPerPage,
                        responseJson.data.pageCount
                    );
                    console.log(this.$state.cameras);
                    return {token: responseJson.token, status: response.status};
                }

                // Process rest of error statuses
                const details = responseJson.detail
                return {token: details.token, status: response.status, message: details.message};
            } catch (error) {
                return {token, status: 503, message: "Network Error"};
            }
        },
        setCameras(cameras) {
            this.cameras = cameras.map(camera => new CameraDTO(
                camera.id,
                camera.name,
                camera.addressLink,
                camera.groupId,
                camera.version,
                camera.createdAt,
                camera.updatedAt
            ));
            console.log(this.$state.cameras);
        },

        /**
         * Resets store to initial state
         */
        clearCameras() {
            this.cameras = [];
            this.params = {
                page: 0,
                count: 10,
                totalPages: 1,
                id: "",
                name: "",
                addressLink: "",
                createdFrom: null,
                createdTo: null,
                updatedFrom: null,
                updatedTo: null,
                sortBy: {
                    createdAt: "desc",
                    updatedAt: null,
                    id: null,
                    name: null,
                    addressLink: null,
                }
            }
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
            console.log(`Page: ${this.page}, Page Size: ${this.pageSize}, Total Pages: ${this.totalPages}`);
        },
        /**
         * Updates search filters
         * @param {Object} filters - New filter values
         */
        setFilters(filters) {
            this.params = {...this.params, ...filters};
        },

        /**
         * Deletes a user session by ID.
         * @param {string} token - JWT token.
         * @param {number} cameraId - Camera ID
         * @returns {Promise<{token: string, status: number, message?: string}>} - Response data.
         */
        async deleteCameraById(token, cameraId) {
            try {

                const response = await deleteCameraById(token, this.$state.groupId, cameraId);

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
        /** @returns {number} Total cameras count in current view */
        getCamerasCount: (state) => state.cameras.length,

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