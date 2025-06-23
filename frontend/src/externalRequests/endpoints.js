const authUrl = import.meta.env.VITE_AUTH_URL;
const userUrl = import.meta.env.VITE_USER_URL;
const sessionUrl = import.meta.env.VITE_SESSION_URL;
const cameraUrl = import.meta.env.VITE_CAMERA_URL;
const cameraReaderUrl = import.meta.env.VITE_CAMERA_READER_URL;
const cameraImages = import.meta.env.VITE_CAMERA_IMAGE_URL;
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
export const getCameraGroup = (groupId) => `${cameraUrl}/camera/crud/groups/${groupId}`;
export const createCameraGroup = `${cameraUrl}/camera/crud/groups`;
export const updateCameraGroup = (groupId) => `${cameraUrl}/camera/crud/groups/${groupId}`;
export const deleteCameraGroup = (groupId) => `${cameraUrl}/camera/crud/groups/${groupId}`;
export const getCameraOfGroup = (groupId) => `${cameraUrl}/camera/crud/groups/${groupId}/cameras`;
export const getCameraOfGroupById = (groupId, cameraId) => `${cameraUrl}/camera/crud/groups/${groupId}/cameras/${cameraId}`;
export const createCameraOfGroup = (groupId) => `${cameraUrl}/camera/crud/groups/${groupId}/cameras`;
export const deleteCameraOfGroup = (groupId, cameraId) => `${cameraUrl}/camera/crud/groups/${groupId}/cameras/${cameraId}`;
export const updateCameraOfGroup = (groupId, cameraId) => `${cameraUrl}/camera/crud/groups/${groupId}/cameras/${cameraId}`;
export const getCameraOfGroupStatus = (groupId, cameraId) => `${cameraReaderUrl}/camera_reader/groups/${groupId}/cameras/${cameraId}/status`;
export const startCameraOfGroup = (groupId, cameraId) => `${cameraReaderUrl}/camera_reader/groups/${groupId}/cameras/${cameraId}/activate`;
export const stopCameraOfGroup = (groupId, cameraId) => `${cameraReaderUrl}/camera_reader/groups/${groupId}/cameras/${cameraId}/deactivate`;
export const getCameraSubscriptions = (groupId, cameraId) => `${cameraUrl}/camera/crud/groups/${groupId}/cameras/${cameraId}/subscribers`;
export const deleteCameraSubscription = (groupId, cameraId, subscriptionId) => `${cameraUrl}/camera/crud/groups/${groupId}/cameras/${cameraId}/subscribers/${subscriptionId}`;
export const createCameraSubscription = (groupId, cameraId) => `${cameraUrl}/camera/crud/groups/${groupId}/cameras/${cameraId}/subscribers`;
export const connectSocket = `${cameraImages}`