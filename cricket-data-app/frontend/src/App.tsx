import React, { useState, useEffect } from 'react';
import Histogram from './histogram';
import GameInfo from './gameInfo';
import apiService from './apiService';
import { Game, Games_analysis, Histogram_data } from './types';
import './App.css'

const App: React.FC = () => {
  const [games, setGames] = useState<Game[]>([]);
  const [selectedGameId, setSelectedGameId] = useState<number | null>(null);
  const [gameAnalysis, setGameAnalysis] = useState<Games_analysis | null>(null);
  const [histogramData, setHistogramData] = useState<Histogram_data | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadGames();
  }, []);

  const loadGames = async () => {
    try {
      setLoading(true);
      const gamesData = await apiService.getGames();
      setGames(gamesData);
      setError(null);
    } catch (err) {
      setError('Failed to load games. Make sure the backend is running.');
      console.error('Error loading games:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGameSelect = async (gameId: number) => {
    try {
      setLoading(true);
      setSelectedGameId(gameId);
      
      // Load analysis and histogram data
      const [analysisData, histogramData] = await Promise.all([
        apiService.getGameAnalysis(gameId),
        apiService.getHistogramData(gameId)
      ]);
      
      setGameAnalysis(analysisData);
      setHistogramData(histogramData);
      setError(null);
    } catch (err) {
      setError('Failed to load game data');
      console.error('Error loading game data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDropdownChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const gameId = parseInt(event.target.value);
    if (gameId) {
      handleGameSelect(gameId);
    } else {
      setSelectedGameId(null);
      setGameAnalysis(null);
      setHistogramData(null);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Cricket Simulation Analysis</h1>
      </header>

      <main className="App-main">
        {error && (
          <div className="error-message">
            <p>{error}</p>
            <button onClick={loadGames}>Retry</button>
          </div>
        )}

        <div className="game-selector">
          <h2>Select a Game</h2>
          {loading && <p>Loading...</p>}
          
          <div className="dropdown-container">
            <select 
              value={selectedGameId || ''}
              onChange={handleDropdownChange}
              className="game-dropdown"
              disabled={loading || games.length === 0}
            >
              <option value="">Choose a game...</option>
              {games.map((game) => (
                <option key={game.id} value={game.id}>
                  {game.home_team} vs {game.away_team} - {game.venue_name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {gameAnalysis && (
          <div className="analysis-section">
            <GameInfo analysis={gameAnalysis} />
            
            {histogramData && (
              <div className="histogram-section">
                <Histogram data={histogramData} />
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default App;