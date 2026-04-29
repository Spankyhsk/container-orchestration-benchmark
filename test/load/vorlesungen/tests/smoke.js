import { activeStudentUser } from "../user/activeStudentUser";
import profiles from "../config/load-profiles.json";
import thresholds from "../config/thresholds.json";
import scenario  from "../config/scenario.json";
import { createSmokeUser} from "../../shared/setup-users";

export const options = {
    vus: profiles.smoke.vus,
    duration: profiles.smoke.duration,
    thresholds
};

export function setup(){
    return createSmokeUser(scenario, profiles.smoke.users, scenario.distribution.activeStudent)
}

export default function (users){
    const user = users[(__VU -1)];

    activeStudentUser(scenario.thinkTime.activeStudent)
}