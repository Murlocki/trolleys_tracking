import {
    login,
    logout,
    getMyProfile
} from "@/externalRequests/endpoints.js";
const apikey = import.meta.env.VITE_API_KEY;
console.log(apikey)

export async function loginUser(authForm) {
    return await fetch(login, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(authForm)
    })
}

export async function loginOut(token) {
    return await fetch(logout, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    })
}


export async function getUserProfile(token) {
    return await fetch(`${getMyProfile}`, {
        method: 'GET',
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            'X-API-Key': apikey
        }
    })
}