import { Game, Games_analysis, Histogram_data } from './types';

// Docker-aware API URL configuration
const getApiBaseUrl = (): string => {
  // Check if we're in production (nginx proxy setup)
  if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return '/api'; // Production: use nginx proxy
  }
  
  // Development: check if backend port is exposed
  return process.env.REACT_APP_API_URL || "http://localhost:8000";
};

const API_BASE_URL = getApiBaseUrl();

console.log(`🔗 API Base URL: ${API_BASE_URL}`);

const apiService = {
  async getGames(): Promise<Game[]> {
    try {
      console.log(`🎯 Fetching games from: ${API_BASE_URL}/games`);
      const response = await fetch(`${API_BASE_URL}/games`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      console.log(`✅ Retrieved ${data.length} games`);
      return data;
    } catch (error) {
      console.error("❌ Failed to fetch games:", error);
      throw new Error("Failed to fetch games");
    }
  },

  async getGameAnalysis(gameId: number): Promise<Games_analysis> {
    try {
      console.log(`🎯 Fetching analysis for game ${gameId}`);
      const response = await fetch(`${API_BASE_URL}/games/${gameId}/analysis`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      console.log(`✅ Retrieved analysis for game ${gameId}`);
      return data;
    } catch (error) {
      console.error("❌ Failed to fetch game analysis:", error);
      throw new Error("Failed to fetch game analysis");
    }
  },

  async getHistogramData(gameId: number): Promise<Histogram_data> {
    try {
      console.log(`🎯 Fetching histogram data for game ${gameId}`);
      const response = await fetch(`${API_BASE_URL}/games/${gameId}/histogram-data`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      console.log(`✅ Retrieved histogram data for game ${gameId}`);
      return data;
    } catch (error) {
      console.error("❌ Failed to fetch histogram data:", error);
      throw new Error("Failed to fetch histogram data");
    }
  },

  // Health check method for debugging
  async healthCheck(): Promise<boolean> {
    try {
      console.log(`🏥 Health check: ${API_BASE_URL}/health`);
      const response = await fetch(`${API_BASE_URL}/health`);
      const isHealthy = response.ok;
      console.log(`${isHealthy ? '✅' : '❌'} Backend health: ${isHealthy ? 'OK' : 'FAILED'}`);
      return isHealthy;
    } catch (error) {
      console.error("❌ Health check failed:", error);
      return false;
    }
  }
};

export default apiService;