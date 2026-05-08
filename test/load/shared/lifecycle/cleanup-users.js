
export async function cleanupUsers({api, users, adminToken }) {

    for (const user of users) {
        await fetch(api.cleanup.userById(user.id), {
            method: "DELETE",
            headers: {
                Authorization: `Bearer ${adminToken}`
            }
        });
    }
}

export async function cleanupCreatedUsers({api, users, adminToken}) {

    const res = await fetch(api.setup.user, {
        headers: {
            Authorization: `Bearer ${adminToken}`
        }
    });

    const allUsers = await res.json();

    const usersToDelete = allUsers.filter(u =>
        users.includes(u.email)
    );

    console.log(`🧹 Deleting ${usersToDelete.length} created users`);

    await Promise.all(
        usersToDelete.map(user =>
            fetch(api.cleanup.userById(user.id), {
                method: "DELETE",
                headers: {
                    Authorization: `Bearer ${adminToken}`
                }
            })
        )
    );
}