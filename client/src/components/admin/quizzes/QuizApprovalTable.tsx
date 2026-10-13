import React, { useState } from "react";
import { QuizStatusBadge } from "./QuizStatusBadge";
import { useNavigate } from "react-router-dom";
import type { QuizSummary } from "../../../api/quizzes/IQuizAPI";

interface Props {
  quizzes: QuizSummary[];
  onReviewClick?: (quiz: QuizSummary) => void;
  onDeleteClick: (quizId: string, title: string) => void;
  showReviewButton?: boolean;
  mode?: "admin" | "moderator";
}

export const QuizApprovalTable: React.FC<Props> = ({
  quizzes,
  onReviewClick,
  onDeleteClick,
  showReviewButton = true,
  mode = "moderator",
}) => {
  const [selectedReason, setSelectedReason] = useState<string | null>(null);
  const navigate = useNavigate();

  if (quizzes.length === 0)
    return (
      <div className="text-center py-12 text-gray-500">
        No quizzes found.
      </div>
    );

  return (
    <div className="overflow-x-auto bg-white/80 backdrop-blur-sm rounded-2xl shadow-md border border-white/60 relative">
      <table className="w-full text-left align-middle">
        <thead className="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200 text-sm text-gray-600 uppercase">
          <tr>
            <th className="px-6 py-3 w-1/4">Title</th>
            <th className="px-6 py-3 w-1/6 text-center">Author</th>
            <th className="px-6 py-3 w-1/12 text-center">Questions</th>
            <th className="px-6 py-3 w-1/12 text-center">Duration</th>
            <th className="px-6 py-3 w-1/6 text-center">Status</th>
            <th className="px-6 py-3 w-1/3 text-center">Actions</th>
          </tr>
        </thead>
        <tbody>
          {quizzes.map((quiz) => (
            <tr
              key={quiz._id}
              className={`border-t transition-all ${
                quiz.status === "REJECTED"
                  ? "bg-red-50/40"
                  : "hover:bg-gray-50"
              }`}
            >
              <td className="px-6 py-4 font-semibold text-lg text-gray-800">
                {quiz.title}
              </td>

              <td className="px-6 py-4 text-gray-600 text-center">{quiz.author_name}</td>
              <td className="px-6 py-4 text-gray-600 text-center">{quiz.question_count}</td>
              <td className="px-6 py-4 text-gray-600 text-center">{quiz.duration}s</td>
              <td className="px-6 py-4 text-center">
                <QuizStatusBadge status={quiz.status} />
              </td>

              <td className="px-6 py-4">
                <div className="flex justify-center items-center gap-3 flex-wrap">
                  {mode === "moderator" && quiz.status === "REJECTED" && (
                    <>
                      <button
                        onClick={() => setSelectedReason(quiz.rejection_reason || "No reason provided")}
                        className="flex-1 min-w-[130px] px-4 py-2 text-sm rounded-lg bg-amber-500 text-white font-medium hover:bg-amber-600 transition"
                      >
                        Review Rejection
                      </button>
                      <button
                        onClick={() => navigate(`/moderator/edit-quiz/${quiz._id}`)}
                        className="flex-1 min-w-[130px] px-4 py-2 text-sm rounded-lg bg-emerald-500 text-white font-medium hover:bg-emerald-600 transition"
                      >
                        Edit Quiz
                      </button>
                    </>
                  )}

                  {/* Only quizzes waiting for approval can be reviewed */}
                  {showReviewButton && quiz.status === "PENDING" && (
                    <button
                      onClick={() => onReviewClick?.(quiz)}
                      className="flex-1 min-w-[130px] px-4 py-2 text-sm rounded-lg bg-gradient-to-r from-violet-500 to-indigo-500 text-white font-medium hover:scale-105 transition"
                    >
                      Review
                    </button>
                  )}

                  <button
                    onClick={() => onDeleteClick(quiz._id, quiz.title)}
                    className="flex-1 min-w-[130px] px-4 py-2 text-sm rounded-lg bg-red-500 text-white font-medium hover:bg-red-600 transition"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {selectedReason && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/40 z-50">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 text-center">
            <h2 className="text-xl font-bold text-gray-800 mb-2">
              Rejection Reason
            </h2>
            <p className="text-gray-700 mb-6 whitespace-pre-line">
              {selectedReason}
            </p>
            <button
              onClick={() => setSelectedReason(null)}
              className="w-full px-4 py-2 rounded-lg bg-gradient-to-r from-violet-500 to-indigo-500 text-white font-semibold hover:scale-105 transition"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
