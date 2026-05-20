import axios from "axios";
import {
    calculateRoleCounts,
    assignScenarioRolesToUsers,
    shuffle
} from "../core/role-utils.js";

export async function setupUsers({
                                     users,
                                     scenario,
                                     api,
                                     adminToken,
                                     mode,
                                     forcedRole,
                                     isAuthTest
                                 }) {

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

    shuffle(users);

    // --------------------
    // 2. APPLY PERMISSIONS
    // --------------------

    for (const user of users) {

        const url = api.setup.userPermissions(user.id);

        try {
            const res = await axios.patch(
                url,
                {
                    permissions: scenario.roleMapping[user.scenarioRole]
                },
                {
                    headers: {
                        Authorization: `Bearer ${adminToken}`,
                        "Content-Type": "application/json"
                    }
                }
            );


        } catch (err) {
            console.log("SETUP STATUS:", err.response?.status);
            console.log("SETUP BODY:", err.response?.data);
        }
    }


    return users;
}