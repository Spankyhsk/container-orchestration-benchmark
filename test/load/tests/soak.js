import { SharedArray } from 'k6/data';
import {loadRoleRegistry} from "../shared/helpers/load-role-registry.js";
import { annotate } from  '../shared/helpers/annotate.js';

const scenario = JSON.parse(open(__ENV.SCENARIO_PATH));
const profiles = JSON.parse(open(__ENV.LOADPROFILES_PATH));
const thresholds = JSON.parse(open(__ENV.THRESHOLDS_PATH));

export const options = {
    vus: profiles.soak.vus,
    duration: profiles.soak.duration,
    thresholds,
    setupTimeout: profiles.soak.setupTimeout
};

const testName = __ENV.TEST_NAME;

const roleRegistry = loadRoleRegistry(testName);

const users = new SharedArray('users', () =>
    JSON.parse(open(__ENV.USERS_PATH))
);

export function setup(){
    annotate("START", "soak", testName);
}

//Jeder VM wird zufällig einen User zugewiesen
export default function () {

    const user = users[(__VU - 1) % users.length];

    const handler = roleRegistry[user.scenarioRole];

    if (!handler) {
        throw new Error(`Unknown role: ${user.scenarioRole}`);
    }

    handler({
        user,
        thinkTime: scenario.thinkTime[user.scenarioRole]
    });
}

export function teardown() {
    annotate("END", "soak", testName);
}