const BASE_URL = __ENV.BASE_URL;

export const API = {
    auth: {
        login: `http://api.${BASE_URL}/signin`
    },
    setup: {
        user: `http://api.${BASE_URL}/users`,
        userPermissions: (id) => `http://api.${BASE_URL}/users/${id}/permissions`
    }
};