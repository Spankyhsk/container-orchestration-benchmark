import http from "k6/http";
import {K6Api} from "../api/k6-api.js";

export function createExam(){

    const professorPayload = {
        email: `professor@mail.com`,
        password: `Passwort123`
    }

    const res = http.post(
        K6Api.auth.login,
        JSON.stringify(professorPayload),
        {
            headers: { "Content-Type": "application/json" }
        }
    );

    const token = (r) => r.json("accessToken");

    const params = {
        headers: {
            Authorization: `Bearer ${token(res)}`,
            'Content-Type': 'application/json',
        },
    };

    const semesterRes = http.get(K6Api.semesters.getSemesterList, params);

    const semester = semesterRes.json().find(x => x.name === 'SS26');

    const lecturesRes = http.get(K6Api.lectures.getLectureList, params);

    const lecture = lecturesRes.json().find(x => x.name === 'Scala 3');

    const courseRes = http.get(K6Api.courses.getCoursesList, params);

    const course = courseRes.json().find(x => x.title === 'Learn Scala 3 The Fast Way');

    const examPayload = {
        name: "Scala 3 - SS26",
        date: Date.now(),
        duration: 180,
        lecture: lecture._id,
        semester: semester._id,
        isOpen: false,
        tasks: [],
        startTime: -1,
        endTime: -1,
        examType: "exam",
        password: "",
        gradeThresholds: {
            top: 1,
            bottom: 0.5,
        },
    };

    const createExamRes = http.post(
        K6Api.exam.createExam,
        JSON.stringify(examPayload),
        params
    )

    const examId = createExamRes.json("_id");

    const chapterIds = ["2", "3"];

    const chapterPayload = chapterIds.map(chapterId => ({
        courseId: course._id,
        chapterId,
    }));

    const updateExamRes = http.put(
        K6Api.exam.updateChapters(examId),
        JSON.stringify(chapterPayload),
        params
    )

    const exam = updateExamRes.json();

    const examStartPayload = {
        ...exam
    };

    const startExamRes = http.put(
        K6Api.exam.startExam(examId),
        JSON.stringify(examStartPayload),
        params
    )

    const password = startExamRes.json("password")

    return {examId: examId, password: password}

}