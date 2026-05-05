import http from 'k6/http';
import { login } from "../shared/auth.js";
import { API } from "../shared/k6-api.js";

export function idleUser(user, thinkTime){
    const mail = `student${__VU}@mail.com`;
    const password = "Passwort123";

    const token = login(mail, password);
    //Steps einbauen
}