const authUrl = import.meta.env.VITE_AUTH_URL;
const userUrl = import.meta.env.VITE_USER_URL;
const sessionUrl = import.meta.env.VITE_SESSION_URL;
const cameraUrl = import.meta.env.VITE_CAMERA_URL;
// EndPoints
export const login = `${authUrl}/auth/login`;
export const logout = `${authUrl}/auth/logout`;
export const getMyProfile = `${userUrl}/user/me`
export const getUsersList = `${userUrl}/user/crud`;
export const createUser = `${userUrl}/user/crud`;
export const deleteUser = (userId) => `${userUrl}/user/crud/${userId}`;
export const getUser = (userId) => `${userUrl}/user/crud/${userId}`;
export const updateUser = (userId) => `${userUrl}/user/crud/${userId}`;
export const updateUserPassword = (userId) => `${userUrl}/user/crud/${userId}/password_update`;
export const getUserRoles = `${userUrl}/user/roles`
export const getUserSessions = `${sessionUrl}/session/crud`;
export const deleteUserSessions = (userId) => `${sessionUrl}/session/crud/${userId}`;
export const deleteUserSessionById = (userId, sessionId) => `${sessionUrl}/session/crud/${userId}/${sessionId}`;
export const getCameraGroups = `${cameraUrl}/camera/crud/groups`;
export const getCameraOfGroup = (groupId) => `${cameraUrl}/camera/crud/groups/${groupId}/cameras`;
export const getCameraSubscriptions = (groupId, cameraId) => `${cameraUrl}/camera/crud/groups/${groupId}/cameras/${cameraId}/subscribers`;
export const deleteCameraSubscription = (groupId, cameraId, subscriptionId) => `${cameraUrl}/camera/crud/groups/${groupId}/cameras/${cameraId}/subscribers/${subscriptionId}`;
export const createCameraSubscription = (groupId, cameraId, subscriptionId) => `${cameraUrl}/camera/crud/groups/${groupId}/cameras/${cameraId}/subscribers`;
