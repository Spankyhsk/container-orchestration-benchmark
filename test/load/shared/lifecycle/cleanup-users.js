import axios from "axios";

export async function cleanupUsers({ api, users, adminToken }) {

    for (const user of users) {
        const url = api.cleanup.userById(user.id);

        try {
            const res = await axios.delete(url, {
                headers: {
                    Authorization: `Bearer ${adminToken.trim()}`,
                    Accept: "*/*"
                }
            });

        } catch (err) {
            console.log("DELETE URL:", url);
            console.log("STATUS:", err.response?.status);
            console.log("BODY:", err.response?.data);
        }
    }
}
