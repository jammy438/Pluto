// apiService.test.ts
import apiService from './apiService';
import { Game, Games_analysis, Histogram_data } from './types';

// Mock fetch globally
global.fetch = jest.fn();
const mockedFetch = fetch as jest.MockedFunction<typeof fetch>;

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('getGames', () => {
    test('fetches games successfully', async () => {
      const mockGames: Game[] = [
        { 
          id: 1, 
          home_team: 'Team A', 
          away_team: 'Team B', 
          venue_id: 0, 
          venue_name: 'Ground A' 
        },
        { 
          id: 2, 
          home_team: 'Team C', 
          away_team: 'Team D', 
          venue_id: 1, 
          venue_name: 'Ground B' 
        }
      ];

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockGames
      } as unknown as Response);

      const result = await apiService.getGames();

      expect(mockedFetch).toHaveBeenCalledWith('http://localhost:8000/games');
      expect(mockedFetch).toHaveBeenCalledTimes(1);
      expect(result).toEqual(mockGames);
    });

    test('throws error when response is not ok', async () => {
      mockedFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      } as unknown as Response);

      await expect(apiService.getGames()).rejects.toThrow('Failed to fetch games');
      expect(mockedFetch).toHaveBeenCalledWith('http://localhost:8000/games');
    });

    test('throws error when network request fails', async () => {
      mockedFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(apiService.getGames()).rejects.toThrow('Network error');
    });

    test('returns empty array when no games available', async () => {
      mockedFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => []
      } as unknown as Response);

      const result = await apiService.getGames();

      expect(result).toEqual([]);
    });
  });

  describe('getGameAnalysis', () => {
    test('fetches game analysis successfully', async () => {
      const mockAnalysis: Games_analysis = {
        game: { 
          id: 1, 
          home_team: 'Team A', 
          away_team: 'Team B', 
          venue_id: 0, 
          venue_name: 'Ground A' 
        },
        simulations: [
          { home_score: 150, away_score: 140 },
          { home_score: 160, away_score: 155 }
        ],
        home_win_probability: 75.0,
        total_simulations: 20
      };

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalysis
      } as unknown as Response);

      const result = await apiService.getGameAnalysis(1);

      expect(mockedFetch).toHaveBeenCalledWith('http://localhost:8000/games/1/analysis');
      expect(mockedFetch).toHaveBeenCalledTimes(1);
      expect(result).toEqual(mockAnalysis);
    });

    test('throws error when response is not ok', async () => {
      mockedFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      } as unknown as Response);

      await expect(apiService.getGameAnalysis(1)).rejects.toThrow('Failed to fetch game analysis');
    });

    test('fetches analysis for different game IDs', async () => {
      const mockAnalysis: Games_analysis = {
        game: { 
          id: 5, 
          home_team: 'Team X', 
          away_team: 'Team Y', 
          venue_id: 2, 
          venue_name: 'Stadium Z' 
        },
        simulations: [],
        home_win_probability: 50.0,
        total_simulations: 10
      };

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalysis
      } as unknown as Response);

      const result = await apiService.getGameAnalysis(5);

      expect(mockedFetch).toHaveBeenCalledWith('http://localhost:8000/games/5/analysis');
      expect(result.game.id).toBe(5);
    });

    test('handles analysis with zero win probability', async () => {
      const mockAnalysis: Games_analysis = {
        game: { 
          id: 1, 
          home_team: 'Weak Team', 
          away_team: 'Strong Team', 
          venue_id: 0, 
          venue_name: 'Ground A' 
        },
        simulations: [
          { home_score: 100, away_score: 150 },
          { home_score: 110, away_score: 160 }
        ],
        home_win_probability: 0.0,
        total_simulations: 20
      };

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalysis
      } as unknown as Response);

      const result = await apiService.getGameAnalysis(1);

      expect(result.home_win_probability).toBe(0.0);
    });

    test('handles analysis with 100% win probability', async () => {
      const mockAnalysis: Games_analysis = {
        game: { 
          id: 1, 
          home_team: 'Strong Team', 
          away_team: 'Weak Team', 
          venue_id: 0, 
          venue_name: 'Ground A' 
        },
        simulations: [
          { home_score: 200, away_score: 100 },
          { home_score: 210, away_score: 110 }
        ],
        home_win_probability: 100.0,
        total_simulations: 20
      };

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalysis
      } as unknown as Response);

      const result = await apiService.getGameAnalysis(1);

      expect(result.home_win_probability).toBe(100.0);
    });
  });

  describe('getHistogramData', () => {
    test('fetches histogram data successfully', async () => {
      const mockHistogramData: Histogram_data = {
        home_team: 'Team A',
        away_team: 'Team B',
        home_scores: [150, 160, 155],
        away_scores: [140, 155, 145],
        home_frequency: { '150': 5, '160': 3, '155': 2 },
        away_frequency: { '140': 4, '155': 4, '145': 2 },
        score_range: { min: 140, max: 160 }
      };

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockHistogramData
      } as unknown as Response);

      const result = await apiService.getHistogramData(1);

      expect(mockedFetch).toHaveBeenCalledWith('http://localhost:8000/games/1/histogram-data');
      expect(mockedFetch).toHaveBeenCalledTimes(1);
      expect(result).toEqual(mockHistogramData);
    });

    test('throws error when response is not ok', async () => {
      mockedFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      } as unknown as Response);

      await expect(apiService.getHistogramData(1)).rejects.toThrow('Failed to fetch histogram data');
    });

    test('fetches histogram data for different game IDs', async () => {
      const mockHistogramData: Histogram_data = {
        home_team: 'Different Home',
        away_team: 'Different Away',
        home_scores: [120, 130, 125],
        away_scores: [110, 125, 115],
        home_frequency: { '120': 3, '130': 2, '125': 1 },
        away_frequency: { '110': 2, '125': 3, '115': 1 },
        score_range: { min: 110, max: 130 }
      };

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockHistogramData
      } as unknown as Response);

      const result = await apiService.getHistogramData(3);

      expect(mockedFetch).toHaveBeenCalledWith('http://localhost:8000/games/3/histogram-data');
      expect(result.home_team).toBe('Different Home');
    });

    test('handles empty histogram data', async () => {
      const emptyHistogramData: Histogram_data = {
        home_team: 'Team A',
        away_team: 'Team B',
        home_scores: [],
        away_scores: [],
        home_frequency: {},
        away_frequency: {},
        score_range: { min: 0, max: 0 }
      };

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => emptyHistogramData
      } as unknown as Response);

      const result = await apiService.getHistogramData(1);

      expect(result.home_scores).toEqual([]);
      expect(result.away_scores).toEqual([]);
    });

    test('handles large histogram datasets', async () => {
      const largeScores = Array.from({ length: 1000 }, (_, i) => 100 + i);
      const largeFrequency: Record<string, number> = {};
      largeScores.forEach(score => {
        largeFrequency[score.toString()] = Math.floor(Math.random() * 10) + 1;
      });

      const largeHistogramData: Histogram_data = {
        home_team: 'Team Large',
        away_team: 'Team Big',
        home_scores: largeScores,
        away_scores: largeScores.map(s => s - 10),
        home_frequency: largeFrequency,
        away_frequency: largeFrequency,
        score_range: { min: 90, max: 1099 }
      };

      mockedFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => largeHistogramData
      } as unknown as Response);

      const result = await apiService.getHistogramData(1);

      expect(result.home_scores.length).toBe(1000);
      expect(result.score_range.max).toBe(1099);
    });
  });

  describe('API Base URL', () => {
    test('all methods use correct base URL', () => {
      const expectedBaseUrl = 'http://localhost:8000';
      
      mockedFetch.mockResolvedValue({
        ok: true,
        json: async () => ({})
      } as unknown as Response);

      apiService.getGames();
      expect(mockedFetch).toHaveBeenLastCalledWith(`${expectedBaseUrl}/games`);

      apiService.getGameAnalysis(1);
      expect(mockedFetch).toHaveBeenLastCalledWith(`${expectedBaseUrl}/games/1/analysis`);

      apiService.getHistogramData(1);
      expect(mockedFetch).toHaveBeenLastCalledWith(`${expectedBaseUrl}/games/1/histogram-data`);
    });
  });

  describe('Error Handling', () => {
    test('handles JSON parsing errors', async () => {
      mockedFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON');
        }
      } as unknown as Response);

      await expect(apiService.getGames()).rejects.toThrow('Invalid JSON');
    });

    test('handles network timeout errors', async () => {
      mockedFetch.mockImplementationOnce(() => 
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Request timeout')), 100)
        )
      );

      await expect(apiService.getGames()).rejects.toThrow('Request timeout');
    });

    test('handles server 500 errors', async () => {
      mockedFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      } as unknown as Response);

      await expect(apiService.getGameAnalysis(1)).rejects.toThrow('Failed to fetch game analysis');
    });

    test('handles malformed response data', async () => {
      mockedFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => null
      } as unknown as Response);

      const result = await apiService.getGames();
      expect(result).toBeNull();
    });
  });

  describe('Integration Scenarios', () => {
    test('sequential API calls work correctly', async () => {
      const mockGames: Game[] = [{ id: 1, home_team: 'A', away_team: 'B', venue_id: 0, venue_name: 'Ground' }];
      const mockAnalysis: Games_analysis = {
        game: mockGames[0],
        simulations: [],
        home_win_probability: 60,
        total_simulations: 10
      };

      mockedFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockGames
        } as unknown as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockAnalysis
        } as unknown as Response);

      const games = await apiService.getGames();
      const analysis = await apiService.getGameAnalysis(games[0].id);

      expect(games).toEqual(mockGames);
      expect(analysis).toEqual(mockAnalysis);
      expect(mockedFetch).toHaveBeenCalledTimes(2);
    });
  });
});