export async function createUsers({ count, api }) {

    const users = [];

    for (let i = 1; i <= count; i++) {

        const res = await fetch(api.auth.signup, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                email: `student${i}@mail.com`,
                username: `student${i}`,
                password: "Passwort123"
            })
        });

        const data = await res.json();

        users.push({
            email: `student${i}@mail.com`,
            password: "Passwort123",
            id: data.id,
            token: data.token
        });
    }

    return users;
}