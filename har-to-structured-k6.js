const fs = require("fs");

// -------------------------------------------------
// INPUT
// -------------------------------------------------
const harFile = process.argv[2];
const baseUrl = process.argv[3];

if (!harFile || !baseUrl) {
    console.log(
        "Usage: node har-to-structured-k6.js file.har https://base.url/"
    );
    process.exit(1);
}

// -------------------------------------------------
// LOAD HAR
// -------------------------------------------------
const har = JSON.parse(fs.readFileSync(harFile, "utf8"));

const entries = har.log.entries.filter((e) =>
    e.request.url.startsWith(baseUrl)
);

// -------------------------------------------------
// NORMALIZE URL
// -------------------------------------------------
function normalize(url) {
    return url
        .replace(baseUrl, "")
        .replace(/\/[0-9a-fA-F-]{20,}/g, "/:id")
        .replace(/\/\d+/g, "/:id");
}

// -------------------------------------------------
// SAFE VARIABLE NAME
// -------------------------------------------------
function varName(method, path, index) {
    return `${method.toLowerCase()}_${path
        .replace(/\//g, "_")
        .replace(/:/g, "")
        .replace(/[^a-zA-Z0-9_]/g, "")
        .replace(/__+/g, "_")
        .replace(/^_+/, "")}_${index}`;
}

// -------------------------------------------------
// BODY PARSER + PLACEHOLDERS
// -------------------------------------------------
function parseBody(req) {
    if (!req.postData?.text) return null;

    let body = req.postData.text;

    // ---------------------------------------------
    // PLACEHOLDER REPLACEMENTS
    // ---------------------------------------------
    body = body
        .replaceAll(
            /"userId"\s*:\s*"[^"]+"/g,
            `"userId":"\${userId}"`
        )
        .replaceAll(
            /"examId"\s*:\s*"[^"]+"/g,
            `"examId":"\${examId}"`
        )
        .replaceAll(
            /"semesterId"\s*:\s*"[^"]+"/g,
            `"semesterId":"\${semesterId}"`
        )
        .replaceAll(
            /"lectureId"\s*:\s*"[^"]+"/g,
            `"lectureId":"\${lectureId}"`
        )
        .replaceAll(
            /"authCode"\s*:\s*"[^"]+"/g,
            `"authCode":"\${authCode}"`
        );

    return `JSON.stringify(${body})`;
}

// -------------------------------------------------
// FILTER SPECIFIC POLLING ENDPOINTS
// -------------------------------------------------
const filteredEntries = [];

entries.forEach((e) => {

    const url = e.request.url;

    // ---------------------------------------------
    // REMOVE:
    // /exam/:id/student-grants
    // ---------------------------------------------
    const isStudentGrants =
        /\/exam\/[^/]+\/student-grants$/.test(url);

    // ---------------------------------------------
    // REMOVE:
    // /exam/:examId/user/:userId
    // ---------------------------------------------
    const isUserExam =
        /\/exam\/[^/]+\/user\/[^/]+$/.test(url);

    if (isStudentGrants || isUserExam) {
        return;
    }

    // ---------------------------------------------
    // KEEP EVERYTHING ELSE
    // ---------------------------------------------
    filteredEntries.push(e);
});

// -------------------------------------------------
// ROUTE REGISTRY (DEDUPED)
// -------------------------------------------------
const routeMap = new Map();

const flow = [];

filteredEntries.forEach((e) => {

    const req = e.request;

    const method = req.method.toUpperCase();

    const path = normalize(req.url);

    const key = `${method} ${path}`;

    // ---------------------------------------------
    // CREATE ROUTE VARIABLE ONCE
    // ---------------------------------------------
    if (!routeMap.has(key)) {

        routeMap.set(key, {
            method,
            path,
            var: varName(method, path, routeMap.size),
        });
    }

    // ---------------------------------------------
    // FLOW
    // ---------------------------------------------
    flow.push({
        method,
        path,
        var: routeMap.get(key).var,
        body: parseBody(req),
    });
});

// -------------------------------------------------
// GENERATE K6 SCRIPT
// -------------------------------------------------
let out = `
import http from 'k6/http';

export function examUser(user, thinkTime, ctx) {

  const params = {
    headers: {
      Authorization: \`Bearer \${user.token}\`,
      'Content-Type': 'application/json',
    },
  };

  // -------------------------------------------------
  // PLACEHOLDERS
  // -------------------------------------------------

  const userId = user.id;
  const examId = ctx.examId;
  const authCode = ctx.password;
  const semesterId = ctx.semesterId;
  const lectureId = ctx.lectureId;

  const baseUrl = "${baseUrl}";

  // -------------------------------------------------
  // ROUTES
  // -------------------------------------------------
`;

// -------------------------------------------------
// ROUTE VARIABLES
// -------------------------------------------------
routeMap.forEach((r) => {

    out += `
  const ${r.var} = baseUrl + "${r.path}";
`;
});

out += `

  // -------------------------------------------------
  // FLOW
  // -------------------------------------------------
`;

// -------------------------------------------------
// EXECUTE FLOW
// -------------------------------------------------
flow.forEach((r) => {

    let call;

    switch (r.method) {

        case "GET":
            call = `http.get(${r.var}, params)`;
            break;

        case "POST":
            call = `http.post(${r.var}, ${r.body || "null"}, params)`;
            break;

        case "PUT":
            call = `http.put(${r.var}, ${r.body || "null"}, params)`;
            break;

        case "PATCH":
            call = `http.patch(${r.var}, ${r.body || "null"}, params)`;
            break;

        case "DELETE":
            call = `http.del(${r.var}, params)`;
            break;

        default:
            call = `http.request("${r.method}", ${r.var}, ${r.body || "null"}, params)`;
    }

    out += `
  // ${r.method} ${r.path}
  ${call};
`;
});

out += `
}
`;

// -------------------------------------------------
// WRITE FILE
// -------------------------------------------------
fs.writeFileSync("test.js", out);

console.log("✅ Generated clean structured k6 test: test.js");