async function waitForRecovery(targets, {
    intervalMs = 1000,
    stableChecks = 5,
    timeoutMs = 120000
} = {}) {

    let successMap = new Map();
    const startTime = Date.now();

    // init counters
    for (const t of targets) {
        successMap.set(t.name, 0);
    }

    while (true) {

        if (Date.now() - startTime > timeoutMs) {
            throw new Error("Recovery timeout exceeded");
        }

        let allStable = true;

        for (const t of targets) {

            try {
                const res = await t.check();

                const ok = res?.status === 200;

                if (ok) {
                    successMap.set(t.name, successMap.get(t.name) + 1);
                } else {
                    successMap.set(t.name, 0);
                }

            } catch (e) {
                successMap.set(t.name, 0);
            }

            if (successMap.get(t.name) < stableChecks) {
                allStable = false;
            }
        }

        if (allStable) {
            return Date.now();
        }

        await new Promise(r => setTimeout(r, intervalMs));
    }
}

export async function waitForStableRecovery(targets, stableMs = 5000) {
    const start = Date.now();

    // first: normal recovery wait
    await waitForRecovery(targets);

    // second: stability window
    while (Date.now() - start < stableMs) {

        for (const t of targets) {
            const res = await t.check();

            if (!res || res.status !== 200) {
                throw new Error("Service not stable yet");
            }
        }

        await new Promise(r => setTimeout(r, 1000));
    }

    return Date.now();
}