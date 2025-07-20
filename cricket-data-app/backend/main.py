from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# Import from the app package
from app.config import get_environment_settings

# Load configuration
config = get_environment_settings()

# Initialize FastAPI app with config
app = FastAPI(
    title=config.api_title,
    version=config.api_version,
    debug=config.api_debug
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins_list,
    allow_credentials=config.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class Venue(BaseModel):
    id: int
    name: str

class Game(BaseModel):
    id: int
    home_team: str
    away_team: str
    date: Optional[str] = None
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

def init_database():
    """Initialize the SQLite database using config"""
    conn = sqlite3.connect(config.database_path)
    cursor = conn.cursor()

    # Create tables
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
    """Load CSV data using configured paths"""
    conn = sqlite3.connect(config.database_path)
    
    try:
        # Load venues
        if os.path.exists(config.venues_path):
            venues_df = pd.read_csv(config.venues_path)
            venues_df.to_sql('venues', conn, if_exists='replace', index=False)
            print(f"Loaded {len(venues_df)} venues from {config.venues_path}")
        
        # Load games
        if os.path.exists(config.games_path):
            games_df = pd.read_csv(config.games_path)
            # Reset index and add ID column if not present
            if 'id' not in games_df.columns:
                games_df = games_df.reset_index()
                games_df['id'] = games_df.index + 1
            games_df.to_sql('games', conn, if_exists='replace', index=False)
            print(f"Loaded {len(games_df)} games from {config.games_path}")
        
        # Load simulations
        if os.path.exists(config.simulations_path):
            simulations_df = pd.read_csv(config.simulations_path)
            simulations_df.to_sql('simulations', conn, if_exists='replace', index=False)
            print(f"Loaded {len(simulations_df)} simulations from {config.simulations_path}")
            
    except Exception as e:
        print(f"Error loading CSV data: {e}")
    finally:
        conn.close()

def get_database_connection():
    """Get database connection using configured path"""
    return sqlite3.connect(config.database_path)

# Initialize database and load data on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and load CSV data on application startup"""
    init_database()
    load_csv_data()

@app.get("/")
async def root():
    """Root endpoint returning API status"""
    return {
        "message": f"{config.api_title} is running",
        "environment": config.environment,
        "version": config.api_version
    }

@app.get("/venues", response_model=List[Venue])
async def get_venues():
    """Get all venues"""
    conn = get_database_connection()
    try:
        venues_df = pd.read_sql_query("SELECT venue_id as id, venue_name as name FROM venues", conn)
        return venues_df.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching venues: {str(e)}")
    finally:
        conn.close()

@app.get("/games", response_model=List[Game])
async def get_games():
    """Get all games with venue information"""
    conn = get_database_connection()
    try:
        query = """
        SELECT 
            g.id,
            g.home_team,
            g.away_team,
            g.date,
            g.venue_id,
            v.venue_name
        FROM games g
        LEFT JOIN venues v ON g.venue_id = v.venue_id
        ORDER BY g.id
        """
        games_df = pd.read_sql_query(query, conn)
        return games_df.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching games: {str(e)}")
    finally:
        conn.close()

@app.get("/games/{game_id}", response_model=Game)
async def get_game(game_id: int):
    """Get a specific game by ID"""
    conn = get_database_connection()
    try:
        query = """
        SELECT 
            g.id,
            g.home_team,
            g.away_team,
            g.date,
            g.venue_id,
            v.venue_name
        FROM games g
        LEFT JOIN venues v ON g.venue_id = v.venue_id
        WHERE g.id = ?
        """
        game_df = pd.read_sql_query(query, conn, params=[game_id])
        
        if game_df.empty:
            raise HTTPException(status_code=404, detail="Game not found")
        
        return game_df.iloc[0].to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching game: {str(e)}")
    finally:
        conn.close()

@app.get("/games/{game_id}/analysis", response_model=GameAnalysis)
async def get_game_analysis(game_id: int):
    """Get game analysis with win probabilities"""
    conn = get_database_connection()
    try:
        # Get game details
        game_query = """
        SELECT 
            g.id,
            g.home_team,
            g.away_team,
            g.date,
            g.venue_id,
            v.venue_name
        FROM games g
        LEFT JOIN venues v ON g.venue_id = v.venue_id
        WHERE g.id = ?
        """
        game_df = pd.read_sql_query(game_query, conn, params=[game_id])
        
        if game_df.empty:
            raise HTTPException(status_code=404, detail="Game not found")
        
        game = game_df.iloc[0].to_dict()
        
        # Get simulation data for both teams
        home_team = game['home_team']
        away_team = game['away_team']
        
        # Get home team simulations
        home_query = "SELECT results FROM simulations WHERE team = ?"
        home_simulations = pd.read_sql_query(home_query, conn, params=[home_team])
        
        # Get away team simulations
        away_query = "SELECT results FROM simulations WHERE team = ?"
        away_simulations = pd.read_sql_query(away_query, conn, params=[away_team])
        
        if home_simulations.empty or away_simulations.empty:
            raise HTTPException(
                status_code=404, 
                detail="Simulation data not found for one or both teams"
            )
        
        # Calculate win probability
        home_scores = home_simulations['results'].tolist()
        away_scores = away_simulations['results'].tolist()
        
        # Pair up simulations (truncate to minimum length)
        min_length = min(len(home_scores), len(away_scores))
        home_scores = home_scores[:min_length]
        away_scores = away_scores[:min_length]
        
        # Count home team wins
        home_wins = sum(1 for h, a in zip(home_scores, away_scores) if h > a)
        win_probability = (home_wins / min_length) * 100 if min_length > 0 else 0.0
        
        # Create simulation pairs for response
        simulations = [
            {"home_score": h, "away_score": a} 
            for h, a in zip(home_scores, away_scores)
        ]
        
        return {
            "game": game,
            "simulations": simulations,
            "home_win_probability": round(win_probability, 2),
            "total_simulations": min_length
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing game: {str(e)}")
    finally:
        conn.close()

@app.get("/games/{game_id}/histogram-data")
async def get_game_histogram_data(game_id: int):
    """Get histogram data for game visualization"""
    conn = get_database_connection()
    try:
        # Get game details
        game_query = """
        SELECT 
            g.id,
            g.home_team,
            g.away_team,
            g.date,
            g.venue_id,
            v.venue_name
        FROM games g
        LEFT JOIN venues v ON g.venue_id = v.venue_id
        WHERE g.id = ?
        """
        game_df = pd.read_sql_query(game_query, conn, params=[game_id])
        
        if game_df.empty:
            raise HTTPException(status_code=404, detail="Game not found")
        
        game = game_df.iloc[0].to_dict()
        
        # Get simulation data for both teams
        home_team = game['home_team']
        away_team = game['away_team']
        
        # Get simulations
        home_query = "SELECT results FROM simulations WHERE team = ?"
        home_simulations = pd.read_sql_query(home_query, conn, params=[home_team])
        
        away_query = "SELECT results FROM simulations WHERE team = ?"
        away_simulations = pd.read_sql_query(away_query, conn, params=[away_team])
        
        if home_simulations.empty or away_simulations.empty:
            raise HTTPException(
                status_code=404, 
                detail="Simulation data not found for one or both teams"
            )
        
        home_scores = home_simulations['results'].tolist()
        away_scores = away_simulations['results'].tolist()
        
        # Calculate frequency for each score
        from collections import Counter
        home_frequency = dict(Counter(home_scores))
        away_frequency = dict(Counter(away_scores))
        
        # Convert keys to strings as expected by frontend
        home_frequency = {str(k): v for k, v in home_frequency.items()}
        away_frequency = {str(k): v for k, v in away_frequency.items()}
        
        # Calculate score range
        all_scores = home_scores + away_scores
        min_score = min(all_scores) if all_scores else 0
        max_score = max(all_scores) if all_scores else 0
        
        return {
            "home_team": home_team,
            "away_team": away_team,
            "home_scores": home_scores,
            "away_scores": away_scores,
            "home_frequency": home_frequency,
            "away_frequency": away_frequency,
            "score_range": {
                "min": min_score,
                "max": max_score
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating histogram data: {str(e)}")
    finally:
        conn.close()

@app.get("/teams", response_model=List[str])
async def get_teams():
    """Get all unique team names"""
    conn = get_database_connection()
    try:
        # Get teams from games table
        teams_query = """
        SELECT DISTINCT home_team as team FROM games
        UNION
        SELECT DISTINCT away_team as team FROM games
        ORDER BY team
        """
        teams_df = pd.read_sql_query(teams_query, conn)
        return teams_df['team'].tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching teams: {str(e)}")
    finally:
        conn.close()

@app.get("/simulations/{team_name}")
async def get_team_simulations(team_name: str):
    """Get simulation results for a specific team"""
    conn = get_database_connection()
    try:
        query = "SELECT * FROM simulations WHERE team = ? ORDER BY simulation_run"
        simulations_df = pd.read_sql_query(query, conn, params=[team_name])
        
        if simulations_df.empty:
            raise HTTPException(status_code=404, detail="No simulations found for this team")
        
        return simulations_df.to_dict('records')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching simulations: {str(e)}")
    finally:
        conn.close()

@app.get("/debug/data-status")
async def get_data_status():
    """Debug endpoint to check data loading status"""
    conn = get_database_connection()
    try:
        # Check if tables exist and have data
        tables_info = {}
        
        # Check venues
        try:
            venues_count = pd.read_sql_query("SELECT COUNT(*) as count FROM venues", conn)
            venues_sample = pd.read_sql_query("SELECT * FROM venues LIMIT 3", conn)
            tables_info['venues'] = {
                'count': venues_count.iloc[0]['count'],
                'sample': venues_sample.to_dict('records')
            }
        except Exception as e:
            tables_info['venues'] = {'error': str(e)}
        
        # Check games
        try:
            games_count = pd.read_sql_query("SELECT COUNT(*) as count FROM games", conn)
            games_sample = pd.read_sql_query("SELECT * FROM games LIMIT 3", conn)
            tables_info['games'] = {
                'count': games_count.iloc[0]['count'],
                'sample': games_sample.to_dict('records')
            }
        except Exception as e:
            tables_info['games'] = {'error': str(e)}
        
        # Check simulations
        try:
            simulations_count = pd.read_sql_query("SELECT COUNT(*) as count FROM simulations", conn)
            simulations_sample = pd.read_sql_query("SELECT * FROM simulations LIMIT 3", conn)
            tables_info['simulations'] = {
                'count': simulations_count.iloc[0]['count'],
                'sample': simulations_sample.to_dict('records')
            }
        except Exception as e:
            tables_info['simulations'] = {'error': str(e)}
        
        # Check file existence
        files_status = {
            'venues_csv': os.path.exists(config.venues_path),
            'games_csv': os.path.exists(config.games_path),
            'simulations_csv': os.path.exists(config.simulations_path),
            'data_directory': os.path.exists(config.data_directory),
            'database_file': os.path.exists(config.database_path)
        }
        
        return {
            'config': {
                'environment': config.environment,
                'database_path': config.database_path,
                'data_directory': config.data_directory,
                'venues_path': config.venues_path,
                'games_path': config.games_path,
                'simulations_path': config.simulations_path
            },
            'files_status': files_status,
            'tables_info': tables_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debug error: {str(e)}")
    finally:
        conn.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "environment": config.environment,
            "version": config.api_version
        }
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Service unavailable: {str(e)}"
        )

# Error handlers
@app.exception_handler(sqlite3.Error)
async def database_exception_handler(request, exc):
    """Handle database errors"""
    return HTTPException(
        status_code=500,
        detail="Database error occurred"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=config.api_host, 
        port=config.api_port, 
        reload=config.api_reload
    )