import {defineStore} from "pinia";
import {
    createUserRecord,
    deleteUserById,
    getUserById,
    getUsers,
    updateUserRecord
} from "@/externalRequests/requests.js";
import {UserAdminDTO} from "@/models/user/UserAdminDTO.js";
import {SessionDTO} from "@/models/SessionDTO.js";
import {logOutUser, unprocessableEntity} from "@/validators/validators.js";
import {UserData, UserDTO} from "@/models/user/UserDTO.js";
import {UserCreate} from "@/models/user/UserCreate.js";
import {UserUpdate} from "@/models/user/UserUpdate.js";

export const userFormStore = defineStore("userFormStore", {
    state: () => ({
        user: null,
        id: null,
        username: null,
        password: null,
        firstName: null,
        lastName: null,
        email: null,
        isActive: false,
        role: null,
        version: 0,
        visible: false,
        creatingUser: false,
    }),
    actions: {
        async setUserId(userId){
            this.$state.id = userId;
        },
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
                    console.log(this.$state.user);
                    await this.setUserFields(this.$state.user);
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
                user.isActive,
                user.role,
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
            if(user.userData) {
                this.$state.firstName = user.userData.firstName;
                this.$state.lastName = user.userData.lastName;
                this.$state.email = user.userData.email;
            }
            this.$state.isActive = user.isActive;
            this.$state.role = user.role;
            this.$state.version = user.version;
        },
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
                this.clearData()
            }
        },
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
        async createUserRecord(token) {
            try {
                const user = new UserCreate(
                    this.$state.username,
                    this.$state.password,
                    this.$state.role !== "service" ? new UserData(
                        this.$state.firstName,
                        this.$state.lastName,
                        this.$state.email,
                    ) : null,
                    this.$state.role,
                );
                const response = await createUserRecord(token, user);
                console.log(response);
                //Handle incorrect form data
                if (response.status === 422) {
                    const unprocessResponse = await unprocessableEntity(response);
                    const unprocessResponseJson = await unprocessResponse.json();
                    return {token: token, status: response.status, message: unprocessResponseJson.message};
                }

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
        async updateUserRecord(token) {
            try {
                const user = new UserUpdate(
                    this.$state.username,
                    this.$state.role !== "service" ? new UserData(
                        this.$state.firstName,
                        this.$state.lastName,
                        this.$state.email,
                    ) : null,
                    this.$state.isActive,
                    this.$state.role,
                    this.$state.version,
                );
                const response = await updateUserRecord(token, this.$state.id, user);
                console.log(response);
                //Handle incorrect form data
                if (response.status === 422) {
                    const unprocessResponse = await unprocessableEntity(response);
                    const unprocessResponseJson = await unprocessResponse.json();
                    return {token: token, status: response.status, message: unprocessResponseJson.message};
                }

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

        }

    }
})