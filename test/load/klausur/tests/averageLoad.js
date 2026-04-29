import { examUser } from "../user/exam-user";
import { browsingUser } from "../user/browsing-user";
import { professorUser } from "../user/professor-user";
import { idleUser } from "../user/idle-user";
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
    return createAndAssignRoles(scenario, profiles.averageLoad.users);
}

//Jeder VM wird zufällig einen User zugewiesen
export default function (users) {

    const user = users[(__VU - 1) % users.length];

    if(user.scenarioRole === "exam") {
        examUser(scenario.thinkTime.exam)
    } else if(user.scenarioRole === "browsing"){
        browsingUser(scenario.thinkTime.browsing)
    } else if(user.scenarioRole === "professor"){
        professorUser(scenario.thinkTime.professor)
    }else{
        idleUser(scenario.thinkTime.idle)
    }

}