import React from "react";
import { QuizForm } from "../../components/moderator/QuizForm";
import { quizAPI } from "../../api/quizzes/QuizAPI";
import type { QuizInput } from "../../api/quizzes/IQuizAPI";

const CreateQuizPage: React.FC = () => {
  const handleCreate = async (quiz: QuizInput) => {
    await quizAPI.createQuiz(quiz);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-violet-50 to-indigo-50 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-4xl">
        <QuizForm
          heading="Create New Quiz"
          subheading="Fill in quiz details and questions"
          submitLabel="Submit Quiz"
          successMessage="Quiz created and sent to the admin for approval"
          resetAfterSubmit
          onSubmit={handleCreate}
        />
      </div>
    </div>
  );
};

export default CreateQuizPage;
