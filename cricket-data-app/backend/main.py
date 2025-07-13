from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd
import os
from typing import List, Dict, Any
from pydantic import BaseModel

app = FastAPI(title="Cricket Data API", version="1.0.0")

#Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Cricket Data API is running"}

#database setup
DATABASE_PATH = "cricket_data.db"

def init_database():
    """Initialize the SQLite database and load CSV data"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    #create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS venues (
            venue_id INTEGER PRIMARY KEY,
            venue_name TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            date TEXT,
            venue_id INTEGER,
            FOREIGN KEY (venue_id) REFERENCES venues (venue_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER,
            team TEXT,
            simulation_run INTEGER,
            results INTEGER
        )
    ''')

    conn.commit()
    conn.close()

def load_csv_data():
    """Load data from CSV files into the database"""
    conn = sqlite3.connect(DATABASE_PATH)

    try:

        # Load venues
        if os.path.exists('data/venues.csv'):
            venues_df = pd.read_csv('data/venues.csv')
            venues_df.to_sql('venues', conn, if_exists='replace', index=False)
            print("venues.csv loaded successfully")
        
        # Load games
        if os.path.exists('data/games.csv'):
            games_df = pd.read_csv('data/games.csv')
            games_df = games_df.reset_index()
            games_df['id'] = games_df.index + 1
            games_df.to_sql('games', conn, if_exists='replace', index=False)
            print("games.csv loaded successfully")
        
        # Load simulations
        if os.path.exists('data/simulations.csv'):
            simulations_df = pd.read_csv('data/simulations.csv')
            simulations_df.to_sql('simulations', conn, if_exists='replace', index=False)
            print("simulations.csv loaded successfully")

    except Exception as e:
        print(f"Error loading CSV data: {e}")
    finally:
        conn.close()

# Response models
class Venue(BaseModel):
    id: int
    name: str

class Game(BaseModel):
    id: int
    home_team: str
    away_team: str
    venue_id: int
    venue_name: str

class Simulation(BaseModel):
    home_score: int
    away_score: int

class GameAnalysis(BaseModel):
    game: Game
    simulations: List[Simulation]
    home_win_probability: float
    total_simulations: int

@app.on_event("startup")
async def startup_event():
        """Initialize the database and load data on startup"""
        init_database()
        load_csv_data()

@app.get("/venues", response_model=List[Venue])
async def get_venues():
    """Get all venues"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT venue_id, venue_name FROM venues")
    venues = [{"id":row[0], "name":row[1]} for row in cursor.fetchall()]

    conn.close()
    return venues

@app.get("/games", response_model=List[Game])
async def get_games():
    """Get all games with venue info"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT g.id, g.home_team, g.away_team, g.venue_id, v.venue_name
        FROM games g
        LEFT JOIN venues v ON g.venue_id = v.venue_id
    """)
    
    games = [
        {
            "id": row[0],
            "home_team": row[1],
            "away_team": row[2],
            "venue_id": row[3],
            "venue_name": row[4] or "Unknown Venue"
        }
        for row in cursor.fetchall()
    ]

    conn.close()
    return games

@app.get("/games/{game_id}/analysis", response_model=GameAnalysis)
async def get_game_analysis(game_id: int):
    """Get game analysis including simulations and win probabilities"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get game details
    cursor.execute("""
        SELECT g.id, g.home_team, g.away_team, g.venue_id, v.venue_name
        FROM games g
        LEFT JOIN venues v ON g.venue_id = v.venue_id
        WHERE g.id = ?
    """, (game_id,))
    
    game_row = cursor.fetchone()
    if not game_row:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = Game(
        id=game_row[0],
        home_team=game_row[1],
        away_team=game_row[2],
        venue_id=game_row[3],
        venue_name=game_row[4] or "Unknown Venue"
    )
    
    # Get simulations for the teams
    cursor.execute("""
        SELECT results FROM simulations 
        WHERE team = ? 
        LIMIT 20
    """, (game.home_team,))
    home_results = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT results FROM simulations 
        WHERE team = ? 
        LIMIT 20
    """, (game.away_team,))
    away_results = [row[0] for row in cursor.fetchall()]
    
    simulations = []
    home_wins = 0
    total_sims = min(len(home_results), len(away_results), 20)
    
    for i in range(total_sims):
        home_score = home_results[i] if i < len(home_results) else 150
        away_score = away_results[i] if i < len(away_results) else 150
        
        simulations.append({
            "home_score": home_score,
            "away_score": away_score
        })
        
        if home_score > away_score:
            home_wins += 1
    
    conn.close()

    if total_sims == 0:
        raise HTTPException(status_code=404, detail="No simulation data found for this game")
    
    home_win_percentage = (home_wins / total_sims) * 100
    
    return {
        "game": game,
        "simulations": simulations,
        "home_win_probability": round(home_win_percentage, 2),
        "total_simulations": total_sims
    }

@app.get("/games/{game_id}/histogram-data")
async def get_histogram_data(game_id: int):
    """Get histogram data for visualization"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get game info
    cursor.execute("SELECT home_team, away_team FROM games WHERE id = ?", (game_id,))
    game_row = cursor.fetchone()
    if not game_row:
        raise HTTPException(status_code=404, detail="Game not found")
    
    home_team, away_team = game_row
    
    # Get simulation scores
    cursor.execute("SELECT results FROM simulations WHERE team = ?", (home_team,))
    home_scores = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT results FROM simulations WHERE team = ?", (away_team,))
    away_scores = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    if not home_scores or not away_scores:
        raise HTTPException(status_code=404, detail="No simulation data found")
    
    # Create histogram data
    # Create frequency distributions
    from collections import Counter
    home_freq = Counter(home_scores)
    away_freq = Counter(away_scores)
    
    return {
        "home_team": home_team,
        "away_team": away_team,
        "home_scores": home_scores,
        "away_scores": away_scores,
        "home_frequency": dict(home_freq),
        "away_frequency": dict(away_freq),
        "score_range": {"min": min(min(home_scores), min(away_scores)), "max": max(max(home_scores), max(away_scores))}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)