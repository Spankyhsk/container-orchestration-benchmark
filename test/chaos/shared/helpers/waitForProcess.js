export function waitForProcess(p) {
    return new Promise((res, rej) => {
        p.on("close", c => c === 0 ? res() : rej(c));
    });
}