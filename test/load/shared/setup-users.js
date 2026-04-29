import {login, loginAdmin} from "./auth";
import { API } from "./api"
import scenario  from "../vorlesungen/config/scenario.json";
import http from "k6/http";


export function buildUsers(count) {
    const users = [];

    for (let i = 1; i <= count; i++) {
        users.push({
            email: `student${i}@mail.com`,
            password: "Passwort123"
        });
    }

    return users;
}

export function getAllUsers(admin) {
    const res = http.get( API.setup.user, {
        headers: {
            Authorization: `Bearer ${admin}`,
            "Content-Type": "application/json"
        }
    });

    return res.json();
}

export function mapUsers(builtUsers, existingUsers) {

    const userMap = new Map();

    // DB User nach Email indexieren
    existingUsers.forEach(u => {
        userMap.set(u.email, u);
    });

    // gewünschte User matchen
    return builtUsers.map(u => {

        const dbUser = userMap.get(u.email);

        if (!dbUser) {
            throw new Error(`User nicht gefunden: ${u.email}`);
        }

        return {
            ...u,
            id: dbUser.id
        };
    });
}

export function loginUsers(users) {
    return users.map(u => ({
        ...u,
        token: login(u.email, u.password)
    }));
}

export function prepareUsers(count, admin) {

    // 1. gewünschte User definieren
    const builtUsers = buildUsers(count);

    // 2. alle DB User holen
    const existingUsers = getAllUsers(admin);

    // 3. matchen
    let users = mapUsers(builtUsers, existingUsers);

    return users;
}


export function calculateRoleCounts(distribution, totalUsers) {

    const result = {};
    let assigned = 0;

    // 1. erstmal abrunden
    for (const [role, percent] of Object.entries(distribution)) {
        const count = Math.floor(percent * totalUsers);
        result[role] = count;
        assigned += count;
    }

    // 2. Rest verteilen (wegen Rundung)
    let remaining = totalUsers - assigned;
    const roles = Object.keys(distribution);

    let i = 0;
    while (remaining > 0) {
        result[roles[i % roles.length]]++;
        remaining--;
        i++;
    }

    return result;
}


export function assignScenarioRolesToUsers(users, scenarioCounts) {

    let index = 0;

    for (const [role, count] of Object.entries(scenarioCounts)) {

        for (let i = 0; i < count; i++) {

            users[index].scenarioRole = role;
            index++;
        }
    }

    return users;
}

export function assignRoles(users, roleMapping, adminToken) {

    users.forEach(user => {

        const dbRole = roleMapping[user.scenarioRole];

        http.patch(API.setup.userPermissions(user.id), JSON.stringify({
            permissions: dbRole
        }), {
            headers: {
                Authorization: `Bearer ${adminToken}`,
                "Content-Type": "application/json"
            }
        });

        // lokal speichern
        user.dbRole = dbRole;
    });

    return users;
}

//Verteilt Rollen zufällig damit nicht zuerst nur die eine Rolle kommt und dann die nächste
export function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}

export function createAndAssignRoles(scenario, totalUsers, withLogin = true) {

    const distribution = scenario.distribution;
    const roleMapping = scenario.roleMapping;

    // 1. Szenario-Rollen berechnen
    const scenarioCounts = calculateRoleCounts(distribution, totalUsers);

    // 2. Admin login
    const admin = loginAdmin();

    // 3. Users holen + matchen
    let users = prepareUsers(totalUsers, admin);

    shuffle(users);

    // 4. Szenario-Rollen auf User verteilen
    users = assignScenarioRolesToUsers(users, scenarioCounts);

    // 5. DB Rollen setzen
    users = assignRoles(users, roleMapping, admin);

    // 6. Login
    if(withLogin){
        users = loginUsers(users);
    }


    return users;
}

export function createSmokeUser(scenario, totalUsers, smokerRole, withLogin = true){
    const roleMapping = scenario.roleMapping;

    const admin = loginAdmin();

    let users = prepareUsers(totalUsers, admin)

    users.forEach(u => {
        u.scenarioRole = smokerRole;
        u.dbRole = roleMapping[smokerRole];
    });

    users = assignRoles(users, roleMapping, admin);

    if(withLogin){
        users = loginUsers(users);
    }

    return users;
}




