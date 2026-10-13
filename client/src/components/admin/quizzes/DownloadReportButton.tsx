import React from "react";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import type { QuizSummary } from "../../../api/quizzes/IQuizAPI";

interface Props {
  quizzes: QuizSummary[];
}

const formatDate = (dateString?: string) => {
  try {
    if (!dateString) return "—";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  } catch {
    return "—";
  }
};

const DownloadReportButton: React.FC<Props> = ({ quizzes }) => {
  const handleDownload = () => {
    const doc = new jsPDF();
    const date = new Date().toISOString().split("T")[0];

    doc.setFontSize(16);
    doc.text("Quiz Platform – Summary Report", 14, 18);
    doc.setFontSize(11);
    doc.text(`Generated on: ${date}`, 14, 25);

    const tableData = quizzes.map((q) => [
      q.title,
      q.author_name,
      q.status,
      q.question_count,
      q.duration + "s",
      formatDate(q.created_at),
    ]);

    autoTable(doc, {
      startY: 32,
      head: [["Title", "Author", "Status", "Questions", "Duration", "Created"]],
      body: tableData,
      theme: "grid",
      styles: { fontSize: 10 },
      headStyles: { fillColor: [120, 81, 169] },
    });

    doc.save(`quiz_report_${date}.pdf`);
  };

  return (
    <button
      onClick={handleDownload}
      className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-violet-500 to-indigo-500 text-white font-medium shadow hover:scale-105 transition-transform cursor-pointer"
    >
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        strokeWidth={2}
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M12 4v16m8-8H4"
        />
      </svg>
      Download PDF Report
    </button>
  );
};

export default DownloadReportButton;
