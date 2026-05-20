import http from 'k6/http';
import { check, group } from 'k6';
import { think } from "../../shared/helpers/helpers.js"
import { K6Api } from "../../shared/api/k6-api.js";

export function professorUser(user, thinkTime, ctx){
    const params = {
        headers: {
            Authorization: `Bearer ${user.token}`,
            'Content-Type': 'application/json',
        },
    };

    const userId = user.id;


    // ------------------------------------------------------
    // Auth / Session Requests
    // ------------------------------------------------------

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
    })

    // ---------------------------------------------------------
    // Dashboard / Subscription
    // ---------------------------------------------------------
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

        think(thinkTime);
    })

    group('Statistic Dashboard', () => {
        http.get(K6Api.auth.isAuthenticated, params);

        http.get(K6Api.auth.getUser, params);

        http.get(K6Api.user.getUserList, params);

        http.get(K6Api.subscriptions.getSubscriptionList, params);

        http.get(K6Api.lectures.getLectureList, params);

        http.get(K6Api.semesters.getSemesterList, params);

        http.get(K6Api.courses.getCoursesList, params);

        const statistic = http.get(K6Api.taskProgress.getTaskProgressList, params);

        check(statistic, {
            'statistic View status 200': (r) => r.status === 200
        });

        think(thinkTime);
    })

    group('Ranking Dashboard', () => {
        http.get(K6Api.auth.isAuthenticated, params);

        http.get(K6Api.auth.getUser, params);

        http.get(K6Api.lectures.getLectureList, params);

        http.get(K6Api.semesters.getSemesterList, params);

        http.get(K6Api.courses.getCoursesList, params);

        http.get(K6Api.quizduel.getQuizduelOriginalList, params);

        http.get(K6Api.quiztasksets.getQuiztasksetsList, params);

        http.get(K6Api.user.getUserList, params);

        http.get(K6Api.subscriptions.getSubscriptionList, params);

        http.get(K6Api.taskProgress.getTaskProgressList, params);

        http.get(K6Api.exam.getExamList, params);

        const ranking = http.get(K6Api.exam.getExamSolutionList, params);

        check(ranking, {
            'ranking View status 200': (r) => r.status === 200
        });

        think(thinkTime)


    })

    group('Kurs-Analyse Dashboard', () => {
        http.get(K6Api.auth.isAuthenticated, params);

        http.get(K6Api.auth.getUser, params);

        const semestersRes = http.get(K6Api.semesters.getSemesterList, params);

        const semesterData = semestersRes.json();

        const semester = semesterData.find(x => x.name === 'SS26')

        const semesterId = semester._id;

        const lecturesRes = http.get(K6Api.lectures.getLectureList, params);

        const lectureData = lecturesRes.json();

        const lecture = lectureData.find(x => x.name === 'Scala 3')

        const lectureId = lecture._id;

        const coursesRes = http.get(K6Api.courses.getCoursesList, params);

        const courseData = coursesRes.json();

        const course = courseData.find(x => x.title === 'Learn Scala 3 The Fast Way')

        const courseId = course._id;

        const taskAnalyticsload1 = http.get(K6Api.taskProgress.getCourseTaskAnalytics(semesterId, lectureId, courseId), params);

        check(taskAnalyticsload1, {
            'kurs-analyse View status 200': (r) => r.status === 200
        });

        think(thinkTime);

        const taskAnalyticsload2 = http.get(K6Api.taskProgress.getCourseTaskAnalytics(semesterId, lectureId, courseId), params);

        check(taskAnalyticsload2, {
            'kurs-analyse View status 200': (r) => r.status === 200
        });

        think(thinkTime);

    })

    group('Reflaction task Dashboard', () => {
        http.get(K6Api.auth.isAuthenticated, params);

        http.get(K6Api.auth.getUser, params);

        http.get(K6Api.user.getUserPublicList, params);

        http.get(K6Api.courses.getCoursesList, params);

        http.get(K6Api.taskProgress.getTaskProgressList, params);

        think(thinkTime);
    })

    group('Course synch', () => {
        http.get(K6Api.auth.isAuthenticated, params);

        http.get(K6Api.auth.getUser, params);

        http.get(K6Api.courses.getCoursesList, params);

        const res = http.post(K6Api.parser.sychronize, {}, params);

        check(res, {
            'Course synchronize status 200': (r) => r.status === 200
        });

        think(thinkTime);
    })

    group('Edit Course View', () => {
        http.get(K6Api.auth.isAuthenticated, params);

        http.get(K6Api.auth.getUser, params);

        const coursesRes = http.get(K6Api.courses.getCoursesList, params);

        const courseData = coursesRes.json();

        const course = courseData.find(x => x.title === 'Learn Scala 3 The Fast Way')

        const courseId = course._id;

        think(thinkTime);

        const chapterOverview = http.get(K6Api.courses.getCourse(courseId), params);

        check(chapterOverview, {
            'Chapter overview status 200': (r) => r.status === 200
        });

        think(thinkTime);

        const courseChapters = chapterOverview.json();

        const chapter = courseChapters.chapters.find(
            x => x.title === "Ch82_SwingGui"
        );

        const chapterId = chapter._id;

        const chaptereditor = http.get(K6Api.courses.getChapterEditor(courseId, chapterId), params);

        check(chaptereditor, {
            'chapter editor view status 200': (r) => r.status === 200
        });
    })

    group('Jump Back to Dashboard', () => {
        http.get(K6Api.auth.isAuthenticated, params);

        http.get(K6Api.auth.getUser, params);

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
            'semester response valid': (r) => r.json().length > 0,
        });

        think(thinkTime);
    })
}