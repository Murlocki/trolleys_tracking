import {
    createCameraGroup,
    createCameraOfGroup,
    createCameraSubscription,
    createUser,
    deleteCameraGroup,
    deleteCameraOfGroup,
    deleteCameraSubscription,
    deleteUser,
    deleteUserSessionById,
    deleteUserSessions,
    getCameraGroup,
    getCameraGroups,
    getCameraOfGroup,
    getCameraOfGroupById,
    getCameraOfGroupStatus,
    getCameraSubscriptions,
    getMyProfile,
    getUser,
    getUserRoles,
    getUserSessions,
    getUsersList,
    login,
    logout,
    startCameraOfGroup,
    stopCameraOfGroup,
    updateCameraGroup,
    updateCameraOfGroup,
    updateUser,
    updateUserPassword
} from "@/externalRequests/endpoints.js";
import {camelToSnake} from "@/validators/validators.js";

const apikey = import.meta.env.VITE_API_KEY;
console.log(apikey)

/**
 * Calls login api
 * @param {AuthForm} authForm - User auth data
 * @returns {Promise<Response>} - new access token
 */
export async function loginUser(authForm) {
    try {
        return await fetch(login, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(authForm)
        })
    } catch (error) {
        // Create response for network errors
        return new Response(JSON.stringify({
            error: "Network request failed",
            message: error.message
        }), {
            status: 503,
            statusText: "Network Error"
        });
    }
}

/**
 * Call login out api
 * @param {string} token - Auth token
 * @returns {Promise<Response>} - result of login out
 */
export async function loginOut(token) {
    try {
        return await fetch(logout, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        })
    } catch (error) {
        // Create response for network errors
        return new Response(JSON.stringify({
            error: "Network request failed",
            message: error.message
        }), {
            status: 503,
            statusText: "Network Error"
        });
    }
}

/**
 * Extracts user profile info
 * @param {string} token - Auth token
 * @returns {Promise<Response>} - user profile data
 */
export async function getUserProfile(token) {
    try {
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
        // Create response for network errors
        return new Response(JSON.stringify({
            error: "Network request failed",
            message: error.message
        }), {
            status: 503,
            statusText: "Network Error"
        });
    }
}

/**
 * Extracts list of user active sessions
 * @param {string} token - Auth token
 * @param {number} id - User id
 * @returns {Promise<Response>} - list of user active sessions
 */
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
        // Create response for network errors
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

/**
 * Delete user session by ID
 * @param {string} token - Auth token
 * @param {number} userId - User ID
 * @param {string} sessionId - Session ID
 * @returns {Promise<Response>} - deleted session info
 */
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
        // Create response for network errors
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

/**
 * Delete all user sessions
 * @param {string} token - Auth token
 * @param {number} userId - User ID
 * @returns {Promise<Response>} - List of deleted sessions
 */
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
        // Create response for network errors
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


export async function getCameraGroupsList(token, params = {}) {
    try {
        const queryParams = new URLSearchParams();
        // Adding filter info to query
        if (params.page !== undefined) queryParams.append('page', params.page);
        if (params.count !== undefined) queryParams.append('count', params.count);
        if (params.id) queryParams.append('id', params.id);
        if (params.name) queryParams.append('name', params.name);
        if (params.address) queryParams.append('address', params.address);
        if (params.description) queryParams.append('description', params.description);
        if (params.createdFrom) queryParams.append('created_from', params.createdFrom.toISOString());
        if (params.createdTo) queryParams.append('created_to', params.createdTo.toISOString());
        if (params.updatedFrom) queryParams.append('updated_from', params.updatedFrom.toISOString());
        if (params.updatedTo) queryParams.append('updated_to', params.updatedTo.toISOString());

        // Adding sorting parameters to query
        for (const val in params.sortBy) {
            if (params.sortBy[val] !== null) {
                queryParams.append('sort_by', camelToSnake(val));
                queryParams.append('sort_order', params.sortBy[val]);
            }
        }
        console.log(queryParams.toString());

        const url = `${getCameraGroups}?${queryParams.toString()}`;

        return await fetch(`${url}`, {
            method: 'GET',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            }
        })
    } catch (error) {
        return {
            ok: false,
            status: 0, // 0 = Network Error
            statusText: error.message,
            error: "Server is unreachable. Check your connection."
        };
    }
}

/**
 * GET group by ID
 * @param {string} token - Auth token
 * @param {number} groupID - Group ID
 * @returns {Promise<Response>} - Extracted group info
 */
export async function getGroupById(token, groupID) {
    try {
        return await fetch(`${getCameraGroup(groupID)}`, {
            method: 'GET',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            }
        })

    } catch (error) {
        // Create response for network errors
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

/**
 * Create group
 * @param {string} token - Auth token
 * @param {CameraGroupDTO} group - Group data
 * @returns {Promise<Response>} - Created group info
 */
export async function createGroup(token, group) {
    try {
        return await fetch(`${createCameraGroup}`, {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            },
            body: JSON.stringify(group)
        })

    } catch (error) {
        // Create response for network errors
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

/**
 * Update group
 * @param {string} token - Auth token
 * @param {number} groupId - Group ID
 * @param {CameraGroupDTO} group - Group data
 * @returns {Promise<Response>} - Created group info
 */
export async function updateGroup(token, groupId, group) {
    try {
        return await fetch(`${updateCameraGroup(groupId)}`, {
            method: 'PATCH',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            },
            body: JSON.stringify(group)
        })

    } catch (error) {
        // Create response for network errors
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

/**
 * Delete group
 * @param {string} token - Auth token
 * @param {number} groupId - Group ID
 * @returns {Promise<Response>} - Deleted group info
 */
export async function deleteGroup(token, groupId) {
    try {
        return await fetch(`${deleteCameraGroup(groupId)}`, {
            method: 'DELETE',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            }
        })

    } catch (error) {
        // Create response for network errors
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



export async function getCamerasList(token, groupId, params={}) {
    try {
        const queryParams = new URLSearchParams();
        // Adding filter info to query
        if (params.page) queryParams.append('page', params.page);
        if (params.count) queryParams.append('count', params.count);
        if (params.id) queryParams.append('id', params.id);
        if (params.name) queryParams.append('name', params.name);
        if (params.addressLink) queryParams.append('address_link', params.addressLink);
        if (params.createdFrom) queryParams.append('created_from', params.createdFrom.toISOString());
        if (params.createdTo) queryParams.append('created_to', params.createdTo.toISOString());
        if (params.updatedFrom) queryParams.append('updated_from', params.updatedFrom.toISOString());
        if (params.updatedTo) queryParams.append('updated_to', params.updatedTo.toISOString());

        // Adding sorting parameters to query
        for (const val in params.sortBy) {
            if (params.sortBy[val] !== null) {
                queryParams.append('sort_by', camelToSnake(val));
                queryParams.append('sort_order', params.sortBy[val]);
            }
        }
        console.log(queryParams.toString());

        const url = `${getCameraOfGroup(groupId)}?${queryParams.toString()}`;

        return await fetch(`${url}`, {
            method: 'GET',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            }
        })
    } catch (error) {
        return {
            ok: false,
            status: 0, // 0 = Network Error
            statusText: error.message,
            error: "Server is unreachable. Check your connection."
        };
    }
}


/**
 * Delete camera by ID
 * @param {string} token - Auth token
 * @param {number} groupID - Group ID
 * @param {number} cameraID - Camera ID
 * @returns {Promise<Response>} - Deleted user info
 */
export async function deleteCameraById(token, groupID, cameraID) {
    try {
        return await fetch(`${deleteCameraOfGroup(groupID, cameraID)}`, {
            method: 'DELETE',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            }
        })

    } catch (error) {
        // Create response for network errors
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

/**
 * Get camera by ID
 * @param {string} token - Auth token
 * @param {number} groupID - Group ID
 * @param {number} cameraID - Camera ID
 * @returns {Promise<Response>} - Deleted user info
 */
export async function getCameraById(token, groupID, cameraID) {
    try {
        return await fetch(`${getCameraOfGroupById(groupID, cameraID)}`, {
            method: 'GET',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            }
        })

    } catch (error) {
        // Create response for network errors
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

/**
 * Get camera by ID
 * @param {string} token - Auth token
 * @param {number} groupID - Group ID
 * @param {number} cameraID - Camera ID
 * @param {CameraDTO} camera - Camera update data
 * @returns {Promise<Response>} - Deleted user info
 */
export async function updateCameraById(token, groupID, cameraID, camera) {
    try {
        return await fetch(`${updateCameraOfGroup(groupID, cameraID)}`, {
            method: 'PATCH',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            },
            body: JSON.stringify(camera),
        })

    } catch (error) {
        // Create response for network errors
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

/**
 * Create camera
 * @param {string} token - Auth token
 * @param {number} groupID - Group ID
 * @param {CameraDTO} camera - Camera create data
 * @returns {Promise<Response>} - Created camera info
 */
export async function createCamera(token, groupID, camera) {
    try {
        return await fetch(`${createCameraOfGroup(groupID)}`, {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            },
            body: JSON.stringify(camera)
        })

    } catch (error) {
        // Create response for network errors
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

/**
 * Extract camera status by ID
 * @param {string} token - Auth token
 * @param {number} groupId - Group ID
 * @param {number} cameraId - Camera ID
 * @returns {Promise<Response>} - Extracted camera status info
 */
export async function getCameraStatusById(token, groupId, cameraId) {
    try {
        return await fetch(`${getCameraOfGroupStatus(groupId, cameraId)}`, {
            method: 'GET',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            }
        })

    } catch (error) {
        // Create response for network errors
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

/**
 * Stop camera process by ID
 * @param {string} token - Auth token
 * @param {number} groupId - Group ID
 * @param {number} cameraId - Camera ID
 * @returns {Promise<Response>} - Stopped camera process info
 */
export async function stopCameraById(token, groupId, cameraId) {
    try {
        return await fetch(`${stopCameraOfGroup(groupId, cameraId)}`, {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            }
        })

    } catch (error) {
        // Create response for network errors
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

/**
 * Stop camera process by ID
 * @param {string} token - Auth token
 * @param {number} groupId - Group ID
 * @param {number} cameraId - Camera ID
 * @param {Object} params - Process params
 * @returns {Promise<Response>} - Stopped camera process info
 */
export async function startCameraById(token, groupId, cameraId, params) {
    try {
        return await fetch(`${startCameraOfGroup(groupId, cameraId)}`, {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            },
            body: JSON.stringify(params)
        })

    } catch (error) {
        // Create response for network errors
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



export async function getCameraSubscribersList(token, groupId, cameraId, params={}) {
    try {
        const queryParams = new URLSearchParams();
        // Adding filter info to query
        if (params.page) queryParams.append('page', params.page);
        if (params.count) queryParams.append('count', params.count);
        if (params.username) queryParams.append('username', params.username);
        if (params.id) queryParams.append('id', params.id);
        if (params.createdFrom) queryParams.append('created_from', params.createdFrom.toISOString());
        if (params.createdTo) queryParams.append('created_to', params.createdTo.toISOString());
        if (params.updatedFrom) queryParams.append('updated_from', params.updatedFrom.toISOString());
        if (params.updatedTo) queryParams.append('updated_to', params.updatedTo.toISOString());

        // Adding sorting parameters to query
        for (const val in params.sortBy) {
            if (params.sortBy[val] !== null) {
                queryParams.append('sort_by', camelToSnake(val));
                queryParams.append('sort_order', params.sortBy[val]);
            }
        }
        console.log(queryParams.toString());

        const url = `${getCameraSubscriptions(groupId, cameraId)}?${queryParams.toString()}`;

        return await fetch(`${url}`, {
            method: 'GET',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            }
        })
    } catch (error) {
        return {
            ok: false,
            status: 0, // 0 = Network Error
            statusText: error.message,
            error: "Server is unreachable. Check your connection."
        };
    }
}

/**
 * Delete subscription by ID
 * @param {string} token - Auth token
 * @param {number} groupID - Group ID
 * @param {number} cameraID - Group ID
 * @param {number} subscriptionID - Group ID
 * @returns {Promise<Response>} - Deleted user info
 */
export async function deleteSubscriptionById(token, groupID, cameraID, subscriptionID) {
    try {
        return await fetch(`${deleteCameraSubscription(groupID, cameraID, subscriptionID)}`, {
            method: 'DELETE',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            }
        })

    } catch (error) {
        // Create response for network errors
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

/**
 * Delete subscription by ID
 * @param {string} token - Auth token
 * @param {number} groupID - Group ID
 * @param {number} cameraID - Group ID
 * @param {SubscriptionCreateDTO} subscription - Subscription create data
 * @returns {Promise<Response>} - Created subscription info
 */
export async function createSubscription(token, groupID, cameraID, subscription) {
    try {
        return await fetch(`${createCameraSubscription(groupID, cameraID)}`, {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            },
            body: JSON.stringify(subscription)
        })

    } catch (error) {
        // Create response for network errors
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

/**
 * Get filtered sorted user list
 * @param {string} token - Auth token
 * @param {Object} [params={}] - Filter and sort parameters
 * @return {Promise<Response>} - Extracted user list
 */
export async function getUsers(token, params = {}) {
    try {
        const queryParams = new URLSearchParams();

        // Adding filter info to query
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
        if (params.isActive === true || params.isActive === false) queryParams.append("is_active", params.isActive);
        if (params.createdFrom) queryParams.append('created_from', params.createdFrom.toISOString());
        if (params.createdTo) queryParams.append('created_to', params.createdTo.toISOString());
        if (params.updatedFrom) queryParams.append('updated_from', params.updatedFrom.toISOString());
        if (params.updatedTo) queryParams.append('updated_to', params.updatedTo.toISOString());

        // Adding sorting parameters to query
        for (const val in params.sortBy) {
            if (params.sortBy[val] !== null) {
                queryParams.append('sort_by', camelToSnake(val));
                queryParams.append('sort_order', params.sortBy[val]);
            }
        }
        console.log(queryParams.toString());

        const url = `${getUsersList}?${queryParams.toString()}`;

        // Creating request
        return await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey,
            },
        });
    } catch (error) {
        // Create response for network errors
        return new Response(JSON.stringify({
            error: "Network request failed",
            message: error.message
        }), {
            status: 503,
            statusText: "Network Error"
        });
    }
}

/**
 * Delete user by ID
 * @param {string} token - Auth token
 * @param {number} userId - User ID
 * @returns {Promise<Response>} - Deleted user info
 */
export async function deleteUserById(token, userId) {
    try {
        return await fetch(`${deleteUser(userId)}`, {
            method: 'DELETE',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'X-API-Key': apikey
            }
        })

    } catch (error) {
        // Create response for network errors
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

/**
 * Extract user by ID
 * @param {string} token - Auth token
 * @param {number} userId - User ID
 * @returns {Promise<Response>} - Extracted user info
 */
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
        // Create response for network errors
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

/**
 * Create new user Record
 * @param {string} token - Auth token
 * @param {UserCreate} user - User create info
 * @returns {Promise<Response>} - Created user info
 */
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
        // Create response for network errors
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

/**
 * Update user record
 * @param {string} token - Auth token
 * @param {number} userId - User ID
 * @param {UserUpdate} user - User update info
 * @returns {Promise<Response>} - Updated user info
 */
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
        // Create response for network errors
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

/**
 * Update user password
 * @param {string} token - Auth token
 * @param {number} userId - User ID
 * @param {PasswordDTO} passwordForm - Password update inf0
 * @returns {Promise<Response>} - Updated user info
 */
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
        // Create response for network errors
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

/**
 * Extract list of all existing roles
 * @param {string} token - Auth token
 * @returns {Promise<Response>} - List of all existing roles
 */
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
        // Create response for network errors
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