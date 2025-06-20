import {
    createUser,
    deleteUser,
    deleteUserSessionById, deleteUserSessions,
    getCameraGroups,
    getCameraOfGroup,
    getCameraSubscriptions,
    getMyProfile, getUser, getUserRoles,
    getUserSessions,
    getUsersList,
    login,
    logout, updateUser, updateUserPassword
} from "@/externalRequests/endpoints.js";
import {camelToSnake} from "@/validators/validators.js";

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

export async function deleteUserSessionList(token, userId) {
    try {
        return await fetch(`${deleteUserSessions(userId)}`, {
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
        if (params.firstName) queryParams.append('first_name', params.firstName);
        if (params.lastName) queryParams.append('last_name', params.lastName);
        if (params.id) queryParams.append('id', params.id);
        if (params.role) {
            for (const role of params.role) {
                queryParams.append('role', role);
            }
        }
        if (params.isActive!==null) queryParams.append("is_active", params.isActive);
        if (params.createdFrom) queryParams.append('created_from', params.createdFrom.toISOString());
        if (params.createdTo) queryParams.append('created_to', params.createdTo.toISOString());
        if (params.updatedFrom) queryParams.append('updated_from', params.updatedFrom.toISOString());
        if (params.updatedTo) queryParams.append('updated_to', params.updatedTo.toISOString());

        for(const val in params.sortBy) {
            if(params.sortBy[val]!==null){
                queryParams.append('sort_by', camelToSnake(val));
                queryParams.append('sort_order', params.sortBy[val]);
            }
        }
        console.log(queryParams.toString());

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


export async function deleteUserById(token, userId) {
    try {
        return await fetch(`${deleteUser(token, userId)}`, {
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

export async function getUserById(token, userId) {
    try {
        return await fetch(`${getUser(userId)}`, {
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

export async function createUserRecord(token, user) {
    try {
        return await fetch(`${createUser}`, {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            },
            body: JSON.stringify(user)
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

export async function updateUserRecord(token, userId, user) {
    try {
        return await fetch(`${updateUser(userId)}`, {
            method: 'PATCH',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            },
            body: JSON.stringify(user)
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

export async function updateUserPasswordRecord(token, userId, passwordForm) {
    try {
        return await fetch(`${updateUserPassword(userId)}`, {
            method: 'PATCH',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            },
            body: JSON.stringify(passwordForm)
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

export async function getUserRoleList(token) {
    try {
        return await fetch(`${getUserRoles}`, {
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