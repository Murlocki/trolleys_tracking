import {defineStore} from "pinia";
import {getUsers, getUserSessionList} from "@/externalRequests/requests.js";
import {UserAdminDTO} from "@/models/UserAdminDTO.js";
import {SessionDTO} from "@/models/SessionDTO.js";
import router from "@/router/index.js";
import {logOutUser, processUnauthorized} from "@/validators/accessValidators.js";

export const  sessionsStore = defineStore("sessionsStore", {
    state: () => ({
        sessions: [],
        userId: null,
    }),
    actions: {
        async fetchSessions(token, userId) {
            const response = await getUserSessionList(token, userId);
            if (response.status === 401) {
                return await logOutUser(response);
            }

            if (response.status === 503) {
                return {token: token, status:503, message: "Network Error"};
            }

            const responseJson = await response.json();
            if (response.ok){
                await this.setUserSessions(responseJson.data, userId);
                console.log(this.$state.sessions);
                return {token: responseJson.token, status: response.status};
            }
            const details = responseJson.detail
            console.log(responseJson)
            return {token: details.token, status: response.status, message: details.message};
        },


        async setUserSessions(sessions) {
            this.$state.sessions = await sessions.map(session => new SessionDTO(
                session.sessionId,
                session.userId,
                session.accessToken,
                session.refreshToken,
                session.device,
                session.ipAddress,
                session.createdAt,
                session.expiresAt
            ));
            console.log(this.$state.sessions);
        },
        async deleteUserSession() {
            this.$state.userId = null
            this.$state.sessions=[]
        },

        async setUserId(userId) {
            this.$state.userId = userId;
            console.log(this.$state.userId);
        }
    }
})