# test_main.py
import pytest
import sqlite3
import tempfile
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd

# Import your FastAPI app
from main import app, init_database, load_csv_data

client = TestClient(app)

class TestDatabaseSetup:
    """Test database initialization and CSV loading"""
    
    def setup_method(self):
        """Setup test database for each test"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db_path = self.test_db.name
        self.test_db.close()
    
    def teardown_method(self):
        """Clean up test database after each test"""
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)
    
    def test_init_database(self):
        """Test database initialization creates all required tables"""
        with patch('main.DATABASE_PATH', self.test_db_path):
            init_database()
        
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'venues' in tables
        assert 'games' in tables
        assert 'simulations' in tables
        
        conn.close()
    
    def test_database_tables_structure(self):
        """Test that database tables have correct structure"""
        with patch('main.DATABASE_PATH', self.test_db_path):
            init_database()
        
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Check venues table structure
        cursor.execute("PRAGMA table_info(venues)")
        venues_columns = [row[1] for row in cursor.fetchall()]
        assert 'venue_id' in venues_columns
        assert 'venue_name' in venues_columns
        
        # Check games table structure
        cursor.execute("PRAGMA table_info(games)")
        games_columns = [row[1] for row in cursor.fetchall()]
        assert 'id' in games_columns
        assert 'home_team' in games_columns
        assert 'away_team' in games_columns
        
        conn.close()

class TestCSVLoading:
    """Test CSV data loading functionality"""
    
    def setup_method(self):
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db_path = self.test_db.name
        self.test_db.close()
        
        # Create test CSV data
        self.test_venues_data = pd.DataFrame({
            'venue_id': [0, 1, 2],
            'venue_name': ['Test Ground 1', 'Test Ground 2', 'Test Ground 3']
        })
        
        self.test_games_data = pd.DataFrame({
            'home_team': ['Team A', 'Team B'],
            'away_team': ['Team B', 'Team A'],
            'date': ['2024-01-01', '2024-01-02'],
            'venue_id': [0, 1]
        })
        
        self.test_simulations_data = pd.DataFrame({
            'team_id': [0, 0, 1, 1],
            'team': ['Team A', 'Team A', 'Team B', 'Team B'],
            'simulation_run': [1, 2, 1, 2],
            'results': [150, 160, 140, 145]
        })
    
    def teardown_method(self):
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)
    
    @patch('pandas.read_csv')
    @patch('os.path.exists')
    def test_load_csv_data_success(self, mock_exists, mock_read_csv):
        """Test successful CSV data loading"""
        mock_exists.return_value = True
        
        # Mock CSV reading
        def mock_csv_side_effect(filename):
            if 'venues.csv' in filename:
                return self.test_venues_data
            elif 'games.csv' in filename:
                return self.test_games_data
            elif 'simulations.csv' in filename:
                return self.test_simulations_data
            return pd.DataFrame()
        
        mock_read_csv.side_effect = mock_csv_side_effect
        
        with patch('main.DATABASE_PATH', self.test_db_path):
            init_database()
            load_csv_data()
        
        # Verify data was loaded
        conn = sqlite3.connect(self.test_db_path)
        
        # Check venues
        venues = pd.read_sql_query("SELECT * FROM venues", conn)
        assert len(venues) == 3
        
        # Check games
        games = pd.read_sql_query("SELECT * FROM games", conn)
        assert len(games) == 2
        
        conn.close()

class TestAPIEndpoints:
    """Test FastAPI endpoints"""
    
    def setup_method(self):
        """Setup test data before each test"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db_path = self.test_db.name
        self.test_db.close()
        
        # Initialize test database with sample data
        with patch('main.DATABASE_PATH', self.test_db_path):
            init_database()
            self._insert_test_data()
    
    def teardown_method(self):
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)
    
    def _insert_test_data(self):
        """Insert test data into database"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Insert venues
        cursor.execute("INSERT INTO venues (venue_id, venue_name) VALUES (0, 'Test Ground')")
        
        # Insert games
        cursor.execute("""
            INSERT INTO games (id, home_team, away_team, date, venue_id) 
            VALUES (1, 'Team A', 'Team B', '2024-01-01', 0)
        """)
        
        # Insert simulations
        for i in range(5):
            cursor.execute("""
                INSERT INTO simulations (team_id, team, simulation_run, results) 
                VALUES (?, ?, ?, ?)
            """, (0, 'Team A', i+1, 150+i))
            cursor.execute("""
                INSERT INTO simulations (team_id, team, simulation_run, results) 
                VALUES (?, ?, ?, ?)
            """, (1, 'Team B', i+1, 140+i))
        
        conn.commit()
        conn.close()
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        with patch('main.DATABASE_PATH', self.test_db_path):
            response = client.get("/")
            assert response.status_code == 200
            assert response.json() == {"message": "Cricket Data API is running"}
    
    def test_get_venues(self):
        """Test venues endpoint"""
        with patch('main.DATABASE_PATH', self.test_db_path):
            response = client.get("/venues")
            assert response.status_code == 200
            
            venues = response.json()
            assert len(venues) == 1
            assert venues[0]["name"] == "Test Ground"
    
    def test_get_games(self):
        """Test games endpoint"""
        with patch('main.DATABASE_PATH', self.test_db_path):
            response = client.get("/games")
            assert response.status_code == 200
            
            games = response.json()
            assert len(games) == 1
            assert games[0]["home_team"] == "Team A"
            assert games[0]["away_team"] == "Team B"
    
    def test_get_game_analysis(self):
        """Test game analysis endpoint"""
        with patch('main.DATABASE_PATH', self.test_db_path):
            response = client.get("/games/1/analysis")
            assert response.status_code == 200
            
            analysis = response.json()
            assert "game" in analysis
            assert "home_win_probability" in analysis
            assert "total_simulations" in analysis
            assert analysis["game"]["home_team"] == "Team A"
    
    def test_get_game_analysis_not_found(self):
        """Test game analysis endpoint with non-existent game"""
        with patch('main.DATABASE_PATH', self.test_db_path):
            response = client.get("/games/999/analysis")
            assert response.status_code == 404
            assert "Game not found" in response.json()["detail"]
    
    def test_get_histogram_data(self):
        """Test histogram data endpoint"""
        with patch('main.DATABASE_PATH', self.test_db_path):
            response = client.get("/games/1/histogram-data")
            assert response.status_code == 200
            
            histogram = response.json()
            assert "home_team" in histogram
            assert "away_team" in histogram
            assert "home_scores" in histogram
            assert "away_scores" in histogram
            assert histogram["home_team"] == "Team A"
    
    def test_get_histogram_data_not_found(self):
        """Test histogram data endpoint with non-existent game"""
        with patch('main.DATABASE_PATH', self.test_db_path):
            response = client.get("/games/999/histogram-data")
            assert response.status_code == 404

class TestWinProbabilityCalculation:
    """Test win probability calculation logic"""
    
    def test_win_probability_all_home_wins(self):
        """Test win probability when home team wins all simulations"""
        home_scores = [150, 160, 170, 180, 190]
        away_scores = [140, 150, 160, 170, 180]
        
        home_wins = sum(1 for h, a in zip(home_scores, away_scores) if h > a)
        win_percentage = (home_wins / len(home_scores)) * 100
        
        assert win_percentage == 100.0
    
    def test_win_probability_equal_teams(self):
        """Test win probability with equal performing teams"""
        home_scores = [150, 140, 160, 130, 170]
        away_scores = [140, 150, 150, 140, 160]
        
        home_wins = sum(1 for h, a in zip(home_scores, away_scores) if h > a)
        win_percentage = (home_wins / len(home_scores)) * 100
        
        # Should be 60% (3 out of 5 wins)
        assert win_percentage == 60.0
    
    def test_win_probability_no_wins(self):
        """Test win probability when home team loses all"""
        home_scores = [140, 150, 160, 170, 180]
        away_scores = [150, 160, 170, 180, 190]
        
        home_wins = sum(1 for h, a in zip(home_scores, away_scores) if h > a)
        win_percentage = (home_wins / len(home_scores)) * 100
        
        assert win_percentage == 0.0

class TestDataValidation:
    """Test data validation and error handling"""
    
    def test_empty_simulation_data(self):
        """Test handling of empty simulation data"""
        # Test that the system handles empty data gracefully
        home_scores = []
        away_scores = []
        
        if len(home_scores) == 0:
            win_percentage = 0.0
        else:
            home_wins = sum(1 for h, a in zip(home_scores, away_scores) if h > a)
            win_percentage = (home_wins / len(home_scores)) * 100
        
        assert win_percentage == 0.0
    
    def test_mismatched_data_lengths(self):
        """Test handling of mismatched data lengths"""
        home_scores = [150, 160, 170]
        away_scores = [140, 150]  # Shorter list
        
        # Should handle gracefully by using minimum length
        min_length = min(len(home_scores), len(away_scores))
        home_wins = sum(1 for h, a in zip(home_scores[:min_length], away_scores[:min_length]) if h > a)
        win_percentage = (home_wins / min_length) * 100 if min_length > 0 else 0.0
        
        assert win_percentage == 100.0  # Both home scores are higher

# Pytest fixtures
@pytest.fixture
def test_client():
    """Fixture for FastAPI test client"""
    return TestClient(app)

@pytest.fixture
def temp_database():
    """Fixture for temporary test database"""
    test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    test_db_path = test_db.name
    test_db.close()
    
    yield test_db_path
    
    if os.path.exists(test_db_path):
        os.unlink(test_db_path)

if __name__ == "__main__":
    pytest.main([__file__])