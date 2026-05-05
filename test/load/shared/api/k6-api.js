const BASE_URL = __ENV.BASE_URL;

const apiUrl = `http://api.${BASE_URL}`;
const aiapiUrl = `http://ai-api.${BASE_URL}`;
const frontendUrl = `http://${BASE_URL}`;

export const K6Api = {
    auth: {
        signup: `${apiUrl}/auth/signup`
    }
};