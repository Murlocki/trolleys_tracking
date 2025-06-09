import {defineStore} from "pinia";
import {getUsers} from "@/externalRequests/requests.js";
import {UserAdminDTO} from "@/models/UserAdminDTO.js";
import {SessionDTO} from "@/models/SessionDTO.js";

export const  usersStore = defineStore("usersStore", {
    state: () => ({
        users: [],
        page: 1,
        pageSize: 10,
        totalPages: 1,
        userSessions: {},
    }),
    actions: {
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
            this.$state.users.forEach(user => {
                this.$state.userSessions[user.id] = []
            })
            console.log(this.$state.users);
            console.log(this.$state.userSessions);
        },
        async setUserSessions(sessions, userId) {
            const userSession = this.$state.userSessions[userId];
            this.$state.userSessions[userId] = sessions.map(session => new SessionDTO(
                session.sessionId,
                session.userId,
                session.accessToken,
                session.refreshToken,
                session.device,
                session.ipAddress,
                session.createdAt,
                session.expiresAt
            ));
            console.log(this.$state.userSessions);
        },
        async deleteUserSession(userId) {
            this.$state.userSessions[userId]=[]
        },
        clearUsers() {
            this.users = [];
            this.page = 1;
            this.pageSize = 10;
            this.totalPages = 1;
        },
        setPaginator(page, pageSize, totalPages) {
            this.page = page;
            this.pageSize = pageSize;
            this.totalPages = totalPages;
            console.log(`Page: ${this.page}, Page Size: ${this.pageSize}, Total Pages: ${this.totalPages}`);
        }
    },
    getters: {
        getUsersCount: (state) => state.users.length,
        getCurrentUserName: (state) => state.currentUser ? state.currentUser.name : ''
    }
})