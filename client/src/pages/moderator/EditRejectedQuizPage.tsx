import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { quizAPI } from "../../api/quizzes/QuizAPI";
import type { QuizInput } from "../../api/quizzes/IQuizAPI";
import { QuizForm } from "../../components/moderator/QuizForm";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { ErrorAlert } from "../../components/ui/ErrorAlert";

export const EditRejectedQuizPage: React.FC = () => {
  const { quizId } = useParams<{ quizId: string }>();
  const navigate = useNavigate();

  const [quiz, setQuiz] = useState<QuizInput | null>(null);
  const [rejectionReason, setRejectionReason] = useState<string | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    quizAPI
      .getQuizById(quizId!)
      .then((data) => {
        setRejectionReason(data.rejection_reason);
        setQuiz({
          title: data.title,
          duration: data.duration,
          questions: data.questions.map((q) => ({
            text: q.text,
            options: q.options,
            correct_answers: q.correct_answers ?? [],
            points: q.points,
          })),
        });
      })
      .catch((err: Error) => setError(err.message || "Failed to load quiz"));
  }, [quizId]);

  const handleUpdate = async (updated: QuizInput) => {
    await quizAPI.updateQuiz(quizId!, updated);
    setTimeout(() => navigate("/moderator/quizzes"), 1500);
  };

  if (error) return <ErrorAlert message={error} onDismiss={() => setError("")} />;
  if (!quiz) return <LoadingSpinner message="Loading quiz..." />;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-violet-50 to-indigo-50 px-4 py-12">
      <div className="max-w-4xl mx-auto">
        {rejectionReason && (
          <div className="mb-6 p-4 rounded-2xl bg-red-50 border border-red-200 text-red-700">
            <span className="font-semibold">Rejection reason:</span> {rejectionReason}
          </div>
        )}

        <QuizForm
          heading="Edit Rejected Quiz"
          subheading="Fix the quiz and send it to the admin again"
          submitLabel="Save and Resubmit"
          successMessage="Quiz updated and re-submitted for approval!"
          initialQuiz={quiz}
          onSubmit={handleUpdate}
        />
      </div>
    </div>
  );
};

export default EditRejectedQuizPage;
