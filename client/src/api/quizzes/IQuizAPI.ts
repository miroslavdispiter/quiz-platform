import type { QuestionData } from "../../types/moderator/QuestionData";

export type QuizStatus = "PENDING" | "APPROVED" | "REJECTED";

// What the moderator sends when creating / editing a quiz
// (the author is NOT sent - the server takes it from the logged-in user)
export interface QuizInput {
  title: string;
  duration: number; // seconds
  questions: QuestionData[];
}

// Quiz in lists (without questions)
export interface QuizSummary {
  _id: string;
  title: string;
  duration: number;
  author_id: number;
  author_name: string;
  status: QuizStatus;
  rejection_reason: string | null;
  question_count: number;
  created_at: string;
}

// Question of one quiz - players do not get correct_answers
export interface QuizQuestion {
  text: string;
  options: string[];
  points: number;
  correct_answers?: string[];
}

// One whole quiz
export interface Quiz {
  _id: string;
  title: string;
  duration: number;
  author_id: number;
  author_name: string;
  status: QuizStatus;
  rejection_reason: string | null;
  created_at: string;
  questions: QuizQuestion[];
}

// One answer of the player
export interface AnswerInput {
  question_index: number;
  selected: string[];
}

export interface SubmitResponse {
  result_id: string;
  status: string;
  message: string;
}

export interface IQuizAPI {
  createQuiz(data: QuizInput): Promise<Quiz>;
  updateQuiz(quizId: string, data: QuizInput): Promise<Quiz>;
  deleteQuiz(quizId: string): Promise<void>;
  getAllQuizzes(): Promise<QuizSummary[]>;
  getMyQuizzes(): Promise<QuizSummary[]>;
  getApprovedQuizzes(): Promise<QuizSummary[]>;
  getQuizById(quizId: string): Promise<Quiz>;
  reviewQuiz(quizId: string, status: "APPROVED" | "REJECTED", rejection_reason?: string): Promise<Quiz>;
  submitAnswers(quizId: string, answers: AnswerInput[], timeSpent: number): Promise<SubmitResponse>;
}
