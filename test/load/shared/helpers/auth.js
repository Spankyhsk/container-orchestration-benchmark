export function login(email, password, api) {
    const res = http.post(api.auth.signup, JSON.stringify({
        email,
        password
    }), {
        headers: { "Content-Type": "application/json" }
    });

    const body = res.json();

    return body.accessToken;
}

export function loginAdmin(api){
    let email = "admin@mail.com";
    let password = "admin123"

    return login(email, password, api)
}

