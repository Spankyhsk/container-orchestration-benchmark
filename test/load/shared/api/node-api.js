export const API = (baseUrl) => {


    const apiBase = `http://api.${baseUrl}`;
    const aiBase = `http://ai-api.${baseUrl}`;
    const frontendBase = `http://${baseUrl}`;

    return {
        setup: {
            user: `${apiBase}/users`,
            userPermissions: (id) => `${apiBase}/users/${id}/permissions`
        },

        auth: {
            login: `${apiBase}/auth/signin`,
            signup: `${apiBase}/auth/signup`
        },

        cleanup: {
            userById: (id) => `${apiBase}/users/delete/${id}`
        },

        health: async () => {
            const res = await fetch(`${apiBase}/health`);
            return res;
        }
    };
};
