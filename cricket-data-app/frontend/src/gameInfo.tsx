import React from 'react';
import { Games_analysis } from './types';

const GameInfo: React.FC<{ analysis: Games_analysis }> = ({ analysis }) => {
    const { game, home_win_probability, total_simulations } = analysis;
    
    return (
      <div className="game-info">
        <h2>Game Analysis</h2>
        <div className="game-details">
          <div className="teams">
            <div className="team home">
              <h3>{game.home_team}</h3>
              <span className="team-label">Home</span>
            </div>
            <div className="vs">VS</div>
            <div className="team away">
              <h3>{game.away_team}</h3>
              <span className="team-label">Away</span>
            </div>
          </div>
          
          <div className="venue">
            <strong>Venue:</strong> {game.venue_name}
          </div>
          
          <div className="stats">
            <div className="stat">
              <div className="stat-value">{home_win_probability}%</div>
              <div className="stat-label">Home Win Percentage</div>
            </div>
            <div className="stat">
              <div className="stat-value">{total_simulations}</div>
              <div className="stat-label">Total Simulations</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  export default GameInfo;