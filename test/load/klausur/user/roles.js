import {professorUser} from "./professor-user.js";
import {examUser} from "./exam-user.js";
import {browsingUser} from "./browsing-user.js";
import {idleUser} from "./idle-user.js";

export const ROLE_REGISTRY = {
    professor: professorUser,
    exam: examUser,
    browsing: browsingUser,
    idle: idleUser
};