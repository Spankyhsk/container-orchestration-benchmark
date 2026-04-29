import { examUser } from "../user/exam-user";
import profiles from "../config/load-profiles.json";
import thresholds from "../config/thresholds.json";
import scenario  from "../config/scenario.json";
import { createSmokeUser } from "../../shared/setup-users";


export const options = {
    vus: profiles.smoke.vus,
    duration: profiles.smoke.duration,
    thresholds
};

export function setup(){
    return createSmokeUser(scenario, profiles.smoke.users, scenario.distribution.exam)
}

export default function (users){
    const user = users[(__VU -1)];

    examUser(scenario.thinkTime.exam)
}