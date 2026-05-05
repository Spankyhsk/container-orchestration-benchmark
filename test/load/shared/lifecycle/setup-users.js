import {
    calculateRoleCounts,
    assignScenarioRolesToUsers,
    shuffle
} from "../core/role-utils.js";

export async function setupUsers({users, scenario, api, adminToken, mode, forcedRole, isAuthTest}) {

    // --------------------
    // 1. ROLE STRATEGY
    // --------------------

    if (mode === "smoke") {

        console.log(`🔥 Smoke mode → forcing role: ${forcedRole}`);

        users.forEach(u => {
            u.scenarioRole = forcedRole;
        });

    } else {

        const counts = calculateRoleCounts(
            scenario.distribution,
            users.length
        );

        users = assignScenarioRolesToUsers(users, counts);
    }

    // optional shuffle (immer sinnvoll)
    shuffle(users);

    // --------------------
    // 2. APPLY PERMISSIONS
    // --------------------
    if(isAuthTest){
        return users
    }

    for (const user of users) {

        await fetch(api.setup.userPermissions(user.id), {
            method: "PATCH",
            headers: {
                Authorization: `Bearer ${adminToken}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                permissions: scenario.roleMapping[user.scenarioRole]
            })
        });
    }

    return users;
}