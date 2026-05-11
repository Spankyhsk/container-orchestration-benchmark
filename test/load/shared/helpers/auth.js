import axios from "axios";

export async function loginAdmin(api) {

    const res = await axios.post(
        api.auth.login,
        {
            email: "admin@mail.com",
            password: "admin123"
        },
        {
            headers: {
                "Content-Type": "application/json"
            }
        }
    );

    return res.data.accessToken;
}

