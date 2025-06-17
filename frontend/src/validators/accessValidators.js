import router from "@/router/index.js";
import {userSettingsStore} from "@/store/userSettingsStore.js";

let _userSettings = null;

const getUserSettings = () => {
    if (!_userSettings) {
        _userSettings = userSettingsStore();
    }
    return _userSettings;
};

export async function logOutUser(response) {
    if (response.status === 401) {
        await router.push("/");
        getUserSettings().clearJwt();
    }
    return response;
}

export async function processUnauthorized(response) {
    return response;
}