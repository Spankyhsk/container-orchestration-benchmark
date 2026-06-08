import axios from "axios";

export const API = (baseUrl) => {

    const apiBase = `http://api.${baseUrl}`;
    const aiBase = `http://ai-api.${baseUrl}`;

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
            return await axios.get(`${apiBase}/health/ready`);
        },
        ai:{
            health: async () => {
                return await axios.get(`${aiBase}/health/ready`);
            },
        }
    };
};
