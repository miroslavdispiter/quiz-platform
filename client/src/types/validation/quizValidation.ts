import type { QuizInput } from "../../api/quizzes/IQuizAPI";

// Same limits as on the server (quiz_service/app/WebAPI/validation/QuizValidation.py)
export const QUIZ_LIMITS = {
  TITLE_MIN: 3,
  TITLE_MAX: 100,
  DURATION_MIN: 10,
  DURATION_MAX: 3600,
  QUESTIONS_MAX: 50,
  OPTIONS_MIN: 2,
  OPTIONS_MAX: 10,
  POINTS_MIN: 1,
  POINTS_MAX: 100,
};

/**
 * Returns null if the quiz is valid, otherwise the first error message.
 */
export function validateQuiz(quiz: QuizInput): string | null {
  const title = quiz.title.trim();
  if (title.length < QUIZ_LIMITS.TITLE_MIN || title.length > QUIZ_LIMITS.TITLE_MAX) {
    return `Quiz title must have ${QUIZ_LIMITS.TITLE_MIN}-${QUIZ_LIMITS.TITLE_MAX} characters`;
  }

  if (
    !Number.isInteger(quiz.duration) ||
    quiz.duration < QUIZ_LIMITS.DURATION_MIN ||
    quiz.duration > QUIZ_LIMITS.DURATION_MAX
  ) {
    return `Duration must be between ${QUIZ_LIMITS.DURATION_MIN} and ${QUIZ_LIMITS.DURATION_MAX} seconds`;
  }

  if (quiz.questions.length === 0) {
    return "Quiz must have at least one question";
  }
  if (quiz.questions.length > QUIZ_LIMITS.QUESTIONS_MAX) {
    return `Quiz can have at most ${QUIZ_LIMITS.QUESTIONS_MAX} questions`;
  }

  for (let i = 0; i < quiz.questions.length; i++) {
    const q = quiz.questions[i];
    const label = `Question ${i + 1}`;

    if (q.text.trim() === "") {
      return `${label}: text is required`;
    }

    if (!Number.isInteger(q.points) || q.points < QUIZ_LIMITS.POINTS_MIN || q.points > QUIZ_LIMITS.POINTS_MAX) {
      return `${label}: points must be between ${QUIZ_LIMITS.POINTS_MIN} and ${QUIZ_LIMITS.POINTS_MAX}`;
    }

    if (q.options.length < QUIZ_LIMITS.OPTIONS_MIN || q.options.length > QUIZ_LIMITS.OPTIONS_MAX) {
      return `${label}: must have between ${QUIZ_LIMITS.OPTIONS_MIN} and ${QUIZ_LIMITS.OPTIONS_MAX} options`;
    }

    const options = q.options.map((o) => o.trim());
    if (options.some((o) => o === "")) {
      return `${label}: options cannot be empty`;
    }
    if (new Set(options).size !== options.length) {
      return `${label}: options must be different from each other`;
    }

    if (q.correct_answers.length === 0) {
      return `${label}: select at least one correct answer`;
    }
    if (q.correct_answers.some((a) => !options.includes(a.trim()))) {
      return `${label}: every correct answer must be one of the options`;
    }
  }

  return null;
}
