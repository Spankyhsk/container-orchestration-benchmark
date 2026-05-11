import axios from "axios";

export async function createUsers({ count, api }) {

    const users = [];

    for (let i = 1; i <= count; i++) {

        const res = await axios.post(api.auth.signup, {
            email: `student${i}@mail.com`,
            username: `student${i}`,
            password: "Passwort123"
        }, {
            headers: {
                "Content-Type": "application/json"
            }
        });

        const data = res.data;

        users.push({
            email: `student${i}@mail.com`,
            password: "Passwort123",
            id: data._id,
            token: data.accessToken
        });
    }

    return users;
}