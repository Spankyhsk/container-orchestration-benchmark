import profiles from "../config/load-profiles.json";
import thresholds from "../config/thresholds.json";
import scenario  from "../config/scenario.json";
import { createSmokeUser } from "../../shared/setup-users";
import {casualUser} from "../user/casualUser";


export const options = {
    vus: profiles.smoke.vus,
    duration: profiles.smoke.duration,
    thresholds
};

export function setup(){
    return createSmokeUser(scenario, profiles.smoke.users, scenario.distribution.casualUser, false)
}

export default function (users){
    const user = users[(__VU -1)];

    casualUser(user, scenario.thinkTime.casualUser);
}