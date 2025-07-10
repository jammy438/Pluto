from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd
import os

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
            name TEXT NOT NULL,
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