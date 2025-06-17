import {defineStore} from "pinia";
import {deleteUserById, getUsers} from "@/externalRequests/requests.js";
import {UserAdminDTO} from "@/models/UserAdminDTO.js";
import {SessionDTO} from "@/models/SessionDTO.js";
import {logOutUser} from "@/validators/accessValidators.js";

export const usersStore = defineStore("usersStore", {
    state: () => ({
        users: [],
        params: {page: 0, count: 10, totalPages: 1},
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
                    await this.setPaginator(responseJson.data.page, responseJson.data.itemsPerPage,responseJson.data.pageCount);
                    return {token: responseJson.token, status: response.status};
                }
                const details = responseJson.detail
                return {token: details.token, status: response.status, message: details.message};
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
                return {token: details.token, status: response.status, message: details.message};
            } catch (error) {
                console.error(error);
                return {token, status: 503, message: "Network Error"};
            }
        },
        async setUsers(users) {
            this.users = users.map(user => new UserAdminDTO(
                user.id,
                user.username,
                user.firstName,
                user.lastName,
                user.email,
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
            this.params = {page: 0, count: 10, totalPages: 1}
        },
        setPaginator(page, pageSize, totalPages) {
            this.params.page = page;
            this.params.count = pageSize;
            this.params.totalPages = totalPages;
            console.log(`Page: ${this.page}, Page Size: ${this.pageSize}, Total Pages: ${this.totalPages}, Total Records: ${this.totalRecords}`);
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