const BASE_URL = import.meta.env.VITE_API_URL;

export interface LeaderboardEntry {
  user_id: number;
  full_name: string;
  score: number;
  max_score: number;
  time_spent: number; // seconds
}

export class LeaderboardAPI {
  async getLeaderboard(quizId: string): Promise<LeaderboardEntry[]> {
    const token = localStorage.getItem("access_token");
    const response = await fetch(`${BASE_URL}/quizzes/${quizId}/leaderboard`, {
      headers: {
        Authorization: token ? `Bearer ${token}` : "",
      },
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(
        `Failed to load leaderboard (${response.status}): ${text}`,
      );
    }

    return await response.json();
  }
}

export const leaderboardAPI = new LeaderboardAPI();
