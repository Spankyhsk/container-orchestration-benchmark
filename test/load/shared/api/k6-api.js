const BASE_URL = __ENV.BASE_URL;

const apiUrl = `http://api.${BASE_URL}`;
const aiapiUrl = `http://ai-api.${BASE_URL}`;
const frontendUrl = `http://${BASE_URL}`;

export const K6Api = {
    auth: {
        getUser: `${apiUrl}/auth/user`,
        isAuthenticated: `${apiUrl}/auth/is-authenticated`
    },
    subscriptions: {
        getSubscription: (userId) => `${apiUrl}/subscriptions/user/${userId}`,
        getSubscriptionList: `${apiUrl}/subscriptions`
    },
    lectures: {
        getCourses: (userId, semesterId, lectureId) => `${apiUrl}/users/${userId}/semesters/${semesterId}/lectures/${lectureId}/courses`
    },
    taskProgress: {
        getChapter: (userId, semesterId, lectureId, courseId, chapterId) => `${apiUrl}/taskProgresses/user/${userId}/semester/${semesterId}/lecture/${lectureId}/course/${courseId}/chapter/${chapterId}`,
        makeProgresse: `${apiUrl}/taskProgresses`
    },
    semesters: {
        getView: `${apiUrl}/semesters/view`,
        getSemesters: (semesterId) => `${apiUrl}/semesters/${semesterId}`
    },
    courses: {
        getChapter: (courseId, chapterId) => `${apiUrl}/courses/${courseId}/${chapterId}`
    }
};