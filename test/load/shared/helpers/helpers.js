export async function waitForIdle({
                                      api,
                                      threshold = 200,
                                      stableCount = 3,
                                      interval = 2000,
                                      timeout = 60000
                                  }) {

    let stable = 0;
    const start = Date.now();

    while (true) {

        const t0 = Date.now();

        await api.health(); // 👈 hier nutzt du deine node-api

        const duration = Date.now() - t0;

        const isFast = duration < threshold;

        if (isFast) {
            stable++;
        } else {
            stable = 0;
        }

        if (stable >= stableCount) {
            console.log("System stabilized");
            return;
        }

        if (Date.now() - start > timeout) {
            throw new Error("System did not stabilize");
        }

        await new Promise(r => setTimeout(r, interval));
    }
}

function randomBetween(min, max) {
    return Math.random() * (max - min) + min;
}