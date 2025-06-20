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

export async function unprocessableEntity(response) {
    if (response.status === 422) {
        const responseJson = await response.json();
        console.log(responseJson);
        const innerLength = responseJson.detail[0].loc.length;
        return new Response(JSON.stringify(
                {
                    error: "Incorrect form",
                    message: `${responseJson.detail[0].loc[innerLength-1]}: ${responseJson.detail[0].msg}`,
                }
            ), {
                status: 422,
            }
        );
    }
}