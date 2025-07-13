export interface Venue {
    id: number;
    name: string;
  }
  
  export interface Game {
    id: number;
    home_team: string;
    away_team: string;
    venue_id: number;
    venue_name: string;
  }
  export interface Simulation {
    home_score: number;
    away_score: number;
  }
  
  export interface Games_analysis {
    game: Game;
    simulations: Simulation[];
    home_win_probability: number;
    total_simulations: number;
  }
  
  export interface Histogram_data {
    home_team: string;
    away_team: string;
    home_scores: number[];
    away_scores: number[];
    home_frequency: Record<string, number>;
    away_frequency: Record<string, number>;
    score_range: { min: number; max: number };
  }