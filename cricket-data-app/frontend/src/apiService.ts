import { Game, Games_analysis, Histogram_data } from './types';

const API_BASE_URL = "http://localhost:8000";

const apiService = {
  async getGames(): Promise<Game[]> {
    const response = await fetch(`${API_BASE_URL}/games`);
    if (!response.ok) throw new Error("Failed to fetch games");
    return response.json();
  },

  async getGameAnalysis(gameId: number): Promise<Games_analysis> {
    const response = await fetch(`${API_BASE_URL}/games/${gameId}/analysis`);
    if (!response.ok) throw new Error("Failed to fetch game analysis");
    return response.json();
  },

  async getHistogramData(gameId: number): Promise<Histogram_data> {
    const response = await fetch(
      `${API_BASE_URL}/games/${gameId}/histogram-data`
    );
    if (!response.ok) throw new Error("Failed to fetch histogram data");
    return response.json();
  },
};