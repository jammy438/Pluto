"""
Updated main.py using centralized constants.

This version replaces all magic numbers and hardcoded strings with constants
from the app.constants module for better maintainability.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from collections import Counter

# Import from the app package
from app.config import get_environment_settings
from app.constants import (
    HTTPStatus, ErrorMessages, Database, API, BusinessLogic,
    Frontend, Logging, format_error_message
)

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
    allow_methods=API.CORS.ALLOWED_METHODS,
    allow_headers=API.CORS.ALLOWED_HEADERS,
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
    """Initialize the SQLite database using config and constants"""
    conn = sqlite3.connect(config.database_path)
    cursor = conn.cursor()

    # Create tables using constants
    cursor.execute(Database.Queries.CREATE_VENUES_TABLE)
    cursor.execute(Database.Queries.CREATE_GAMES_TABLE)
    cursor.execute(Database.Queries.CREATE_SIMULATIONS_TABLE)

    conn.commit()
    conn.close()
    print(Logging.Messages.DATABASE_INITIALIZED)

def load_csv_data():
    """Load CSV data using configured paths and constants"""
    conn = sqlite3.connect(config.database_path)
    
    try:
        # Load venues
        if os.path.exists(config.venues_path):
            venues_df = pd.read_csv(config.venues_path)
            venues_df.to_sql(Database.Tables.VENUES, conn, if_exists='replace', index=False)
            print(Logging.Messages.CSV_LOADED.format(
                count=len(venues_df), 
                type=Database.Tables.VENUES, 
                path=config.venues_path
            ))
        
        # Load games
        if os.path.exists(config.games_path):
            games_df = pd.read_csv(config.games_path)
            # Reset index and add ID column if not present
            if Database.Columns.GAME_ID not in games_df.columns:
                games_df = games_df.reset_index()
                games_df[Database.Columns.GAME_ID] = games_df.index + 1
            games_df.to_sql(Database.Tables.GAMES, conn, if_exists='replace', index=False)
            print(Logging.Messages.CSV_LOADED.format(
                count=len(games_df), 
                type=Database.Tables.GAMES, 
                path=config.games_path
            ))
        
        # Load simulations
        if os.path.exists(config.simulations_path):
            simulations_df = pd.read_csv(config.simulations_path)
            simulations_df.to_sql(Database.Tables.SIMULATIONS, conn, if_exists='replace', index=False)
            print(Logging.Messages.CSV_LOADED.format(
                count=len(simulations_df), 
                type=Database.Tables.SIMULATIONS, 
                path=config.simulations_path
            ))
            
    except Exception as e:
        print(format_error_message(ErrorMessages.ERROR_LOADING_CSV, error=str(e)))
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
    print(Logging.Messages.STARTUP_COMPLETE)

@app.get("/")
async def root():
    """Root endpoint returning API status"""
    return {
        "message": API.ResponseMessages.API_RUNNING.format(title=config.api_title),
        "environment": config.environment,
        "version": config.api_version
    }

@app.get("/venues", response_model=List[Venue])
async def get_venues():
    """Get all venues"""
    conn = get_database_connection()
    try:
        venues_df = pd.read_sql_query(Database.Queries.SELECT_VENUES, conn)
        return venues_df.to_dict('records')
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, 
            detail=format_error_message(ErrorMessages.ERROR_FETCHING_VENUES, error=str(e))
        )
    finally:
        conn.close()

@app.get("/games", response_model=List[Game])
async def get_games():
    """Get all games with venue information"""
    conn = get_database_connection()
    try:
        games_df = pd.read_sql_query(Database.Queries.SELECT_GAMES_WITH_VENUES, conn)
        return games_df.to_dict('records')
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, 
            detail=format_error_message(ErrorMessages.ERROR_FETCHING_GAMES, error=str(e))
        )
    finally:
        conn.close()

@app.get("/games/{game_id}", response_model=Game)
async def get_game(game_id: int):
    """Get a specific game by ID"""
    conn = get_database_connection()
    try:
        game_df = pd.read_sql_query(Database.Queries.SELECT_GAME_BY_ID, conn, params=[game_id])
        
        if game_df.empty:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, 
                detail=ErrorMessages.GAME_NOT_FOUND
            )
        
        return game_df.iloc[0].to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, 
            detail=format_error_message(ErrorMessages.ERROR_FETCHING_GAME, error=str(e))
        )
    finally:
        conn.close()

@app.get("/games/{game_id}/analysis", response_model=GameAnalysis)
async def get_game_analysis(game_id: int):
    """Get game analysis with win probabilities"""
    conn = get_database_connection()
    try:
        # Get game details
        game_df = pd.read_sql_query(Database.Queries.SELECT_GAME_BY_ID, conn, params=[game_id])
        
        if game_df.empty:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, 
                detail=ErrorMessages.GAME_NOT_FOUND
            )
        
        game = game_df.iloc[0].to_dict()
        
        # Get simulation data for both teams
        home_team = game[Database.Columns.HOME_TEAM]
        away_team = game[Database.Columns.AWAY_TEAM]
        
        # Get home team simulations
        home_simulations = pd.read_sql_query(
            Database.Queries.SELECT_TEAM_SIMULATIONS, 
            conn, 
            params=[home_team]
        )
        
        # Get away team simulations
        away_simulations = pd.read_sql_query(
            Database.Queries.SELECT_TEAM_SIMULATIONS, 
            conn, 
            params=[away_team]
        )
        
        if home_simulations.empty or away_simulations.empty:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, 
                detail=ErrorMessages.SIMULATION_DATA_NOT_FOUND
            )
        
        # Calculate win probability
        home_scores = home_simulations[Database.Columns.RESULTS].tolist()
        away_scores = away_simulations[Database.Columns.RESULTS].tolist()
        
        # Pair up simulations (truncate to minimum length)
        min_length = min(len(home_scores), len(away_scores))
        home_scores = home_scores[:min_length]
        away_scores = away_scores[:min_length]
        
        # Count home team wins
        home_wins = sum(1 for h, a in zip(home_scores, away_scores) if h > a)
        win_probability = (
            (home_wins / min_length) * BusinessLogic.WinProbability.PERCENTAGE_MULTIPLIER 
            if min_length > 0 else 0.0
        )
        
        # Create simulation pairs for response
        simulations = [
            {"home_score": h, "away_score": a} 
            for h, a in zip(home_scores, away_scores)
        ]
        
        return {
            "game": game,
            "simulations": simulations,
            "home_win_probability": round(win_probability, BusinessLogic.WinProbability.DECIMAL_PLACES),
            "total_simulations": min_length
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, 
            detail=format_error_message(ErrorMessages.ERROR_ANALYZING_GAME, error=str(e))
        )
    finally:
        conn.close()

@app.get("/games/{game_id}/histogram-data")
async def get_game_histogram_data(game_id: int):
    """Get histogram data for game visualization"""
    conn = get_database_connection()
    try:
        # Get game details
        game_df = pd.read_sql_query(Database.Queries.SELECT_GAME_BY_ID, conn, params=[game_id])
        
        if game_df.empty:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, 
                detail=ErrorMessages.GAME_NOT_FOUND
            )
        
        game = game_df.iloc[0].to_dict()
        home_team = game[Database.Columns.HOME_TEAM]
        away_team = game[Database.Columns.AWAY_TEAM]
        
        # Get simulation data
        home_simulations = pd.read_sql_query(
            Database.Queries.SELECT_TEAM_SIMULATIONS, 
            conn, 
            params=[home_team]
        )
        
        away_simulations = pd.read_sql_query(
            Database.Queries.SELECT_TEAM_SIMULATIONS, 
            conn, 
            params=[away_team]
        )
        
        if home_simulations.empty or away_simulations.empty:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, 
                detail=ErrorMessages.SIMULATION_DATA_NOT_FOUND
            )
        
        home_scores = home_simulations[Database.Columns.RESULTS].tolist()
        away_scores = away_simulations[Database.Columns.RESULTS].tolist()
        
        # Calculate frequency for each score
        home_frequency = dict(Counter(home_scores))
        away_frequency = dict(Counter(away_scores))
        
        # Convert keys to strings as expected by frontend
        home_frequency = {
            Frontend.DataFormats.SCORE_STRING_FORMAT.format(score=k): v 
            for k, v in home_frequency.items()
        }
        away_frequency = {
            Frontend.DataFormats.SCORE_STRING_FORMAT.format(score=k): v 
            for k, v in away_frequency.items()
        }
        
        # Calculate score range
        all_scores = home_scores + away_scores
        min_score = min(all_scores) if all_scores else BusinessLogic.DataLimits.MIN_SCORE
        max_score = max(all_scores) if all_scores else BusinessLogic.DataLimits.MIN_SCORE
        
        return {
            Database.Columns.HOME_TEAM: home_team,
            Database.Columns.AWAY_TEAM: away_team,
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
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, 
            detail=format_error_message(ErrorMessages.ERROR_GENERATING_HISTOGRAM, error=str(e))
        )
    finally:
        conn.close()

@app.get("/teams", response_model=List[str])
async def get_teams():
    """Get all unique team names"""
    conn = get_database_connection()
    try:
        teams_df = pd.read_sql_query(Database.Queries.SELECT_ALL_TEAMS, conn)
        return teams_df[Database.Columns.TEAM_ALIAS].tolist()
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, 
            detail=format_error_message(ErrorMessages.ERROR_FETCHING_TEAMS, error=str(e))
        )
    finally:
        conn.close()

@app.get("/simulations/{team_name}")
async def get_team_simulations(team_name: str):
    """Get simulation results for a specific team"""
    conn = get_database_connection()
    try:
        simulations_df = pd.read_sql_query(
            Database.Queries.SELECT_TEAM_SIMULATION_DETAILS, 
            conn, 
            params=[team_name]
        )
        
        if simulations_df.empty:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, 
                detail=ErrorMessages.NO_SIMULATIONS_FOR_TEAM
            )
        
        return simulations_df.to_dict('records')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, 
            detail=format_error_message(ErrorMessages.ERROR_FETCHING_SIMULATIONS, error=str(e))
        )
    finally:
        conn.close()

@app.get("/debug/data-status")
async def get_data_status():
    """Debug endpoint to check data loading status"""
    conn = get_database_connection()
    try:
        # Check if tables exist and have data
        tables_info = {}
        
        # Check each table using constants
        for table_name in [Database.Tables.VENUES, Database.Tables.GAMES, Database.Tables.SIMULATIONS]:
            try:
                count_query = Database.Queries.COUNT_RECORDS.format(table=table_name)
                sample_query = Database.Queries.SAMPLE_RECORDS.format(
                    table=table_name, 
                    limit=BusinessLogic.DataLimits.DEFAULT_SAMPLE_LIMIT
                )
                
                count_result = pd.read_sql_query(count_query, conn)
                sample_result = pd.read_sql_query(sample_query, conn)
                
                tables_info[table_name] = {
                    Database.Columns.COUNT: count_result.iloc[0][Database.Columns.COUNT],
                    'sample': sample_result.to_dict('records')
                }
            except Exception as e:
                tables_info[table_name] = {'error': str(e)}
        
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
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, 
            detail=format_error_message(ErrorMessages.DEBUG_ERROR, error=str(e))
        )
    finally:
        conn.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute(Database.Queries.HEALTH_CHECK)
        conn.close()
        
        return {
            "status": API.ResponseMessages.HEALTH_STATUS_HEALTHY,
            "database": API.ResponseMessages.DATABASE_CONNECTED,
            "environment": config.environment,
            "version": config.api_version
        }
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE, 
            detail=format_error_message(ErrorMessages.SERVICE_UNAVAILABLE, error=str(e))
        )

# Error handlers
@app.exception_handler(sqlite3.Error)
async def database_exception_handler(request, exc):
    """Handle database errors"""
    return HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail=ErrorMessages.DATABASE_ERROR
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.api_host,
        port=config.api_port,
        reload=config.api_reload
    )