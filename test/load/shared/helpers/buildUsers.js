export function buildUsers(count) {
    const users = [];

    for (let i = 1; i <= count; i++) {
        users.push({
            email: `student${i}@mail.com`,
            username: `student${i}`,
            password: "Passwort123"
        });
    }

    return users;
}