export function createDistribution(distribution) {
    let cumulative = 0;

    return Object.entries(distribution).map(([key, value]) => {
        cumulative += value;
        return { key, limit: cumulative };
    });
}

export function pickUser(distributionMap) {
    const rand = Math.random();

    for (const entry of distributionMap) {
        if (rand < entry.limit) {
            return entry.key;
        }
    }
}