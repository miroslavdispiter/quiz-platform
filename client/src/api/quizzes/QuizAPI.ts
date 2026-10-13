import type {
  AnswerInput,
  IQuizAPI,
  Quiz,
  QuizInput,
  QuizSummary,
  SubmitResponse,
} from "./IQuizAPI";

// All quiz requests go to the MAIN SERVER, which forwards them to the Quiz Service.
const BASE_URL = import.meta.env.VITE_API_URL;

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem("access_token");

  const response = await fetch(`${BASE_URL}/quizzes${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: token ? `Bearer ${token}` : "",
    },
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    // Our services return {"error": "..."}, flask-jwt-extended returns {"msg": "..."}
    throw new Error(data?.error || data?.message || data?.msg || `Request failed (${response.status})`);
  }

  return data as T;
}

export class QuizAPI implements IQuizAPI {
  createQuiz(data: QuizInput): Promise<Quiz> {
    return request<Quiz>("/", { method: "POST", body: JSON.stringify(data) });
  }

  updateQuiz(quizId: string, data: QuizInput): Promise<Quiz> {
    return request<Quiz>(`/${quizId}`, { method: "PUT", body: JSON.stringify(data) });
  }

  async deleteQuiz(quizId: string): Promise<void> {
    await request(`/${quizId}`, { method: "DELETE" });
  }

  // Admin - all quizzes
  getAllQuizzes(): Promise<QuizSummary[]> {
    return request<QuizSummary[]>("/");
  }

  // Moderator - only his quizzes
  getMyQuizzes(): Promise<QuizSummary[]> {
    return request<QuizSummary[]>("/mine");
  }

  // Players - only approved quizzes
  getApprovedQuizzes(): Promise<QuizSummary[]> {
    return request<QuizSummary[]>("/published");
  }

  getQuizById(quizId: string): Promise<Quiz> {
    return request<Quiz>(`/${quizId}`);
  }

  reviewQuiz(quizId: string, status: "APPROVED" | "REJECTED", rejection_reason?: string): Promise<Quiz> {
    return request<Quiz>(`/${quizId}/review`, {
      method: "PATCH",
      body: JSON.stringify({ status, rejection_reason }),
    });
  }

  submitAnswers(quizId: string, answers: AnswerInput[], timeSpent: number): Promise<SubmitResponse> {
    return request<SubmitResponse>(`/${quizId}/submit`, {
      method: "POST",
      body: JSON.stringify({ answers, time_spent: timeSpent }),
    });
  }
}

export const quizAPI = new QuizAPI();
