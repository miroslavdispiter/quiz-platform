import React, { useCallback, useEffect, useState } from "react";
import { quizAPI } from "../../api/quizzes/QuizAPI";
import type { QuizSummary } from "../../api/quizzes/IQuizAPI";
import { QuizApprovalTable } from "../../components/admin/quizzes/QuizApprovalTable";
import { ErrorAlert } from "../../components/ui/ErrorAlert";
import { SuccessAlert } from "../../components/ui/SuccessAlert";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { socketService, type QuizSocketEvent } from "../../services/socketService";

const ModeratorsQuizPage: React.FC = () => {
  const [quizzes, setQuizzes] = useState<QuizSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Reload the list (used after real-time events and after actions)
  const fetchQuizzes = useCallback(async () => {
    try {
      const data = await quizAPI.getMyQuizzes();
      setQuizzes(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load quizzes");
    }
  }, []);

  useEffect(() => {
    // First load
    quizAPI
      .getMyQuizzes()
      .then((data) => setQuizzes(data))
      .catch((err: Error) => setError(err.message || "Failed to load quizzes"))
      .finally(() => setLoading(false));

    // REAL TIME: the admin approved or rejected one of my quizzes
    const handleReviewed = (data: QuizSocketEvent) => {
      if (data.status === "APPROVED") {
        setSuccess(data.message);
      } else {
        setError(`${data.message}. Reason: ${data.rejection_reason || "no reason"}`);
      }
      fetchQuizzes();
    };

    socketService.on("quiz_reviewed", handleReviewed);
    return () => socketService.off("quiz_reviewed", handleReviewed);
  }, [fetchQuizzes]);

  const handleDelete = async (quizId: string, title: string) => {
    if (!window.confirm(`Are you sure you want to delete quiz "${title}"?`)) return;
    try {
      await quizAPI.deleteQuiz(quizId);
      setSuccess(`Deleted quiz "${title}"`);
      fetchQuizzes();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete quiz");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-violet-50 to-indigo-50 px-6 py-12">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-violet-600 to-indigo-600">
            My Quizzes
          </h1>
          <p className="mt-1 text-gray-500">
            View and track your quizzes. You will be notified in real time if the admin approves or rejects them.
          </p>
        </div>

        {error && <ErrorAlert message={error} onDismiss={() => setError("")} />}
        {success && <SuccessAlert message={success} onDismiss={() => setSuccess("")} />}

        {loading ? (
          <LoadingSpinner message="Loading quizzes..." />
        ) : (
          <QuizApprovalTable
            quizzes={quizzes}
            onDeleteClick={handleDelete}
            showReviewButton={false}
            mode="moderator"
          />
        )}
      </div>
    </div>
  );
};

export default ModeratorsQuizPage;
