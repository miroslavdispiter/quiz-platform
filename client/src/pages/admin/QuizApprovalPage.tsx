import React, { useCallback, useEffect, useState } from "react";
import { quizAPI } from "../../api/quizzes/QuizAPI";
import type { QuizSummary } from "../../api/quizzes/IQuizAPI";
import { QuizApprovalTable } from "../../components/admin/quizzes/QuizApprovalTable";
import { QuizReviewDialog } from "../../components/admin/quizzes/QuizReviewDialog";
import { socketService, type QuizSocketEvent } from "../../services/socketService";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { ErrorAlert } from "../../components/ui/ErrorAlert";
import { SuccessAlert } from "../../components/ui/SuccessAlert";
import DownloadReportButton from "../../components/admin/quizzes/DownloadReportButton";

const QuizApprovalPage: React.FC = () => {
  const [quizzes, setQuizzes] = useState<QuizSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [selectedQuiz, setSelectedQuiz] = useState<QuizSummary | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  // Reload the list (used after real-time events and after actions)
  const fetchQuizzes = useCallback(async () => {
    try {
      const data = await quizAPI.getAllQuizzes();
      setQuizzes(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load quizzes");
    }
  }, []);

  useEffect(() => {
    // First load
    quizAPI
      .getAllQuizzes()
      .then((data) => setQuizzes(data))
      .catch((err: Error) => setError(err.message || "Failed to load quizzes"))
      .finally(() => setLoading(false));

    // REAL TIME: a moderator created (or edited) a quiz -> it appears here immediately
    const handleCreated = (data: QuizSocketEvent) => {
      setSuccess(data.message);
      fetchQuizzes();
    };
    const handleDeleted = () => fetchQuizzes();

    socketService.on("quiz_created", handleCreated);
    socketService.on("quiz_deleted", handleDeleted);
    return () => {
      socketService.off("quiz_created", handleCreated);
      socketService.off("quiz_deleted", handleDeleted);
    };
  }, [fetchQuizzes]);

  const handleApprove = async () => {
    if (!selectedQuiz) return;
    try {
      await quizAPI.reviewQuiz(selectedQuiz._id, "APPROVED");
      setSuccess(`Quiz "${selectedQuiz.title}" approved`);
      setDialogOpen(false);
      fetchQuizzes();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to approve quiz");
    }
  };

  const handleReject = async (reason: string) => {
    if (!selectedQuiz) return;
    try {
      await quizAPI.reviewQuiz(selectedQuiz._id, "REJECTED", reason);
      setSuccess(`Quiz "${selectedQuiz.title}" rejected`);
      setDialogOpen(false);
      fetchQuizzes();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reject quiz");
    }
  };

  const handleDelete = async (quizId: string, title: string) => {
    if (!window.confirm(`Delete quiz "${title}"? This action cannot be undone.`)) return;
    try {
      await quizAPI.deleteQuiz(quizId);
      setSuccess(`Quiz "${title}" deleted`);
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
            Quiz Review & Management
          </h1>
          <p className="mt-1 text-gray-500">
            Approve, reject, or delete submitted quizzes
          </p>
        </div>

        <div className="flex justify-end mb-6">
          <DownloadReportButton quizzes={quizzes} />
        </div>

        {error && <ErrorAlert message={error} onDismiss={() => setError("")} />}
        {success && <SuccessAlert message={success} onDismiss={() => setSuccess("")} />}

        {loading ? (
          <LoadingSpinner message="Loading quizzes..." />
        ) : (
          <QuizApprovalTable
            quizzes={quizzes}
            onReviewClick={(quiz) => { setSelectedQuiz(quiz); setDialogOpen(true); }}
            onDeleteClick={handleDelete}
            mode="admin"
          />
        )}

        <QuizReviewDialog
          open={dialogOpen}
          quizTitle={selectedQuiz?.title || ""}
          quizId={selectedQuiz?._id}
          onClose={() => setDialogOpen(false)}
          onApprove={handleApprove}
          onReject={handleReject}
        />
      </div>
    </div>
  );
};

export default QuizApprovalPage;
