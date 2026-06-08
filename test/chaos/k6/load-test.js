import { SharedArray } from 'k6/data';
import http from 'k6/http';
import { check, group } from 'k6';

import {annotate} from "../shared/helpers/annotate.js";
import {K6Api} from "../shared/api/k6-api.js";
import {think} from "../shared/helpers/helpers.js";

export const options = {
    vus: 50,
    duration: "10m",
    thresholds: {
        "http_req_duration": [
            "p(95)<800",
            "p(99)<1200",
            "avg<400"
        ],
        "http_req_failed": [
            "rate<0.01"
        ],
        "http_reqs": [
            "rate>20"
        ]
    },
};

const scenario = __ENV.TEST_NAME;
const type = __ENV.TEST_TYPE;


const thinkTime = [2, 5];

const users = new SharedArray('users', () =>
    JSON.parse(open(__ENV.USER_PATH))
);

export function setup() {
    if(type !== "update"){
        annotate("START", type, scenario)
    }
}

export default function () {
    const user = users[(__VU - 1) % users.length];

    const params = {
        headers: {
            Authorization: `Bearer ${user.token}`,
            'Content-Type': 'application/json',
        },
    };

    const userId = user.id;
    let semesterId = "";
    let lectureId = "";
    let courseId = "";

    // -------------------------------------------------
    // Auth / Session Requests
    // -------------------------------------------------
    group('Auth / Session', () => {

        const userRes1 = http.get(K6Api.auth.getUser, params);

        check(userRes1, {
            'getUser status 200': (r) => r.status === 200,
        });

        const authRes1 = http.get(K6Api.auth.isAuthenticated, params);

        check(authRes1, {
            'isAuthenticated status 200': (r) => r.status === 200,
        });

        const userRes2 = http.get(K6Api.auth.getUser, params);

        check(userRes2, {
            'second getUser status 200': (r) => r.status === 200,
        });
    });

    // -------------------------------------------------
    // Dashboard / Subscription
    // -------------------------------------------------
    group('Dashboard / Subscription', () => {

        const subRes = http.get(
            K6Api.subscriptions.getSubscription(userId),
            params
        );

        check(subRes, {
            'subscription status 200': (r) => r.status === 200,
        });


        const semesterRes = http.get(
            K6Api.semesters.getView,
            params
        );

        check(semesterRes, {
            'semester view status 200': (r) => r.status === 200,
        });

        const semesters = semesterRes.json();

        const semester = semesters[0];

        check(semester, {
            'semester exists': (s) => s !== undefined,
        });

        semesterId = semester._id;

        const lecture = semester.lectures.find(
            l => l.name === 'Scala 3'
        );

        check(lecture, {
            'scala 3 lecture found': (l) => l !== undefined,
        });

        lectureId = lecture._id;

        think(thinkTime);

        http.get(
            K6Api.subscriptions.getSubscriptionList,
            params
        );

        think(thinkTime);

        http.get(K6Api.auth.getUser, params);
        http.get(K6Api.auth.isAuthenticated, params);

        http.get(
            K6Api.subscriptions.getSubscription(userId),
            params
        );

        http.get(K6Api.auth.getUser, params);
        http.get(K6Api.auth.isAuthenticated, params);

        const semesterDetailRes = http.get(
            K6Api.semesters.getSemesters(semesterId),
            params
        );

        check(semesterDetailRes, {
            'semester detail status 200': (r) => r.status === 200,
        });

        think(thinkTime);
    });

    // -------------------------------------------------
    // Courses laden
    // -------------------------------------------------
    group('Load Courses', () => {

        const coursesRes = http.get(
            K6Api.lectures.getCourses(
                userId,
                semesterId,
                lectureId
            ),
            params
        );

        check(coursesRes, {
            'courses status 200': (r) => r.status === 200,
        });

        const lectureData = coursesRes.json();

        const course = lectureData.courses.find(
            c => c.title === 'Learn Scala 3 The Fast Way'
        );

        check(course, {
            'scala course found': (c) => c !== undefined,
        });

        courseId = course._id;

        think(thinkTime);
    });
    // -------------------------------------------------
    // Kapitel 2 öffnen
    // -------------------------------------------------
    group('Open Chapter', () => {

        http.get(
            K6Api.subscriptions.getSubscription(userId),
            params
        );

        http.get(K6Api.auth.isAuthenticated, params);
        http.get(K6Api.auth.getUser, params);

        const progressRes = http.get(
            K6Api.taskProgress.getChapter(
                userId,
                semesterId,
                lectureId,
                courseId,
                2
            ),
            params
        );

        check(progressRes, {
            'chapter progress status 200': (r) => r.status === 200,
        });

        const chapterRes = http.get(
            K6Api.courses.getChapter(courseId, 2),
            params
        );

        check(chapterRes, {
            'chapter data status 200': (r) => r.status === 200,
        });

        think(thinkTime);
    });
    // -------------------------------------------------
    // Tasks bearbeiten
    // -------------------------------------------------
    group('Solve Tasks', () => {

        const taskPayloads = [
            "{\"userId\":\"69fccd6bbae82e92b8b786cc\",\"semesterId\":\"69fccc08bae82e92b8b786ca\",\"lectureId\":\"69fccbf7bae82e92b8b786c9\",\"courseId\":\"1520436578208\",\"chapterId\":\"2\",\"taskId\":\"1\",\"solutions\":[],\"cheatedSolutions\":[],\"attemptsUntilSuccess\":null,\"timeOnTaskSeconds\":5,\"solutionRevealedTimestamp\":null,\"checkedByProfessor\":false,\"professorCorrectness\":null,\"professorScore\":null,\"professorComment\":null}",
            "{\"userId\":\"69fccd6bbae82e92b8b786cc\",\"semesterId\":\"69fccc08bae82e92b8b786ca\",\"lectureId\":\"69fccbf7bae82e92b8b786c9\",\"courseId\":\"1520436578208\",\"chapterId\":\"2\",\"taskId\":\"2\",\"solutions\":[],\"cheatedSolutions\":[],\"attemptsUntilSuccess\":null,\"timeOnTaskSeconds\":11,\"solutionRevealedTimestamp\":null,\"checkedByProfessor\":false,\"professorCorrectness\":null,\"professorScore\":null,\"professorComment\":null}",
            "{\"userId\":\"69fccd6bbae82e92b8b786cc\",\"semesterId\":\"69fccc08bae82e92b8b786ca\",\"lectureId\":\"69fccbf7bae82e92b8b786c9\",\"courseId\":\"1520436578208\",\"chapterId\":\"2\",\"taskId\":\"3\",\"solutions\":[\"\\\"Hello, world\\\"\"],\"cheatedSolutions\":[false],\"attemptsUntilSuccess\":1,\"timeOnTaskSeconds\":37,\"solutionRevealedTimestamp\":null,\"checkedByProfessor\":false,\"professorCorrectness\":null,\"professorScore\":null,\"professorComment\":null}",
            "{\"userId\":\"69fccd6bbae82e92b8b786cc\",\"semesterId\":\"69fccc08bae82e92b8b786ca\",\"lectureId\":\"69fccbf7bae82e92b8b786c9\",\"courseId\":\"1520436578208\",\"chapterId\":\"2\",\"taskId\":\"4\",\"solutions\":[\"\\\"ScalaRocks!\\\"\"],\"cheatedSolutions\":[false],\"attemptsUntilSuccess\":1,\"timeOnTaskSeconds\":59,\"solutionRevealedTimestamp\":null,\"checkedByProfessor\":false,\"professorCorrectness\":null,\"professorScore\":null,\"professorComment\":null}",
            "{\"userId\":\"69fccd6bbae82e92b8b786cc\",\"semesterId\":\"69fccc08bae82e92b8b786ca\",\"lectureId\":\"69fccbf7bae82e92b8b786c9\",\"courseId\":\"1520436578208\",\"chapterId\":\"2\",\"taskId\":\"5\",\"solutions\":[],\"cheatedSolutions\":[],\"attemptsUntilSuccess\":null,\"timeOnTaskSeconds\":76,\"solutionRevealedTimestamp\":null,\"checkedByProfessor\":false,\"professorCorrectness\":null,\"professorScore\":null,\"professorComment\":null}",
            "{\"userId\":\"69fccd6bbae82e92b8b786cc\",\"semesterId\":\"69fccc08bae82e92b8b786ca\",\"lectureId\":\"69fccbf7bae82e92b8b786c9\",\"courseId\":\"1520436578208\",\"chapterId\":\"2\",\"taskId\":\"6\",\"solutions\":[\"It adds a newline after the output\"],\"cheatedSolutions\":[false],\"attemptsUntilSuccess\":1,\"timeOnTaskSeconds\":82,\"solutionRevealedTimestamp\":null,\"checkedByProfessor\":false,\"professorCorrectness\":null,\"professorScore\":null,\"professorComment\":null}",
            "{\"userId\":\"69fccd6bbae82e92b8b786cc\",\"semesterId\":\"69fccc08bae82e92b8b786ca\",\"lectureId\":\"69fccbf7bae82e92b8b786c9\",\"courseId\":\"1520436578208\",\"chapterId\":\"2\",\"taskId\":\"7\",\"solutions\":[\"print('Hello, world')\"],\"cheatedSolutions\":[false],\"attemptsUntilSuccess\":null,\"timeOnTaskSeconds\":98,\"solutionRevealedTimestamp\":null,\"checkedByProfessor\":false,\"professorCorrectness\":null,\"professorScore\":null,\"professorComment\":null}",
            "{\"userId\":\"69fccd6bbae82e92b8b786cc\",\"semesterId\":\"69fccc08bae82e92b8b786ca\",\"lectureId\":\"69fccbf7bae82e92b8b786c9\",\"courseId\":\"1520436578208\",\"chapterId\":\"2\",\"taskId\":\"7\",\"solutions\":[\"println(\\\"Hello, world\\\")\"],\"cheatedSolutions\":[false],\"attemptsUntilSuccess\":2,\"timeOnTaskSeconds\":100,\"solutionRevealedTimestamp\":null,\"checkedByProfessor\":false,\"professorCorrectness\":null,\"professorScore\":null,\"professorComment\":null}",
            "{\"userId\":\"69fccd6bbae82e92b8b786cc\",\"semesterId\":\"69fccc08bae82e92b8b786ca\",\"lectureId\":\"69fccbf7bae82e92b8b786c9\",\"courseId\":\"1520436578208\",\"chapterId\":\"2\",\"taskId\":\"8\",\"solutions\":[\"No, it's optional unless multiple statements are on one line\"],\"cheatedSolutions\":[false],\"attemptsUntilSuccess\":1,\"timeOnTaskSeconds\":113,\"solutionRevealedTimestamp\":null,\"checkedByProfessor\":false,\"professorCorrectness\":null,\"professorScore\":null,\"professorComment\":null}",
            "{\"userId\":\"69fccd6bbae82e92b8b786cc\",\"semesterId\":\"69fccc08bae82e92b8b786ca\",\"lectureId\":\"69fccbf7bae82e92b8b786c9\",\"courseId\":\"1520436578208\",\"chapterId\":\"2\",\"taskId\":\"9\",\"solutions\":[\"println(\\\"Hello\\\")\",\"print(\\\"Hello\\\")\",\"System.err.println(\\\"Error!\\\")\"],\"cheatedSolutions\":[false,false,false,false],\"attemptsUntilSuccess\":1,\"timeOnTaskSeconds\":130,\"solutionRevealedTimestamp\":null,\"checkedByProfessor\":false,\"professorCorrectness\":null,\"professorScore\":null,\"professorComment\":null}",
            "{\"userId\":\"69fccd6bbae82e92b8b786cc\",\"semesterId\":\"69fccc08bae82e92b8b786ca\",\"lectureId\":\"69fccbf7bae82e92b8b786c9\",\"courseId\":\"1520436578208\",\"chapterId\":\"2\",\"taskId\":\"10\",\"solutions\":[\"val name = \\\"Scala\\\"\\nval message = \\\"rocks!\\\"\\nprintln(name + \\\" \\\" + message)\"],\"cheatedSolutions\":[false],\"tests\":\"name should be(\\\"Scala\\\")\\nmessage should be(\\\"rocks!\\\")\",\"attemptsUntilSuccess\":null,\"timeOnTaskSeconds\":192,\"solutionRevealedTimestamp\":null,\"checkedByProfessor\":false,\"professorCorrectness\":null,\"professorScore\":null,\"professorComment\":null}",
        ];

        for (const template of taskPayloads) {

            const payload = JSON.parse(template);

            payload.userId = userId;

            payload.semesterId = semesterId;
            payload.lectureId = lectureId;
            payload.courseId = courseId;

            http.post(
                K6Api.taskProgress.makeProgresse,
                JSON.stringify(payload),
                params
            );

            think(thinkTime);

            http.get(K6Api.auth.isAuthenticated, params);
            http.get(K6Api.auth.getUser, params);

            const refreshProgressRes = http.get(
                K6Api.taskProgress.getChapter(
                    userId,
                    semesterId,
                    lectureId,
                    courseId,
                    2
                ),
                params
            );

            check(refreshProgressRes, {
                'chapter refresh success': (r) =>
                    r.status === 200,
            });

            think(thinkTime);
        }
    });

    // -------------------------------------------------
    // Progress erneut laden
    // -------------------------------------------------
    group('Reload Progress', () => {

        http.get(K6Api.auth.isAuthenticated, params);
        http.get(K6Api.auth.getUser, params);

        const semesterReloadRes = http.get(
            K6Api.semesters.getSemesters(semesterId),
            params
        );

        check(semesterReloadRes, {
            'semester reload status 200': (r) =>
                r.status === 200,
        });

        const coursesReloadRes = http.get(
            K6Api.lectures.getCourses(
                userId,
                semesterId,
                lectureId
            ),
            params
        );

        check(coursesReloadRes, {
            'courses reload status 200': (r) =>
                r.status === 200,
        });

        http.get(
            K6Api.subscriptions.getSubscription(user.id),
            params
        );

        think(thinkTime);

        http.get(K6Api.auth.isAuthenticated, params);
        http.get(K6Api.auth.getUser, params);

        http.get(
            K6Api.subscriptions.getSubscription(user.id),
            params
        );

        const finalSemesterView = http.get(
            K6Api.semesters.getView,
            params
        );

        check(finalSemesterView, {
            'final semester view status 200': (r) =>
                r.status === 200,
        });

        think(thinkTime);
    });
}

export function teardown() {
    if(type !== "update"){
        annotate("END", type, scenario)
    }

}