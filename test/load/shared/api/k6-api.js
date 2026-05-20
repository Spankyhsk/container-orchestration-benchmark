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
        makeProgresse: `${apiUrl}/taskProgresses`,
        getTaskProgressList: `${apiUrl}/taskProgresses`,
        getCourseTaskAnalytics: (semesterId, lectureId, courseId) => `${apiUrl}/taskProgresses/analytics/course/${courseId}/semester/${semesterId}/lecture/${lectureId}`
    },
    semesters: {
        getView: `${apiUrl}/semesters/view`,
        getSemesters: (semesterId) => `${apiUrl}/semesters/${semesterId}`,
        getSemesterList: `${apiUrl}/semesters`
    },
    courses: {
        getChapter: (courseId, chapterId) => `${apiUrl}/courses/${courseId}/${chapterId}`,
        getCourseSubscribedList: `${apiUrl}/courses/subscribed/list`,
        getCoursesList: `${apiUrl}/courses`,
        getCourse: (courseId) => `${apiUrl}/courses/${courseId}`,
        getChapterEditor: (courseId, chapterId) => `${apiUrl}/courses/${courseId}/chapters/${chapterId}/source`
    },
    quizduel: {
        getQuizduel: `${apiUrl}/quizduel`,
        getQuizduelOriginalList: `${apiUrl}/quizduels/original`
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
        getExamList: `${apiUrl}/exam`,
        getExamSolutionList: `${apiUrl}/exam-solution`,
        createExam: `${apiUrl}/exam`,
        updateChapters: (examId) => `${apiUrl}/exam/assign-tasks/${examId}`,
        startExam: (examId) => `${apiUrl}/exam/start/${examId}`,
        getUserExam: (examId, userId) => `${apiUrl}/exam/${examId}/user/${userId}`,
        postAuthExam: (examId) => `${apiUrl}/exam-solution/auth/${examId}`,
        getStudentGrants: (examId) => `${apiUrl}/exam/${examId}/student-grants`,
        getExamSolution: (examId) => `${apiUrl}/exam-solution/${examId}`,
        getExamUser: (examId) => `${apiUrl}/exam-solution/user/${examId}`,
        getExamSubmit: (examId) => `${apiUrl}/exam/submit/${examId}`,
        getExam: (examId) => `${apiUrl}/exam/${examId}`,
        getListExamUSer: (examId) => `${apiUrl}/exam-solution/exam/${examId}`
    },
    user: {
        getUserList: `${apiUrl}/users`,
        getUserPublicList: `${apiUrl}/users/public`
    },
    parser: {
        sychronize: `${apiUrl}/synchronize`
    }
};