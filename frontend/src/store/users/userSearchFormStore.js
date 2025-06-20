import {defineStore} from "pinia";
import {
    createUserRecord,
    deleteUserById,
    getUserById,
    getUsers, updateUserPasswordRecord,
    updateUserRecord
} from "@/externalRequests/requests.js";
import {UserAdminDTO} from "@/models/user/UserAdminDTO.js";
import {SessionDTO} from "@/models/SessionDTO.js";
import {logOutUser, unprocessableEntity} from "@/validators/validators.js";
import {UserData, UserDTO} from "@/models/user/UserDTO.js";
import {UserCreate} from "@/models/user/UserCreate.js";
import {UserUpdate} from "@/models/user/UserUpdate.js";
import {PasswordDTO} from "@/models/user/PasswordDTO.js";

export const userSearchFormStore = defineStore("userSearchFormStore", {
    state: () => ({
        visible: false,
        params: {}
    }),
    actions: {
        setVisible(value) {
            this.$state.visible = value;
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
                    await this.setUserFields(responseJson.data);
                    return {token: responseJson.token, status: response.status};
                }
                const details = responseJson.detail
                return {token: details.token, status: response.status, message: details.message};
            } catch (error) {
                console.error(error);
                return {token, status: 503, message: "Network Error"};
            }
        },
        setParams(params) {
            this.$state.params = params;
        },
        clearData() {
            this.$state.params = {};
        },
        async updateUserPassword(token) {
            try {
                const userPasswordForm = new PasswordDTO(
                    this.$state.password,
                    this.$state.version
                );
                const response = await updateUserPasswordRecord(token, this.$state.id, userPasswordForm);
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