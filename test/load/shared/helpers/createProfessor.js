import axios from "axios";

export async function createProfessor(api, adminToken){
    const res = await axios.post(api.auth.signup, {
        email: `professor@mail.com`,
        username: `professor`,
        password: "Passwort123"
    }, {
        headers: {
            "Content-Type": "application/json"
        }
    });

    const data = res.data;

    await axios.patch(
        api.setup.userPermissions(data._id),
        {
            permissions: `professor`
        },
        {
            headers: {
                Authorization: `Bearer ${adminToken}`,
                "Content-Type": "application/json"
            }
        }
    );
}