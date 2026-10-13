import React, { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { quizAPI } from "../../api/quizzes/QuizAPI";
import type { Quiz } from "../../api/quizzes/IQuizAPI";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { ErrorAlert } from "../../components/ui/ErrorAlert";

const PlayQuizPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [answers, setAnswers] = useState<Record<number, string[]>>({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [error, setError] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [resultMessage, setResultMessage] = useState("");

  // Refs keep the latest values for the timer (a normal state value inside setInterval would be old)
  const answersRef = useRef<Record<number, string[]>>({});
  const startTimeRef = useRef(0);
  const sendingRef = useRef(false);

  // LOAD QUIZ AND START THE TIMER
  useEffect(() => {
    quizAPI
      .getQuizById(id!)
      .then((data) => {
        startTimeRef.current = Date.now();
        setTimeLeft(data.duration);
        setQuiz(data);
      })
      .catch((err: Error) => setError(err.message || "Failed to load quiz"));
  }, [id]);

  // SEND ANSWERS (button or when the time runs out)
  const submitQuiz = useCallback(async () => {
    if (!quiz || sendingRef.current) return;
    sendingRef.current = true;

    const timeSpent = Math.min(quiz.duration, Math.round((Date.now() - startTimeRef.current) / 1000));
    const payload = Object.entries(answersRef.current).map(([index, selected]) => ({
      question_index: Number(index),
      selected,
    }));

    try {
      const response = await quizAPI.submitAnswers(quiz._id, payload, timeSpent);
      setResultMessage(response.message);
      setSubmitted(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit quiz");
      sendingRef.current = false;
    }
  }, [quiz]);

  // TIMER - counts down every second, sends the answers automatically at 0
  useEffect(() => {
    if (!quiz || submitted) return;

    const timer = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
      const left = Math.max(quiz.duration - elapsed, 0);
      setTimeLeft(left);

      if (left === 0) {
        clearInterval(timer);
        submitQuiz();
      }
    }, 1000);

    return () => clearInterval(timer);
  }, [quiz, submitted, submitQuiz]);

  const toggleOption = (questionIndex: number, option: string) => {
    const current = answersRef.current[questionIndex] || [];
    const updated = current.includes(option)
      ? current.filter((x) => x !== option)
      : [...current, option];

    const next = { ...answersRef.current, [questionIndex]: updated };
    answersRef.current = next;
    setAnswers(next);
  };

  if (error) return <ErrorAlert message={error} onDismiss={() => setError("")} />;
  if (!quiz) return <LoadingSpinner message="Loading quiz..." />;

  // AFTER SUBMIT - processing continues in the background, the player can go on
  if (submitted) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-gray-50 via-violet-50 to-indigo-50 p-6">
        <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl p-8 w-full max-w-xl text-center border border-white/60">
          <div className="text-5xl mb-4">📧</div>
          <h2 className="text-2xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-violet-600 to-indigo-600">
            Quiz Submitted!
          </h2>
          <p className="text-gray-700 mb-6">
            Your answers for <strong>{quiz.title}</strong> have been sent for processing.
          </p>
          <div className="bg-violet-50 p-4 rounded-xl text-violet-800 text-sm mb-6">
            {resultMessage} You can continue using the platform in the meantime.
          </div>
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => navigate("/quizzes")}
              className="px-6 py-3 bg-gradient-to-r from-violet-500 to-indigo-500 text-white rounded-xl font-semibold hover:scale-105 transition-all"
            >
              Back to Quizzes
            </button>
            <button
              onClick={() => navigate(`/leaderboard/${quiz._id}`)}
              className="px-6 py-3 rounded-xl font-semibold text-indigo-600 border border-indigo-200 bg-white hover:bg-indigo-50 transition-all"
            >
              Leaderboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-violet-50 to-indigo-50 p-6">
      <div className="max-w-3xl mx-auto bg-white/90 backdrop-blur-sm rounded-3xl shadow-xl p-8 border border-white/60">
        <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-violet-600 to-indigo-600 text-center mb-4">
          {quiz.title}
        </h1>
        <div className={`text-center mb-6 font-semibold ${timeLeft <= 10 ? "text-red-600" : "text-gray-500"}`}>
          Time left: {timeLeft}s / {quiz.duration}s
        </div>

        {quiz.questions.map((q, idx) => (
          <div key={idx} className="mb-6">
            <p className="font-semibold text-gray-800 mb-2">
              {idx + 1}. {q.text} <span className="text-sm text-gray-400 font-normal">({q.points} pts)</span>
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {q.options.map((opt, i) => {
                const selected = answers[idx]?.includes(opt) || false;
                return (
                  <button
                    key={i}
                    type="button"
                    onClick={() => toggleOption(idx, opt)}
                    className={`p-3 rounded-xl border transition-all ${
                      selected
                        ? "bg-violet-500 text-white shadow-md scale-[1.03]"
                        : "bg-gray-50 hover:bg-gray-100 text-gray-700"
                    }`}
                  >
                    {opt}
                  </button>
                );
              })}
            </div>
          </div>
        ))}

        <div className="text-center">
          <button
            onClick={submitQuiz}
            className="px-6 py-3 bg-gradient-to-r from-violet-500 to-indigo-500 text-white rounded-xl font-semibold hover:scale-105 transition-all"
          >
            Submit Quiz
          </button>
        </div>
      </div>
    </div>
  );
};

export default PlayQuizPage;
