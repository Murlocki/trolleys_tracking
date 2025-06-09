const authUrl = import.meta.env.VITE_AUTH_URL;
const userUrl = import.meta.env.VITE_USER_URL;
const sessionUrl = import.meta.env.VITE_SESSION_URL;
// EndPoints
export const login = `${authUrl}/auth/login`;
export const logout = `${authUrl}/auth/logout`;
export const getMyProfile = `${userUrl}/user/me`
export const getUsersList = `${userUrl}/user/crud`;
export const getUserSessions = `${sessionUrl}/session/crud`;
export const getCameraGroups = `${userUrl}/camera/crud/groups`;
export const getCameraOfGroup = (groupId) => `${userUrl}/camera/crud/groups/${groupId}/cameras`;
export const getCameraSubscriptions = (groupId, cameraId) => `${userUrl}/camera/crud/groups/${groupId}/cameras/${cameraId}/subscribers`;
