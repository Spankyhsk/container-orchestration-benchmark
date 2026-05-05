import { SharedArray } from 'k6/data';

const scenario = JSON.parse(open(__ENV.SCENARIO_PATH));
const profiles = JSON.parse(open(__ENV.LOADPROFILES_PATH));
const thresholds = JSON.parse(open(__ENV.THRESHOLDS));

export const options = {
    vus: profiles.stress.stages,
    thresholds,
    setupTimeout: profiles.stress.setupTimeout
};

const roleRegistry = JSON.parse(open(__ENV.ROLE_REGISTRY_PATH));

const users = new SharedArray('users', () =>
    JSON.parse(open(__ENV.USERS_PATH))
);

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