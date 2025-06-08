const apiUrl = import.meta.env.VITE_API_URL;

// EndPoints
export const login = `${apiUrl}/auth/login`;
export const logout = `${apiUrl}/auth/logout`;
export const getMyProfile = `${apiUrl}/user/me`