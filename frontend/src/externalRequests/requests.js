import {
    login,
    logout,
    getMyProfile
} from "@/externalRequests/endpoints.js";


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
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    })
}