import http from 'k6/http';
import { K6Api } from "../../shared/api/k6-api.js";
import {randomBetween, think} from "../../shared/helpers/helpers.js";

export function professorUser(user, thinkTime, ctx) {
    const params = {
        headers: {
            Authorization: `Bearer ${user.token}`,
            'Content-Type': 'application/json',
        },
    };

    const userId = user.id;
    const examId = ctx.examId;

    http.get(K6Api.auth.getUser, params);
    http.get(K6Api.auth.isAuthenticated, params);
    http.get(K6Api.auth.getUser, params);

    http.get(K6Api.subscriptions.getSubscription(userId), params);
    http.get(K6Api.semesters.getView, params);

    think(thinkTime);

    http.get(K6Api.auth.isAuthenticated, params);
    http.get(K6Api.auth.getUser, params);

    http.get(K6Api.exam.getExamList, params)

    http.get(K6Api.auth.isAuthenticated, params);
    http.get(K6Api.auth.getUser, params);

    for(let i = 0; i < randomBetween(thinkTime[0], thinkTime[1]); i++){
        http.get(K6Api.exam.getExam(examId), params)
        http.get(K6Api.exam.getListExamUSer(examId), params)
        http.get(K6Api.exam.getStudentGrants(examId), params)
        http.get(K6Api.subscriptions.getSubscriptionList, params)
    }

    http.get(K6Api.auth.isAuthenticated, params);
    http.get(K6Api.auth.getUser, params);

    http.get(K6Api.exam.getExamList, params)

    think(thinkTime);

    http.get(K6Api.auth.isAuthenticated, params);
    http.get(K6Api.auth.getUser, params);

    http.get(K6Api.subscriptions.getSubscription(userId), params);
    http.get(K6Api.semesters.getView, params);
}