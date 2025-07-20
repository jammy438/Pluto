# app/api/endpoints/venues.py
"""Venue API endpoints with real database queries."""

from fastapi import APIRouter, HTTPException
from typing import List
import logging
import traceback
import sqlite3

# Import database connection
from app.database.connection import db_manager

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/venues", tags=["venues"])


def get_database_connection():
    """Get database connection."""
    return db_manager.get_connection()


@router.get("/")
async def get_venues():
    """Get all venues from database."""
    logger.info("GET /venues/ - Getting all venues from database")
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Query all venues
        query = "SELECT venue_id, venue_name FROM venues ORDER BY venue_id"
        
        logger.info(f"Executing query: {query}")
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert rows to list of dictionaries
        venues = []
        for row in rows:
            venue = {
                "id": row[0],
                "name": row[1]
            }
            venues.append(venue)
        
        conn.close()
        logger.info(f"Successfully retrieved {len(venues)} venues from database")
        return venues
        
    except sqlite3.Error as e:
        logger.error(f"Database error in get_venues: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Database error retrieving venues: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in get_venues: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving venues: {str(e)}"
        )


@router.get("/{venue_id}")
async def get_venue(venue_id: int):
    """Get venue by ID from database."""
    logger.info(f"GET /venues/{venue_id} - Getting venue by ID from database")
    
    try:
        if venue_id <= 0:
            logger.warning(f"Invalid venue ID: {venue_id}")
            raise HTTPException(status_code=400, detail="Venue ID must be positive")
        
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Query specific venue
        query = "SELECT venue_id, venue_name FROM venues WHERE venue_id = ?"
        
        logger.info(f"Executing query: {query} with venue_id: {venue_id}")
        cursor.execute(query, (venue_id,))
        row = cursor.fetchone()
        
        if row:
            venue = {
                "id": row[0],
                "name": row[1]
            }
            conn.close()
            logger.info(f"Found venue: {venue}")
            return venue
        else:
            conn.close()
            logger.warning(f"Venue not found for ID: {venue_id}")
            raise HTTPException(status_code=404, detail="Venue not found")
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except sqlite3.Error as e:
        logger.error(f"Database error in get_venue: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Database error retrieving venue {venue_id}: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in get_venue: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving venue {venue_id}: {str(e)}"
        )