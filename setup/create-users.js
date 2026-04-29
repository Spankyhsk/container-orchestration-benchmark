import fetch from "node-fetch";

const BASE_URL = process.env.BASE_URL;

async function createUsers() {
    console.log("Creating test users...");

    for (let i = 1; i <= 100; i++) {
        try {
            const res = await fetch(`http://api.${BASE_URL}/signup`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: `student${i}@mail.com`,
                    username: `student${i}`,
                    password: "test123"
                })
            });

            if (!res.ok) {
                console.error(`Failed user ${i}`);
            }
        } catch (err) {
            console.error(`Error user ${i}`, err);
        }
    }

    console.log("Done.");
}

createUsers();