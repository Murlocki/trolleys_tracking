import {defineStore} from "pinia";

/**
 * Pinia store for managing camera search forms
 * @module stores/cameras/cameraSearchFormStore
 */
export const groupSearchFormStore = defineStore("groupSearchFormStore", {
    state: () => ({
        /** @type {boolean} visible - Controls visibility of a search form */
        visible: false,
        /** @type {Object} params - Stores search parameters (filters, sorting etc.) */
        params: {},
    }),

    actions: {
        /**
         * Controls visibility of the search form
         * @param {boolean} value - Whether form should be visible
         */
        setVisible(value) {
            this.$state.visible = value;
        },
        /**
         * Updates search parameters
         * @param {Object} params - New search parameters
         */
        setParams(params) {
            this.$state.params = params;
        },

        /**
         * Clears all search parameters
         */
        clearData() {
            this.$state.params = {};
        },
    }
});