import {activeStudentUser} from "./activeStudentUser";
import {passiveStudentUser} from "./passiveStudentUser";
import {browsingStudentUser} from "./browsingStudentUser";
import {professorUser} from "./professorUser";
import {tutorUser} from "./tutorUser";
import {idleUser} from "./idleUser";

export const ROLE_REGISTRY = {
    activeStudent: activeStudentUser,
    passiveStudent: passiveStudentUser,
    browsingStudent: browsingStudentUser,
    tutor: tutorUser,
    professor: professorUser,
    idle: idleUser
};