import http from "k6/http";
import { API } from "test/load/shared/api.js";

export function login(email, password) {
    const res = http.post(API.auth, JSON.stringify({
        email,
        password
    }), {
        headers: { "Content-Type": "application/json" }
    });

    const body = res.json();

    return body.accessToken;
}

export function loginAdmin(){
    let email = "admin@mail.com";
    let password = "admin123"

    return login(email, password)
}

