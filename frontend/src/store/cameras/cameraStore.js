import {defineStore} from "pinia";
import {CameraDTO} from "@/models/CameraDTO.js";

export const  camerasStore = defineStore("camerasStore", {
    state: () => ({
        cameras: [],
        page: 1,
        pageSize: 10,
        totalPages: 1
    }),
    actions: {
        async setCameras(cameras) {
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
        clearCameras() {
            this.cameras = [];
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