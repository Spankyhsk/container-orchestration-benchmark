const BASE_URL = __ENV.BASE_URL;

const apiUrl = `http://api.${BASE_URL}`;
const aiapiUrl = `http://ai-api.${BASE_URL}`;
const frontendUrl = `http://${BASE_URL}`;

export const K6Api = {
    auth: {
        getUser: `${apiUrl}/auth/user`,
        isAuthenticated: `${apiUrl}/auth/is-authenticated`,
        login: `${apiUrl}/auth/signin`
    },
    subscriptions: {
        getSubscription: (userId) => `${apiUrl}/subscriptions/user/${userId}`,
        getSubscriptionList: `${apiUrl}/subscriptions`
    },
    lectures: {
        getCourses: (userId, semesterId, lectureId) => `${apiUrl}/users/${userId}/semesters/${semesterId}/lectures/${lectureId}/courses`,
        getLectures: (userId, semesterId) => `${apiUrl}/users/${userId}/semesters/${semesterId}/lectures`,
        getLectureList: `${apiUrl}/lectures`
    },
    taskProgress: {
        getChapter: (userId, semesterId, lectureId, courseId, chapterId) => `${apiUrl}/taskProgresses/user/${userId}/semester/${semesterId}/lecture/${lectureId}/course/${courseId}/chapter/${chapterId}`,
        makeProgresse: `${apiUrl}/taskProgresses`
    },
    semesters: {
        getView: `${apiUrl}/semesters/view`,
        getSemesters: (semesterId) => `${apiUrl}/semesters/${semesterId}`,
        getSemesterList: `${apiUrl}/semesters`
    },
    courses: {
        getChapter: (courseId, chapterId) => `${apiUrl}/courses/${courseId}/${chapterId}`,
        getCourseSubscribedList: `${apiUrl}/courses/subscribed/list`
    },
    quizduel: {
        getQuizduel: `${apiUrl}/quizduel`,
    },
    quiztasksets: {
        getQuiztasksetsList: `${apiUrl}/quiztasksets`,
    },
    courseDeadline: {
        getCoursesDeadlineSub: `${apiUrl}/course-deadlines/subscribed`
    },
    quizduelDeadline: {
        getQuizduellDeadlineSub: `${apiUrl}/quiz-duel-deadlines/subscribed`
    },
    exam: {
        getListUserExam: (userId) => `${apiUrl}/user/${userId}`,
    }
};