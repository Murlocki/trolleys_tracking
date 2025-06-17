import {
    deleteUserSessionById,
    getCameraGroups,
    getCameraOfGroup,
    getCameraSubscriptions,
    getMyProfile,
    getUserSessions,
    getUsersList,
    login,
    logout
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
    try {
        // Возвращаем полный объект Response для гибкой обработки в компоненте
        return await fetch(`${getMyProfile}`, {
            method: 'GET',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            }
        });

    } catch (error) {
        // Создаём искусственный Response для сетевых ошибок
        return new Response(JSON.stringify({
            error: "Network request failed",
            message: error.message
        }), {
            status: 503,
            statusText: "Network Error"
        });
    }
}

export async function getUserSessionList(token, id) {
    try {
        return await fetch(`${getUserSessions}/${id}`, {
            method: 'GET',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            }
        })
    } catch (error) {
        // Создаём искусственный Response для сетевых ошибок
        return new Response(JSON.stringify({
            error: "Network request failed",
            message: error.message
        }), {
            status: 503,
            detail: {
                data: {
                    message: "Network Error"
                }
            }
        });
    }
}

export async function deleteUserSession(token, userId, sessionId) {
    try {
        return await fetch(`${deleteUserSessionById(userId, sessionId)}`, {
            method: 'DELETE',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            }
        })

    } catch (error) {
        // Создаём искусственный Response для сетевых ошибок
        return new Response(JSON.stringify({
            error: "Network request failed",
            message: error.message
        }), {
            status: 503,
            detail: {
                data: {
                    message: "Network Error"
                }
            }
        });
    }
}

export async function getCameraGroupsList(token) {
    try {
        const response = await fetch(`${getCameraGroups}`, {
            method: 'GET',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            }
        });

        return response
    } catch (error) {
        return {
            ok: false,
            status: 0, // 0 = Network Error
            statusText: error.message,
            error: "Server is unreachable. Check your connection."
        };
    }
}


export async function getCamerasList(token, groupId) {
    return await fetch(`${getCameraOfGroup(groupId)}`, {
        method: 'GET',
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            'X-API-Key': apikey
        }
    })
}


export async function getCameraSubscribersList(token, groupId, cameraId) {
    return await fetch(`${getCameraSubscriptions(groupId, cameraId)}`, {
        method: 'GET',
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            'X-API-Key': apikey
        }
    })
}


/**
 * Получение списка пользователей с фильтрами и сортировкой
 * @param {string} token - JWT токен
 * @param {Object} [params={}] - Параметры запроса
 */
export async function getUsers(token, params = {}) {
    try {
        const queryParams = new URLSearchParams();

        // Обычные фильтры
        if (params.page !== undefined) queryParams.append('page', params.page);
        if (params.count !== undefined) queryParams.append('count', params.count);
        if (params.username) queryParams.append('username', params.username);
        if (params.email) queryParams.append('email', params.email);
        if (params.firstName) queryParams.append('firstName', params.firstName);
        if (params.lastName) queryParams.append('lastName', params.lastName);
        if (params.userId) queryParams.append('userId', params.userId);
        if (params.role) queryParams.append('role', params.role);
        if (params.createdFrom) queryParams.append('createdFrom', params.createdFrom.toISOString());
        if (params.createdTo) queryParams.append('createdTo', params.createdTo.toISOString());
        if (params.updatedFrom) queryParams.append('updatedFrom', params.updatedFrom.toISOString());
        if (params.updatedTo) queryParams.append('updatedTo', params.updatedTo.toISOString());
        console.log(queryParams);
        // Повторяющиеся поля
        if (Array.isArray(params.sort_by)) {
            params.sort_by.forEach(field => queryParams.append('sort_by', field));
        }
        if (Array.isArray(params.sort_order)) {
            params.sort_order.forEach(order => queryParams.append('sort_order', order));
        }

        const url = `${getUsersList}?${queryParams.toString()}`;

        return await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey,
            },
        });
    } catch (error) {
        // Создаём искусственный Response для сетевых ошибок
        return new Response(JSON.stringify({
            error: "Network request failed",
            message: error.message
        }), {
            status: 503,
            statusText: "Network Error"
        });
    }
}
