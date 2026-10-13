import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { leaderboardAPI, type LeaderboardEntry } from "../../api/leaderboard/LeaderboardAPI";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { ErrorAlert } from "../../components/ui/ErrorAlert";

const LeaderboardPage: React.FC = () => {
  const { quizId } = useParams<{ quizId: string }>();
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    leaderboardAPI
      .getLeaderboard(quizId!)
      .then((data) => setEntries(data))
      .catch((err: Error) => setError(err.message || "Failed to load leaderboard"))
      .finally(() => setLoading(false));
  }, [quizId]);

  if (loading) return <LoadingSpinner message="Loading leaderboard..." />;
  if (error) return <ErrorAlert message={error} onDismiss={() => setError("")} />;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-violet-50 to-indigo-50 px-6 py-12">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-center text-transparent bg-clip-text bg-gradient-to-r from-violet-600 to-indigo-600 mb-8">
          Quiz Leaderboard
        </h1>

        {entries.length === 0 ? (
          <div className="text-center bg-white/50 backdrop-blur-sm rounded-2xl py-12 text-gray-500 border border-white/60">
            No results found for this quiz yet.
          </div>
        ) : (
          <div className="overflow-x-auto bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/50">
            <table className="w-full text-left">
              <thead className="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200 text-xs text-gray-600 uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-4">Rank</th>
                  <th className="px-6 py-4">Player</th>
                  <th className="px-6 py-4">Score</th>
                  <th className="px-6 py-4">Time Spent</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((entry, idx) => (
                  <tr
                    key={idx}
                    className={`border-t transition-all ${idx === 0 ? 'bg-yellow-50/30' : 'hover:bg-gray-50'}`}
                  >
                    <td className="px-6 py-4">
                      <span className={`
                        flex items-center justify-center w-8 h-8 rounded-full font-bold
                        ${idx === 0 ? 'bg-yellow-100 text-yellow-700' :
                          idx === 1 ? 'bg-slate-100 text-slate-700' :
                          idx === 2 ? 'bg-orange-100 text-orange-700' : 'text-gray-500'}
                      `}>
                        {idx + 1}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-800">{entry.full_name}</div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-violet-700 font-bold">{entry.score} / {entry.max_score} pts</span>
                    </td>
                    <td className="px-6 py-4 text-gray-600">
                      {entry.time_spent}s
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default LeaderboardPage;
