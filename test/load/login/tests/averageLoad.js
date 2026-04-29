import {casualUser} from "../user/casualUser";
import scenario  from "../config/scenario.json";
import profiles from "../config/load-profiles.json";
import thresholds from "../config/thresholds.json";
import {createAndAssignRoles} from "../../shared/setup-users";

export const options = {
    vus: profiles.averageLoad.vus,
    duration: profiles.averageLoad.duration,
    thresholds
};

export function setup(){
    return createAndAssignRoles(scenario, profiles.averageLoad.users, false);
}

export default function (users) {

    const user = users[(__VU - 1) % users.length];

    casualUser(user, scenario.thinkTime.casualUser);

}