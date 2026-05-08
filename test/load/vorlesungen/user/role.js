import {activeStudentUser} from "./activeStudentUser.js";
import {browsingStudentUser} from "./browsingStudentUser.js";
import {professorUser} from "./professorUser.js";
import {idleUser} from "./idleUser.js";

export const ROLE_REGISTRY = {
    activeStudent: activeStudentUser,
    browsingStudent: browsingStudentUser,
    professor: professorUser,
    idle: idleUser
};