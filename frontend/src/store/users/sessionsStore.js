import {defineStore} from "pinia";
import {deleteUserSession, getUsers, getUserSessionList} from "@/externalRequests/requests.js";
import {UserAdminDTO} from "@/models/user/UserAdminDTO.js";
import {SessionDTO} from "@/models/SessionDTO.js";
import router from "@/router/index.js";
import {logOutUser, processUnauthorized} from "@/validators/validators.js";

export const sessionsStore = defineStore("sessionsStore", {
    state: () => ({
        /** @type {Array[SessionDTO]} sessions - List of sessions data */
        sessions: [],
        /** @type {number || null} userId - Sessions owner ID */
        userId: null,
    }),
    actions: {
        /**
         * Fetches user sessions from the server.
         * @param {string} token - JWT token for authentication.
         * @param {number} userId - ID of the user whose sessions are fetched.
         * @returns {Promise<{token: string, status: number, message?: string}>} - Response data.
         */
        async fetchSessions(token, userId) {
            try {
                if (!userId) {
                    return;
                }
                const response = await getUserSessionList(token, userId);

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
                    await this.setUserSessions(responseJson.data, userId);
                    console.log(this.$state.sessions);
                    return {token: responseJson.token, status: response.status};
                }

                // Process rest of error statuses
                const details = responseJson.detail
                return {token: details.token, status: response.status, message: details.message};
            } catch (error) {
                return {token, status: 503, message: "Network Error"};
            }
        },

        /**
         * Deletes a user session by ID.
         * @param {string} token - JWT token.
         * @param {number} userId - User ID.
         * @param {string} sessionId - Session ID to delete.
         * @returns {Promise<{token: string, status: number, message?: string}>} - Response data.
         */
        async deleteUserSessionById(token, userId, sessionId) {
            try {

                const response = await deleteUserSession(token, userId, sessionId);

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
        /**
         * Updates the store with fetched sessions.
         * @param {Array} sessions - Raw session data from the API.
         */
        async setUserSessions(sessions) {
            this.$state.sessions = sessions.map(session => new SessionDTO(
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

        /** Clears all sessions and resets userId. */
        async clearUserSessions() {
            this.$state.sessions = []
        },

        /** Sets the current user ID. */
        async setUserId(userId) {
            this.$state.userId = userId;
            console.log(this.$state.userId);
        }
    }
})