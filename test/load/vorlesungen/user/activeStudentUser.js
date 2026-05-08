import http from 'k6/http';
import { K6Api } from "../../shared/api/k6-api.js";

export function activeStudentUser(user, thinkTime){
    const params = {
        headers: {
            Authorization: `Bearer ${user.token}`,
            'Content-Type': 'application/json',
        },
    };

}

function courseScala3Flow(user, params, thinkTime) {

    // -------------------------------------------------
    // Auth / Session Requests
    // -------------------------------------------------
    http.get(K6Api.auth.getUser, params);
    http.get(K6Api.auth.isAuthenticated, params);
    http.get(K6Api.auth.getUser, params);


    // -------------------------------------------------
    // Dashboard / Subscription
    // -------------------------------------------------
    http.get(K6Api.subscriptions.getSubscription(user.id), params);
    sleep(thinkTime);

    const semesterRes = http.get(K6Api.semesters.getView, params);

    const semesters = semesterRes.json()
    const semester = semesters[0]
    const semesterId = semester._id;

    // Scala 3 Lecture suchen
    const lecture = semester.lectures.find(
        l => l.name === 'Scala 3'
    );

    const lectureId = lecture._id;
    http.get(K6Api.subscriptions.getSubscriptionList, params);

    sleep(thinkTime);

    http.get(K6Api.auth.getUser, params);
    http.get(K6Api.auth.isAuthenticated, params);

    http.get(K6Api.subscriptions.getSubscription(user.id), params);
    http.get(K6Api.auth.getUser, params);
    http.get(K6Api.auth.isAuthenticated, params);

    http.get(K6Api.semesters.getSemesters(semesterId), params);
    sleep(thinkTime);

    // -------------------------------------------------
    // Courses laden
    // -------------------------------------------------
    const coursesRes = http.get(
        K6Api.lectures.getCourses(user.id, semesterId, lectureId),
        params
    );

    const lectureData = coursesRes.json();

    const course = lectureData.courses.find(
        c => c.title === 'Learn Scala 3 The Fast Way'
    );

    const courseId = course._id;

    sleep(thinkTime);
    // -------------------------------------------------
    // Kapitel 2 öffnen
    // -------------------------------------------------
    http.get(K6Api.subscriptions.getSubscription(user.id), params);
    http.get(K6Api.auth.isAuthenticated, params);
    http.get(K6Api.auth.getUser, params);


    http.get(
        K6Api.taskProgress.getChapter(user.id, semesterId, lectureId, courseId, 2),
        params
    );

    http.get(
        K6Api.courses.getChapter(courseId, 2)
    )

    sleep(thinkTime);
    // -------------------------------------------------
    // Tasks bearbeiten
    // -------------------------------------------------
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
    ]

    for (const template of taskPayloads) {

        const payload = JSON.parse(template);

        payload.userId = user.id;

        payload.semesterId = semesterId;
        payload.lectureId = lectureId;
        payload.courseId = courseId;

        http.post(
            `${baseUrl}/taskProgresses`,
            JSON.stringify(payload),
            params
        );

        sleep(thinkTime);

        http.get(K6Api.auth.isAuthenticated, params);
        http.get(K6Api.auth.getUser, params);

        http.get(
            K6Api.taskProgress.getChapter(user.id, semesterId, lectureId, courseId, 2),
            params
        );
        sleep(thinkTime);
    }

    // -------------------------------------------------
    // Progress erneut laden
    // -------------------------------------------------
    http.get(K6Api.auth.isAuthenticated, params);
    http.get(K6Api.auth.getUser, params);

    http.get(K6Api.semesters.getSemesters(semesterId), params);

    http.get(
        K6Api.lectures.getCourses(user.id, semesterId, lectureId),
        params
    );

    http.get(K6Api.subscriptions.getSubscription(user.id), params);

    sleep(thinkTime);

    http.get(K6Api.auth.isAuthenticated, params);
    http.get(K6Api.auth.getUser, params);

    http.get(K6Api.subscriptions.getSubscription(user.id), params);

    http.get(K6Api.semesters.getView, params);

    sleep(thinkTime);
}