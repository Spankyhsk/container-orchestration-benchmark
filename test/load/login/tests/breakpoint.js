import scenario  from "../config/scenario.json";
import profiles from "../config/load-profiles.json";
import thresholds from "../config/thresholds.json";
import {createAndAssignRoles} from "../../shared/setup-users";
import {casualUser} from "../user/casualUser";


export const options = {
    stages:  profiles.breakpoint.stages,
    thresholds
};

export function setup(){
    return createAndAssignRoles(scenario, profiles.breakpoint.users, false);
}


export default function (users) {

    const user = users[(__VU - 1) % users.length];

    casualUser(user, scenario.thinkTime.casualUser);

}