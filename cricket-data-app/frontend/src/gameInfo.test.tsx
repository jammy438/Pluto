// gameInfo.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import GameInfo from './gameInfo';
import { Games_analysis } from './types';

const mockAnalysis: Games_analysis = {
  game: {
    id: 1,
    home_team: 'Manchester United',
    away_team: 'Arsenal',
    venue_id: 0,
    venue_name: 'Old Trafford'
  },
  simulations: [
    { home_score: 180, away_score: 160 },
    { home_score: 175, away_score: 170 },
    { home_score: 165, away_score: 155 }
  ],
  home_win_probability: 65.5,
  total_simulations: 100
};

describe('GameInfo Component', () => {
  test('renders game analysis title', () => {
    render(<GameInfo analysis={mockAnalysis} />);
    
    expect(screen.getByText('Game Analysis')).toBeInTheDocument();
  });

  test('displays home team name and label', () => {
    render(<GameInfo analysis={mockAnalysis} />);
    
    expect(screen.getByText('Manchester United')).toBeInTheDocument();
    expect(screen.getByText('Home')).toBeInTheDocument();
  });

  test('displays away team name and label', () => {
    render(<GameInfo analysis={mockAnalysis} />);
    
    expect(screen.getByText('Arsenal')).toBeInTheDocument();
    expect(screen.getByText('Away')).toBeInTheDocument();
  });

  test('displays venue information', () => {
    render(<GameInfo analysis={mockAnalysis} />);
    
    expect(screen.getByText(/Venue:/)).toBeInTheDocument();
    expect(screen.getByText('Old Trafford')).toBeInTheDocument();
  });

  test('displays home win percentage correctly', () => {
    render(<GameInfo analysis={mockAnalysis} />);
    
    expect(screen.getByText('65.5%')).toBeInTheDocument();
    expect(screen.getByText('Home Win Percentage')).toBeInTheDocument();
  });

  test('displays total simulations count', () => {
    render(<GameInfo analysis={mockAnalysis} />);
    
    expect(screen.getByText('100')).toBeInTheDocument();
    expect(screen.getByText('Total Simulations')).toBeInTheDocument();
  });

  test('displays VS separator between teams', () => {
    render(<GameInfo analysis={mockAnalysis} />);
    
    expect(screen.getByText('VS')).toBeInTheDocument();
  });

  test('renders with different team names', () => {
    const differentAnalysis: Games_analysis = {
      ...mockAnalysis,
      game: {
        ...mockAnalysis.game,
        home_team: 'Liverpool',
        away_team: 'Chelsea'
      }
    };

    render(<GameInfo analysis={differentAnalysis} />);
    
    expect(screen.getByText('Liverpool')).toBeInTheDocument();
    expect(screen.getByText('Chelsea')).toBeInTheDocument();
  });

  test('renders with different venue name', () => {
    const differentAnalysis: Games_analysis = {
      ...mockAnalysis,
      game: {
        ...mockAnalysis.game,
        venue_name: 'Anfield Stadium'
      }
    };

    render(<GameInfo analysis={differentAnalysis} />);
    
    expect(screen.getByText('Anfield Stadium')).toBeInTheDocument();
  });

  test('renders with 100% win probability', () => {
    const perfectAnalysis: Games_analysis = {
      ...mockAnalysis,
      home_win_probability: 100.0
    };

    render(<GameInfo analysis={perfectAnalysis} />);
    
    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  test('renders with 0% win probability', () => {
    const zeroAnalysis: Games_analysis = {
      ...mockAnalysis,
      home_win_probability: 0.0
    };

    render(<GameInfo analysis={zeroAnalysis} />);
    
    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  test('renders with decimal win probability', () => {
    const decimalAnalysis: Games_analysis = {
      ...mockAnalysis,
      home_win_probability: 33.33
    };

    render(<GameInfo analysis={decimalAnalysis} />);
    
    expect(screen.getByText('33.33%')).toBeInTheDocument();
  });

  test('renders with single simulation', () => {
    const singleSimAnalysis: Games_analysis = {
      ...mockAnalysis,
      total_simulations: 1
    };

    render(<GameInfo analysis={singleSimAnalysis} />);
    
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  test('renders with large number of simulations', () => {
    const largeSimAnalysis: Games_analysis = {
      ...mockAnalysis,
      total_simulations: 10000
    };

    render(<GameInfo analysis={largeSimAnalysis} />);
    
    expect(screen.getByText('10000')).toBeInTheDocument();
  });

  test('has correct CSS classes for styling', () => {
    render(<GameInfo analysis={mockAnalysis} />);
    
    const gameInfoDiv = screen.getByText('Game Analysis').closest('.game-info');
    expect(gameInfoDiv).toBeInTheDocument();
    
    const homeTeamDiv = screen.getByText('Manchester United').closest('.team.home');
    expect(homeTeamDiv).toBeInTheDocument();
    
    const awayTeamDiv = screen.getByText('Arsenal').closest('.team.away');
    expect(awayTeamDiv).toBeInTheDocument();
  });

  test('displays stats section with correct structure', () => {
    render(<GameInfo analysis={mockAnalysis} />);
    
    const statsDiv = document.querySelector('.stats');
    expect(statsDiv).toBeInTheDocument();
    
    const statDivs = document.querySelectorAll('.stat');
    expect(statDivs).toHaveLength(2);
  });
});