import http from "k6/http";

const GRAFANA_URL = __ENV.GRAFANA_URL;  // via SSH tunnel erreichbar
const GRAFANA_TOKEN = __ENV.GRAFANA_TOKEN
const ENV = __ENV.ENV;
const RUNNUMBER = __ENV.RUNNUMBER;

export function annotate(text, scenario) {
    http.post(
        `${GRAFANA_URL}/api/annotations`,
        JSON.stringify({
            text: text,
            tags: [
                `scenario:${scenario}`,
                `env:${ENV}`,
                `class:update`,
                `run:${RUNNUMBER}`
            ]
        }),
        {
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${GRAFANA_TOKEN}`
            }
        }
    );
}