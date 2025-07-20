# app/api/endpoints/games.py
"""Game API endpoints with real database queries."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Annotated
import logging
import traceback
import sqlite3

# Import database connection
from app.database.connection import db_manager

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/games", tags=["games"])


def get_database_connection():
    """Get database connection."""
    return db_manager.get_connection()


@router.get("/")
async def get_games():
    """Get all games from database."""
    logger.info("GET /games/ - Getting all games from database")
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Query games with venue information
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
        
        logger.info(f"Executing query: {query}")
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert rows to list of dictionaries
        games = []
        for row in rows:
            game = {
                "id": row[0],
                "home_team": row[1],
                "away_team": row[2],
                "date": row[3],
                "venue_id": row[4],
                "venue_name": row[5] if row[5] else "Unknown Venue"
            }
            games.append(game)
        
        conn.close()
        logger.info(f"Successfully retrieved {len(games)} games from database")
        return games
        
    except sqlite3.Error as e:
        logger.error(f"Database error in get_games: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Database error retrieving games: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in get_games: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving games: {str(e)}"
        )


@router.get("/{game_id}")
async def get_game(game_id: int):
    """Get game by ID from database."""
    logger.info(f"GET /games/{game_id} - Getting game by ID from database")
    
    try:
        if game_id <= 0:
            logger.warning(f"Invalid game ID: {game_id}")
            raise HTTPException(status_code=400, detail="Game ID must be positive")
        
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Query specific game with venue information
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
        
        logger.info(f"Executing query: {query} with game_id: {game_id}")
        cursor.execute(query, (game_id,))
        row = cursor.fetchone()
        
        if row:
            game = {
                "id": row[0],
                "home_team": row[1],
                "away_team": row[2],
                "date": row[3],
                "venue_id": row[4],
                "venue_name": row[5] if row[5] else "Unknown Venue"
            }
            conn.close()
            logger.info(f"Found game: {game}")
            return game
        else:
            conn.close()
            logger.warning(f"Game not found for ID: {game_id}")
            raise HTTPException(status_code=404, detail="Game not found")
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except sqlite3.Error as e:
        logger.error(f"Database error in get_game: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Database error retrieving game {game_id}: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in get_game: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving game {game_id}: {str(e)}"
        )


@router.get("/{game_id}/analysis")
async def get_game_analysis(game_id: int):
    """Get game analysis with real simulations and win probability."""
    logger.info(f"GET /games/{game_id}/analysis - Getting game analysis from database")
    
    try:
        if game_id <= 0:
            logger.warning(f"Invalid game ID: {game_id}")
            raise HTTPException(status_code=400, detail="Game ID must be positive")
        
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # First, get the game information
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
        
        logger.info(f"Getting game info for ID: {game_id}")
        cursor.execute(game_query, (game_id,))
        game_row = cursor.fetchone()
        
        if not game_row:
            conn.close()
            logger.warning(f"Game not found for analysis: {game_id}")
            raise HTTPException(status_code=404, detail="Game not found")
        
        game_info = {
            "id": game_row[0],
            "home_team": game_row[1],
            "away_team": game_row[2],
            "date": game_row[3],
            "venue_id": game_row[4],
            "venue_name": game_row[5] if game_row[5] else "Unknown Venue"
        }
        
        # Get simulations for both teams
        simulation_query = """
        SELECT 
            team,
            simulation_run,
            results
        FROM simulations 
        WHERE team IN (?, ?)
        ORDER BY simulation_run, team
        """
        
        logger.info(f"Getting simulations for teams: {game_info['home_team']}, {game_info['away_team']}")
        cursor.execute(simulation_query, (game_info['home_team'], game_info['away_team']))
        simulation_rows = cursor.fetchall()
        
        # Process simulations - group by simulation_run
        simulations_by_run = {}
        for row in simulation_rows:
            team, sim_run, result = row
            if sim_run not in simulations_by_run:
                simulations_by_run[sim_run] = {}
            simulations_by_run[sim_run][team] = result
        
        # Create simulation pairs (only where both teams have data for the same run)
        simulations = []
        home_wins = 0
        total_simulations = 0
        
        for sim_run, team_results in simulations_by_run.items():
            home_team = game_info['home_team']
            away_team = game_info['away_team']
            
            if home_team in team_results and away_team in team_results:
                home_score = team_results[home_team]
                away_score = team_results[away_team]
                
                simulations.append({
                    "home_score": home_score,
                    "away_score": away_score
                })
                
                if home_score > away_score:
                    home_wins += 1
                total_simulations += 1
        
        # Calculate win probability
        if total_simulations > 0:
            home_win_probability = round((home_wins / total_simulations) * 100, 2)
        else:
            home_win_probability = 0.0
        
        conn.close()
        
        analysis = {
            "game": game_info,
            "simulations": simulations,
            "home_win_probability": home_win_probability,
            "total_simulations": total_simulations
        }
        
        logger.info(f"Generated analysis for game {game_id}: {total_simulations} simulations, {home_win_probability}% home win rate")
        return analysis
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except sqlite3.Error as e:
        logger.error(f"Database error in get_game_analysis: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Database error retrieving analysis for game {game_id}: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in get_game_analysis: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving analysis for game {game_id}: {str(e)}"
        )


@router.get("/{game_id}/histogram-data")
async def get_histogram_data(game_id: int):
    """Get histogram data for game visualization from database."""
    logger.info(f"GET /games/{game_id}/histogram-data - Getting histogram data from database")
    
    try:
        if game_id <= 0:
            logger.warning(f"Invalid game ID: {game_id}")
            raise HTTPException(status_code=400, detail="Game ID must be positive")
        
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # First, get the game information
        game_query = """
        SELECT home_team, away_team
        FROM games 
        WHERE id = ?
        """
        
        logger.info(f"Getting game info for histogram, ID: {game_id}")
        cursor.execute(game_query, (game_id,))
        game_row = cursor.fetchone()
        
        if not game_row:
            conn.close()
            logger.warning(f"Game not found for histogram: {game_id}")
            raise HTTPException(status_code=404, detail="Game not found")
        
        home_team, away_team = game_row
        
        # Get all simulation results for both teams
        simulation_query = """
        SELECT team, results
        FROM simulations 
        WHERE team IN (?, ?)
        """
        
        logger.info(f"Getting simulation data for teams: {home_team}, {away_team}")
        cursor.execute(simulation_query, (home_team, away_team))
        simulation_rows = cursor.fetchall()
        
        # Separate scores by team
        home_scores = []
        away_scores = []
        
        for row in simulation_rows:
            team, score = row
            if team == home_team:
                home_scores.append(score)
            elif team == away_team:
                away_scores.append(score)
        
        # Calculate score range
        all_scores = home_scores + away_scores
        if all_scores:
            score_range = {"min": min(all_scores), "max": max(all_scores)}
        else:
            score_range = {"min": 0, "max": 0}
        
        # Create frequency objects (count occurrences of each score)
        from collections import Counter
        
        home_frequency = dict(Counter(home_scores))
        away_frequency = dict(Counter(away_scores))
        
        # Convert integer keys to string keys (as expected by frontend)
        home_frequency_str = {str(score): count for score, count in home_frequency.items()}
        away_frequency_str = {str(score): count for score, count in away_frequency.items()}
        
        conn.close()
        
        histogram_data = {
            "home_team": home_team,
            "away_team": away_team,
            "home_scores": home_scores,
            "away_scores": away_scores,
            "home_frequency": home_frequency_str,
            "away_frequency": away_frequency_str,
            "score_range": score_range
        }
        
        logger.info(f"Generated histogram data for game {game_id}: {len(home_scores)} home scores, {len(away_scores)} away scores")
        logger.info(f"Home frequency sample: {dict(list(home_frequency_str.items())[:5])}")
        logger.info(f"Away frequency sample: {dict(list(away_frequency_str.items())[:5])}")
        
        return histogram_data
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except sqlite3.Error as e:
        logger.error(f"Database error in get_histogram_data: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Database error retrieving histogram data for game {game_id}: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in get_histogram_data: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving histogram data for game {game_id}: {str(e)}"
        )