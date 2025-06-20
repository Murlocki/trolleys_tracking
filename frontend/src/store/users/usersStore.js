import {defineStore} from "pinia";
import {deleteUserById, getUsers} from "@/externalRequests/requests.js";
import {UserAdminDTO} from "@/models/user/UserAdminDTO.js";
import {SessionDTO} from "@/models/SessionDTO.js";
import {logOutUser} from "@/validators/validators.js";

export const usersStore = defineStore("usersStore", {
    state: () => ({
        users: [],
        params: {
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
            role: [],
            sortBy: {
                id: null,
                email:null,
                username: null,
                firstName: null,
                lastName: null,
                role: null,
                isActive: null,
                createdAt: "desc",
                updatedAt: null,
            }
        },
    }),
    actions: {
        async fetchUsers(token) {
            try {
                const response = await getUsers(token, this.$state.params);
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
                console.log(responseJson);
                if (response.ok) {
                    await this.setUsers(responseJson.data.items);
                    console.log(this.$state.users);
                    await this.setPaginator(responseJson.data.page, responseJson.data.itemsPerPage, responseJson.data.pageCount);
                    return {token: responseJson.token, status: response.status};
                }
                const details = responseJson.detail
                return {token: details.token, status: response.status, message: details.data.message};
            } catch (error) {
                console.error(error);
                return {token, status: 503, message: "Network Error"};
            }
        },
        async deleteUserRecordById(token, userId) {
            try {
                const response = await deleteUserById(token, userId);
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
                console.log(responseJson);
                if (response.ok) {
                    return {token: responseJson.token, status: response.status};
                }
                const details = responseJson.detail
                return {token: details.token, status: response.status, message: details.data.message};
            } catch (error) {
                console.error(error);
                return {token, status: 503, message: "Network Error"};
            }
        },
        async setUsers(users) {
            this.users = users.map(user => new UserAdminDTO(
                user.id,
                user.username,
                user.userData ? user.userData.firstName : null,
                user.userData ? user.userData.lastName : null,
                user.userData ? user.userData.email : null,
                user.createdAt,
                user.updatedAt,
                user.isActive,
                user.role,
                user.roleDisplay,
                user.version
            ));
            console.log(this.$state.users);
        },
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
            }
        },
        setPaginator(page, pageSize, totalPages) {
            this.params.page = page;
            this.params.count = pageSize;
            this.params.totalPages = totalPages;
            console.log(`Page: ${this.page}, Page Size: ${this.pageSize}, Total Pages: ${this.totalPages}, Total Records: ${this.totalRecords}`);
        },
        setFilters(filters) {
            this.params = {...this.params, ...filters};
            console.log(this.$state.params);
        }
    },
    getters: {
        getUsersCount: (state) => state.users.length,
        getCurrentUserName: (state) => state.currentUser ? state.currentUser.name : '',
        page: (state) => state.params.page,
        totalPages: (state) => state.params.totalPages,
        pageSize: (state) => state.params.count,
        totalRecords: (state) => state.params.totalPages * state.params.count,
    }
})