
export async function cleanupUsers({ users, api, adminToken }) {

    for (const user of users) {
        await fetch(api.cleanup.userById(user.id), {
            method: "DELETE",
            headers: {
                Authorization: `Bearer ${adminToken}`
            }
        });
    }
}