import { activeStudentUser } from "../user/activeStudentUser";
import { passiveStudentUser } from "../user/passiveStudentUser";
import { browsingStudentUser } from "../user/browsingStudentUser";
import { tutorUser } from "../user/tutorUser";
import { professorUser } from "../user/professorUser";
import { idleUser } from "../user/idleUser";
import scenario  from "../config/scenario.json";
import profiles from "../config/load-profiles.json";
import thresholds from "../config/thresholds.json";
import {createAndAssignRoles} from "../../shared/setup-users";

export const options = {
    vus: profiles.soak.vus,
    duration: profiles.soak.duration,
    thresholds
};

export function setup(){
    return createAndAssignRoles(scenario, profiles.soak.users)
}

//Jeder VM wird zufällig einen User zugewiesen
export default function (users) {

    const user = users[(__VU - 1) % users.length];

    if (user.scenarioRole === "activeStudent") {
        activeStudentUser(scenario.thinkTime.activeStudent);
    }

    else if (user.scenarioRole === "passiveStudent") {
        passiveStudentUser(scenario.thinkTime.passiveStudent);
    }

    else if (user.scenarioRole === "browsingStudent") {
        browsingStudentUser(scenario.thinkTime.browsingStudent);
    }

    else if (user.scenarioRole === "tutor") {
        tutorUser(scenario.thinkTime.tutor);
    }

    else if (user.scenarioRole === "professor") {
        professorUser(scenario.thinkTime.professor);
    }

    else {
        idleUser(scenario.thinkTime.idle);
    }
}