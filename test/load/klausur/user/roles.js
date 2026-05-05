import {professorUser} from "./professor-user";
import {examUser} from "./exam-user";
import {browsingUser} from "./browsing-user";
import {idleUser} from "./idle-user";

export const ROLE_REGISTRY = {
    professor: professorUser,
    exam: examUser,
    browsing: browsingUser,
    idle: idleUser
};