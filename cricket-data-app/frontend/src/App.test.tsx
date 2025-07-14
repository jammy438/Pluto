// App.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';
import apiService from './apiService';

// Mock the apiService
jest.mock('./apiService');
const mockedApiService = apiService as jest.Mocked<typeof apiService>;

// Mock data
const mockGames = [
  {
    id: 1,
    home_team: 'Team A',
    away_team: 'Team B',
    venue_id: 0,
    venue_name: 'Test Ground'
  },
  {
    id: 2,
    home_team: 'Team C',
    away_team: 'Team D',
    venue_id: 1,
    venue_name: 'Another Ground'
  }
];

const mockGameAnalysis = {
  game: mockGames[0],
  simulations: [
    { home_score: 150, away_score: 140 },
    { home_score: 160, away_score: 155 }
  ],
  home_win_probability: 75.5,
  total_simulations: 20
};

const mockHistogramData = {
  home_team: 'Team A',
  away_team: 'Team B',
  home_scores: [150, 160, 155],
  away_scores: [140, 155, 145],
  home_frequency: { '150': 5, '160': 3, '155': 2 },
  away_frequency: { '140': 4, '155': 4, '145': 2 },
  score_range: { min: 140, max: 160 }
};

describe('App Component', () => {
    beforeEach(() => {
      jest.clearAllMocks();
    });
  
    test('renders Cricket Simulation Analysis title', () => {
      mockedApiService.getGames.mockResolvedValue([]);
      render(<App />);
      expect(screen.getByText('Cricket Simulation Analysis')).toBeInTheDocument();
    });
  
    test('loads and displays games on component mount', async () => {
      mockedApiService.getGames.mockResolvedValue(mockGames);
      
      render(<App />);
      
      await waitFor(() => {
        expect(mockedApiService.getGames).toHaveBeenCalledTimes(1);
      });
  
      expect(screen.getByText('Team A vs Team B - Test Ground')).toBeInTheDocument();
    });
  });
  
  test('handles API error when loading games', async () => {
    mockedApiService.getGames.mockRejectedValue(new Error('API Error'));
    
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText(/Failed to load games/)).toBeInTheDocument();
    });
  });
