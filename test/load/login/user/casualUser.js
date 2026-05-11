import http from 'k6/http';
import { check, sleep } from 'k6';
import { K6Api } from "../../shared/api/k6-api.js"

export function casualUser({ user, thinkTime }){


    const payload = {
        email: user.email,
        password: user.password
    };

    const res = http.post(
        K6Api.auth.login,
        JSON.stringify(payload),
        {
            headers: { "Content-Type": "application/json" }
        }
    );


    check(res, {
        'login success': (r) => r.status === 200,
        'has token': (r) => r.json("accessToken") !== undefined,
    });

    sleep(thinkTime);
}