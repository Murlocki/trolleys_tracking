import {defineStore} from "pinia";
import {deleteUserById, getUserById, getUsers} from "@/externalRequests/requests.js";
import {UserAdminDTO} from "@/models/UserAdminDTO.js";
import {SessionDTO} from "@/models/SessionDTO.js";
import {logOutUser} from "@/validators/accessValidators.js";
import {UserDTO} from "@/models/UserDTO.js";

export const userFormStore = defineStore("userFormStore", {
    state: () => ({
        user: null,
        id:null,
        username:"",
        password:"",
        firstName:"",
        lastName:"",
        email:"",
        isActive:false,
        role:"",
        version:0,
        visible: false,
        creatingUser: false,
    }),
    actions: {
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
                console.log(responseJson);
                if (response.ok) {
                    await this.setUser(responseJson.data);
                    console.log(this.$state.users);
                    return {token: responseJson.token, status: response.status};
                }
                const details = responseJson.detail
                return {token: details.token, status: response.status, message: details.message};
            } catch (error) {
                console.error(error);
                return {token, status: 503, message: "Network Error"};
            }
        },
        async setUser(user) {
            this.user = new UserDTO(
                user.id,
                user.username,
                user.userData,
                user.createdAt,
                user.updatedAt,
                user.isActive,
                user.role,
                user.roleDisplay,
                user.version,
            )

        },
        async setVisible(visible) {
            this.$state.visible = visible;
        },
        async setCreatingUser(value) {
            this.$state.creatingUser = value;
        },
        async setUserFields(user) {
            this.$state.id = user.id;
            this.$state.username = user.username;
            this.$state.firstName = user.firstName;
            this.$state.lastName = user.lastName;
            this.$state.email = user.email;
            this.$state.isActive = user.isActive;
            this.$state.role = user.role;
            this.$state.version = user.version;
        },
        restoreFields() {
            if(this.$state.user){
                this.$state.id = this.$state.user.id;
                this.$state.username = this.$state.user.username;
                this.$state.firstName = this.$state.user.firstName;
                this.$state.lastName = this.$state.user.lastName;
                this.$state.email = this.$state.user.email;
                this.$state.isActive = this.$state.user.isActive;
                this.$state.role = this.$state.user.role;
            }
            else {
                this.$state.id = null;
                this.$state.username = "";
                this.$state.firstName = "";
                this.$state.lastName = "";
                this.$state.email = "";
                this.$state.isActive = false;
                this.$state.role = "";
                this.$state.password = "";
            }
        },
        clearData(){
            this.$state.id = null;
            this.$state.username = "";
            this.$state.firstName = "";
            this.$state.lastName = "";
            this.$state.email = "";
            this.$state.isActive = false;
            this.$state.role = "";
            this.$state.version = 0;
            this.$state.user = null;
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