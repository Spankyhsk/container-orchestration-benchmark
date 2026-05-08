import http from 'k6/http';
import { check, group } from 'k6';
import { think } from "../../shared/helpers/helpers.js"
import { K6Api } from "../../shared/api/k6-api.js";

export function idleUser(user, thinkTime){
    const params = {
        headers: {
            Authorization: `Bearer ${user.token}`,
            'Content-Type': 'application/json',
        },
    };

    const userId = user.id;
    let semesterId = "";
    let lectureId = "";

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

        think(thinkTime)
    });

    group('Dashboard / Subscription', () => {

        const subRes = http.get(
            K6Api.subscriptions.getSubscription(userId),
            params
        );

        check(subRes, {
            'subscription status 200': (r) => r.status === 200,
        });

        think(thinkTime);

        const semesterRes = http.get(
            K6Api.semesters.getView,
            params
        );

        check(semesterRes, {
            'semester view status 200': (r) => r.status === 200,
            'semester response valid': (r) => r.json().length > 0,
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

        http.get(
            K6Api.subscriptions.getSubscription(userId),
            params
        );


        think(thinkTime);
    });

    group('Jump back to Dashboard', () => {
        http.get(K6Api.auth.getUser, params);
        http.get(K6Api.auth.isAuthenticated, params);

        http.get(
            K6Api.subscriptions.getSubscription(userId),
            params
        );

        const semesterRes = http.get(
            K6Api.semesters.getView,
            params
        );

        check(semesterRes, {
            'semester view status 200': (r) => r.status === 200,
            'semester response valid': (r) => r.json().length > 0,
        });

        think(thinkTime);
    })

    group('Auth refresh', () => {
        http.get(K6Api.auth.getUser, params);
        http.get(K6Api.auth.isAuthenticated, params);

        http.get(
            K6Api.subscriptions.getSubscription(userId),
            params
        );

        const semesterRes = http.get(
            K6Api.semesters.getView,
            params
        );

        check(semesterRes, {
            'semester view status 200': (r) => r.status === 200,
            'semester response valid': (r) => r.json().length > 0,
        });

        think(thinkTime);
    })
}