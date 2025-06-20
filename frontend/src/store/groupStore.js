import {defineStore} from "pinia";
import {getUsers} from "@/externalRequests/requests.js";
import {UserAdminDTO} from "@/models/user/UserAdminDTO.js";
import {SessionDTO} from "@/models/SessionDTO.js";
import {CameraGroupDTO} from "@/models/CameraGroupDTO.js";

export const  groupsStore = defineStore("groupsStore", {
    state: () => ({
        groups: [],
        page: 1,
        pageSize: 10,
        totalPages: 1
    }),
    actions: {
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
    }
})