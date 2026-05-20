import http from 'k6/http';
import { K6Api } from "../../shared/api/k6-api.js";
import {think} from "../../shared/helpers/helpers.js";

export function examUser(user, thinkTime, ctx) {
    const params = {
        headers: {
            Authorization: `Bearer ${user.token}`,
            'Content-Type': 'application/json',
        },
    };

    const userId = user.id;
    const examId = ctx?.examId;
    const authCode = ctx?.password;
    let semesterId = "";
    let lectureId = "";

    // -------------------------------------------------
    // EXAM FLOW
    // -------------------------------------------------

    http.get(K6Api.auth.getUser, params);
    http.get(K6Api.auth.isAuthenticated, params);
    http.get(K6Api.auth.getUser, params);

    http.get(K6Api.subscriptions.getSubscription(userId), params);
    http.get(K6Api.semesters.getView, params);

    think(thinkTime);

    http.get(K6Api.auth.isAuthenticated, params);
    http.get(K6Api.auth.getUser, params);

    http.get(K6Api.exam.getListUserExam(userId), params);

    think(thinkTime);

    http.get(K6Api.auth.isAuthenticated, params);
    http.get(K6Api.auth.getUser, params);

    http.post(
        K6Api.exam.postAuthExam(examId),
        JSON.stringify({
            authCode: `${authCode}`,
        }),
        params
    );


    think(thinkTime);

    http.post(
        K6Api.exam.postAuthExam(examId),
        JSON.stringify({
            authCode: `${authCode}`,
        }),
        params
    );

    think(thinkTime);

    // -------------------------------------------------
    // EXAM SOLUTION FLOW
    // -------------------------------------------------

    const examSolutions = [

        {
            payload: {
                _id: "6a0b2e6038e0aa9eccd4025d",
                userId,
                examId,
                examTaskId: "1",
                solvedWith: [],
                points: -1,
                runId: "776a562b-024f-4f6f-be6b-720a310b50bf",
                touchedAt: 1779117679467,
                reviewedAt: 0,
                submittedAt: 0,
            },
        },

        {
            payload: {
                _id: "6a0b2e6038e0aa9eccd4025e",
                userId,
                examId,
                examTaskId: "2",
                solvedWith: [
                    {
                        _id: "0",
                        solution: "",
                        correctness: false,
                    },
                ],
                points: -1,
                runId: "776a562b-024f-4f6f-be6b-720a310b50bf",
                touchedAt: 1779117682781,
                reviewedAt: 0,
                submittedAt: 0,
            },
        },

        {
            payload: {
                _id: "6a0b2e6038e0aa9eccd4025e",
                userId,
                examId,
                examTaskId: "2",
                solvedWith: [
                    {
                        _id: "0",
                        solution: "\"Ada Lovelace\"",
                        correctness: false,
                    },
                ],
                points: -1,
                runId: "776a562b-024f-4f6f-be6b-720a310b50bf",
                touchedAt: 1779117682781,
                reviewedAt: 0,
                submittedAt: 0,
            },
        },

        {
            payload: {
                _id: "6a0b2e6038e0aa9eccd4025f",
                userId,
                examId,
                examTaskId: "3",
                solvedWith: [
                    {
                        _id: "0",
                        solution: "1",
                        correctness: false,
                    },
                ],
                points: -1,
                runId: "776a562b-024f-4f6f-be6b-720a310b50bf",
                touchedAt: 1779117699341,
                reviewedAt: 0,
                submittedAt: 0,
            },
        },

        {
            payload: {
                _id: "6a0b2e6038e0aa9eccd40261",
                userId,
                examId,
                examTaskId: "5",
                solvedWith: [
                    {
                        solution:
                            "val a = 1\nval b = (a + a) * 2\nval c = b\nval greeting = c + b",
                        correctness: false,
                    },
                ],
                points: -1,
                runId: "776a562b-024f-4f6f-be6b-720a310b50bf",
                touchedAt: 1779117709511,
                reviewedAt: 0,
                submittedAt: 0,
            },
        },

    ];

    // -------------------------------------------------
    // LOOP
    // -------------------------------------------------

    for (const examSolution of examSolutions) {

        http.get(K6Api.auth.isAuthenticated, params);
        http.get(K6Api.auth.getUser, params);

        http.get(K6Api.exam.getExamUser(examId), params);

        think(thinkTime);

        http.put(
            K6Api.exam.getExamSolution(examId),
            JSON.stringify(examSolution.payload),
            params
        );

        think(thinkTime);

        http.get(K6Api.exam.getExamUser(examId), params);
    }

    // -------------------------------------------------
    // SUBMIT EXAM
    // -------------------------------------------------

    think(thinkTime);
    http.put(
        K6Api.exam.getExamSubmit(examId),
        JSON.stringify({}),
        params
    );

    think(thinkTime);


    http.get(K6Api.auth.isAuthenticated, params);
    http.get(K6Api.auth.getUser, params);

    http.get(K6Api.exam.getListUserExam(userId), params);

    think(thinkTime);

    http.get(K6Api.subscriptions.getSubscription(userId), params);
    http.get(K6Api.semesters.getView, params);
}