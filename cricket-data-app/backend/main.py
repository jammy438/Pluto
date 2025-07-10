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
    allow_origins=["http://localhost:3000"],
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
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            venue_id INTEGER,
            FOREIGN KEY (venue_id) REFERENCES venues (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            home_score INTEGER,
            away_score INTEGER,
            FOREIGN KEY (game_id) REFERENCES games (id)
        )
    ''')

    conn.commit()
    conn.close()

def load_csv_data():
    """Load data from CSV files into the database"""
    conn = sqlite3.connect(DATABASE_PATH)


    try:

        # Load venues
        if os.path.exists('venues.csv'):
            venues_df = pd.read_csv('venues.csv')
            venues_df.to_sql('venues', conn, if_exists='replace', index=False)
            print("venues.csv loaded successfully")
        
        # Load games
        if os.path.exists('games.csv'):
            games_df = pd.read_csv('games.csv')
            games_df.to_sql('games', conn, if_exists='replace', index=False)
            print("games.csv loaded successfully")
        
        # Load simulations
        if os.path.exists('simulations.csv'):
            simulations_df = pd.read_csv('simulations.csv')
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
    id: int
    game_id: int
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
    
    cursor.execute("SELECT * FROM venues")
    venues = [{"id":row[0], "name":row[1]} for row in cursor.fetchall()]

    conn.close()
    return venues

@app.get("/games", response_model=List[Game])
async def get_games():
    """Get all games with venue info"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT g.id, g.home_team, g.away_team, g.venue_id, v.name
        FROM games g
        LEFT JOIN venues v ON g.venue_id = v.id
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

