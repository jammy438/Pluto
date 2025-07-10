from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

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
