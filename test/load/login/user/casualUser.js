import http from 'k6/http';
import { check, sleep } from 'k6';
import { API } from "../../shared/api"

export function casualUser(user, thinkTime){
    const res = http.post(API.auth, JSON.stringify({
        email: user.email,
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