import http from 'k6/http';
import { check, sleep } from 'k6';
import { K6Api } from "../../shared/api/k6-api.js"

export function casualUser(user, thinkTime){
    const res = http.post(K6Api.auth.signup, JSON.stringify({
        email: user.email,
        username: user.username,
        password: user.password
    }), {
        headers: { "Content-Type": "application/json" }
    });

    check(res, {
        'login success': (r) => r.status === 200,
        'has token': (r) => r.json('token') !== undefined,
    });

    sleep(thinkTime);
}