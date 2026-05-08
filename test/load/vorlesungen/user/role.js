import {activeStudentUser} from "./activeStudentUser.js";
import {passiveStudentUser} from "./passiveStudentUser.js";
import {professorUser} from "./professorUser.js";
import {idleUser} from "./idleUser.js";

export const ROLE_REGISTRY = {
    activeStudent: activeStudentUser,
    passiveStudent: passiveStudentUser,
    professor: professorUser,
    idle: idleUser
};