import {defineStore} from "pinia";
import {SubscriptionDTO} from "@/models/SubscriptionDTO.js";

export const  subscriptionStore = defineStore("subscriptionStore", {
    state: () => ({
        subscriptions: [],
        page: 1,
        pageSize: 10,
        totalPages: 1
    }),
    actions: {
        async setSubscriptions(subscriptions) {
            this.subscriptions = subscriptions.map(subscription => new SubscriptionDTO(
                subscription.id,
                subscription.cameraId,
                subscription.cameraName,
                subscription.userId,
                subscription.userName,
                subscription.createdAt,
                subscription.updatedAt
            ));
            console.log(this.$state.subscriptions);
        },
        clearSubscriptions() {
            this.subscriptions = [];
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