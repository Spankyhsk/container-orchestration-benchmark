const fs = require("fs");

const harFile = process.argv[2];
const baseUrl = process.argv[3];

if (!harFile || !baseUrl) {
    console.log("Usage: node har-to-k6.js file.har https://api.example.com");
    process.exit(1);
}

const har = JSON.parse(fs.readFileSync(harFile, "utf8"));

const entries = har.log.entries;

// Filter by base URL
const filtered = entries.filter(e =>
    e.request.url.startsWith(baseUrl)
);

// Convert to k6 requests
function buildRequest(entry) {
    const req = entry.request;

    let body = "null";

    if (req.postData && req.postData.text) {
        // try parse JSON, fallback string
        try {
            body = JSON.stringify(JSON.parse(req.postData.text));
        } catch (e) {
            body = JSON.stringify(req.postData.text);
        }
    }

    const url = req.url.replace(baseUrl, "");

    return `
    // ${req.method} ${req.url}
    let res${Math.random().toString(36).substring(7)} = http.request("${req.method}", baseUrl + "${url}", ${body}, {
      headers: ${JSON.stringify(req.headers.reduce((acc, h) => {
        acc[h.name] = h.value;
        return acc;
    }, {}))}
    });
  `;
}

const k6Script = `
import http from "k6/http";

const baseUrl = "${baseUrl}";

export default function () {
  ${filtered.map(buildRequest).join("\n")}
}
`;

fs.writeFileSync("test.js", k6Script);

console.log("✅ k6 script generated: test.js");