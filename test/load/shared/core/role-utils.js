export function calculateRoleCounts(distribution, totalUsers) {

    const result = {};
    let assigned = 0;

    for (const [role, percent] of Object.entries(distribution)) {
        const count = Math.floor(percent * totalUsers);
        result[role] = count;
        assigned += count;
    }

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

export function assignScenarioRolesToUsers(users, counts) {

    let index = 0;

    for (const [role, count] of Object.entries(counts)) {
        for (let i = 0; i < count; i++) {
            users[index].scenarioRole = role;
            index++;
        }
    }

    return users;
}

export function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}