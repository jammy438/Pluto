# app/api/endpoints/simulations.py
"""Simulation API endpoints with real database queries."""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging
import traceback
import sqlite3

# Import database connection
from app.database.connection import db_manager

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/simulations", tags=["simulations"])


def get_database_connection():
    """Get database connection."""
    return db_manager.get_connection()


@router.get("/teams")
async def get_teams():
    """Get all unique team names from database."""
    logger.info("GET /simulations/teams - Getting all team names from database")
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Query unique team names
        query = "SELECT DISTINCT team FROM simulations ORDER BY team"
        
        logger.info(f"Executing query: {query}")
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Extract team names from rows
        teams = [row[0] for row in rows]
        
        conn.close()
        logger.info(f"Successfully retrieved {len(teams)} teams from database")
        return teams
        
    except sqlite3.Error as e:
        logger.error(f"Database error in get_teams: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error retrieving teams: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in get_teams: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving teams: {str(e)}"
        )


@router.get("/{team_name}")
async def get_team_simulations(team_name: str):
    """Get simulations for a specific team from database."""
    logger.info(f"GET /simulations/{team_name} - Getting simulations for team from database")
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Query simulations for specific team
        query = """
        SELECT team_id, team, simulation_run, results 
        FROM simulations 
        WHERE team = ? 
        ORDER BY simulation_run
        """
        
        logger.info(f"Executing query: {query} with team_name: {team_name}")
        cursor.execute(query, (team_name,))
        rows = cursor.fetchall()
        
        if not rows:
            conn.close()
            logger.warning(f"No simulations found for team: {team_name}")
            raise HTTPException(
                status_code=404, 
                detail=f"No simulations found for team: {team_name}"
            )
        
        # Convert rows to list of dictionaries
        simulations = []
        for row in rows:
            simulation = {
                "team_id": row[0],
                "team": row[1],
                "simulation_run": row[2],
                "results": row[3]
            }
            simulations.append(simulation)
        
        conn.close()
        logger.info(f"Successfully retrieved {len(simulations)} simulations for team {team_name}")
        return simulations
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except sqlite3.Error as e:
        logger.error(f"Database error in get_team_simulations: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Database error retrieving simulations for team {team_name}: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in get_team_simulations: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving simulations for team {team_name}: {str(e)}"
        )


@router.get("/{team_name}/statistics")
async def get_team_statistics(team_name: str):
    """Get statistical summary for a team from database."""
    logger.info(f"GET /simulations/{team_name}/statistics - Getting team statistics from database")
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Query statistics for specific team
        query = """
        SELECT
            COUNT(*) as total_simulations,
            AVG(results) as average_score,
            MIN(results) as min_score,
            MAX(results) as max_score
        FROM simulations
        WHERE team = ?
        """
        
        logger.info(f"Executing query: {query} with team_name: {team_name}")
        cursor.execute(query, (team_name,))
        row = cursor.fetchone()
        
        if not row or row[0] == 0:
            conn.close()
            logger.warning(f"No simulations found for team statistics: {team_name}")
            raise HTTPException(
                status_code=404, 
                detail=f"No simulations found for team: {team_name}"
            )
        
        # Calculate standard deviation manually
        std_query = """
        SELECT results 
        FROM simulations 
        WHERE team = ?
        """
        cursor.execute(std_query, (team_name,))
        results = [r[0] for r in cursor.fetchall()]
        
        # Calculate standard deviation
        avg_score = row[1]
        variance = sum((score - avg_score) ** 2 for score in results) / len(results)
        std_dev = variance ** 0.5
        
        conn.close()
        
        statistics = {
            "total_simulations": row[0],
            "average_score": round(row[1], 2),
            "min_score": row[2],
            "max_score": row[3],
            "standard_deviation": round(std_dev, 2)
        }
        
        logger.info(f"Generated statistics for team {team_name}: {statistics}")
        return statistics
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except sqlite3.Error as e:
        logger.error(f"Database error in get_team_statistics: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Database error retrieving statistics for team {team_name}: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in get_team_statistics: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving statistics for team {team_name}: {str(e)}"
        )