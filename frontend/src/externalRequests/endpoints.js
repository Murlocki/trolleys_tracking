const authUrl = import.meta.env.VITE_AUTH_URL;
const userUrl = import.meta.env.VITE_USER_URL;

// EndPoints
export const login = `${authUrl}/auth/login`;
export const logout = `${authUrl}/auth/logout`;
export const getMyProfile = `${userUrl}/user/me`