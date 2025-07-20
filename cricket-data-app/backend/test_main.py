import pytest
import sqlite3
import tempfile
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd

from main import app, init_database, load_csv_data
from app.constants import (
    HTTPStatus, ErrorMessages, Database, Testing,
    FilePaths, BusinessLogic, API
)

client = TestClient(app)

class TestDatabaseSetup:
    """Test database initialization and CSV loading"""
    
    def setup_method(self):
        """Setup test database for each test"""
        self.test_db = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=Testing.MockValues.TEST_DATABASE_SUFFIX
        )
        self.test_db_path = self.test_db.name
        self.test_db.close()
    
    def teardown_method(self):
        """Clean up test database after each test"""
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)
    
    def test_init_database(self):
        """Test database initialization creates all required tables"""
        with patch('main.config.database_path', self.test_db_path):
            init_database()
        
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert Database.Tables.VENUES in tables
        assert Database.Tables.GAMES in tables
        assert Database.Tables.SIMULATIONS in tables
        
        conn.close()
    
    def test_database_tables_structure(self):
        """Test that database tables have correct structure"""
        with patch('main.config.database_path', self.test_db_path):
            init_database()
        
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        cursor.execute(f"PRAGMA table_info({Database.Tables.VENUES})")
        venues_columns = [row[1] for row in cursor.fetchall()]
        assert Database.Columns.VENUE_ID in venues_columns
        assert Database.Columns.VENUE_NAME in venues_columns
        
        cursor.execute(f"PRAGMA table_info({Database.Tables.GAMES})")
        games_columns = [row[1] for row in cursor.fetchall()]
        assert Database.Columns.GAME_ID in games_columns
        assert Database.Columns.HOME_TEAM in games_columns
        assert Database.Columns.AWAY_TEAM in games_columns
        
        conn.close()

class TestCSVLoading:
    """Test CSV data loading functionality"""
    
    def setup_method(self):
        self.test_db = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=Testing.MockValues.TEST_DATABASE_SUFFIX
        )
        self.test_db_path = self.test_db.name
        self.test_db.close()
        
        self.test_venues_data = pd.DataFrame({
            Database.Columns.VENUE_ID: [0, 1, 2],
            Database.Columns.VENUE_NAME: [
                f'{Testing.MockValues.TEST_VENUE_NAME} 1',
                f'{Testing.MockValues.TEST_VENUE_NAME} 2',
                f'{Testing.MockValues.TEST_VENUE_NAME} 3'
            ]
        })
        
        self.test_games_data = pd.DataFrame({
            Database.Columns.HOME_TEAM: [Testing.MockValues.TEST_TEAM_A, Testing.MockValues.TEST_TEAM_B],
            Database.Columns.AWAY_TEAM: [Testing.MockValues.TEST_TEAM_B, Testing.MockValues.TEST_TEAM_A],
            Database.Columns.DATE: [Testing.MockValues.TEST_DATE, '2024-01-02'],
            Database.Columns.GAME_VENUE_ID: [0, 1]
        })
        
        self.test_simulations_data = pd.DataFrame({
            Database.Columns.TEAM_ID: [0, 0, 1, 1],
            Database.Columns.TEAM: [Testing.MockValues.TEST_TEAM_A, Testing.MockValues.TEST_TEAM_A, 
                                   Testing.MockValues.TEST_TEAM_B, Testing.MockValues.TEST_TEAM_B],
            Database.Columns.SIMULATION_RUN: [1, 2, 1, 2],
            Database.Columns.RESULTS: [
                Testing.MockValues.DEFAULT_HOME_SCORE, 
                Testing.MockValues.DEFAULT_HOME_SCORE + 10,
                Testing.MockValues.DEFAULT_AWAY_SCORE, 
                Testing.MockValues.DEFAULT_AWAY_SCORE + 5
            ]
        })
    
    def teardown_method(self):
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)
    
    @patch('pandas.read_csv')
    @patch('os.path.exists')
    def test_load_csv_data_success(self, mock_exists, mock_read_csv):
        """Test successful CSV data loading"""
        mock_exists.return_value = True
        
        def mock_csv_side_effect(filename):
            if FilePaths.CSVFiles.VENUES in filename:
                return self.test_venues_data
            elif FilePaths.CSVFiles.GAMES in filename:
                return self.test_games_data
            elif FilePaths.CSVFiles.SIMULATIONS in filename:
                return self.test_simulations_data
            return pd.DataFrame()
        
        mock_read_csv.side_effect = mock_csv_side_effect
        
        with patch('main.config.database_path', self.test_db_path):
            init_database()
            load_csv_data()
        
        conn = sqlite3.connect(self.test_db_path)
        
        venues = pd.read_sql_query(f"SELECT * FROM {Database.Tables.VENUES}", conn)
        assert len(venues) == 3
        
        games = pd.read_sql_query(f"SELECT * FROM {Database.Tables.GAMES}", conn)
        assert len(games) == 2
        
        conn.close()

class TestAPIEndpoints:
    """Test FastAPI endpoints"""
    
    def setup_method(self):
        """Setup test data before each test"""
        self.test_db = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=Testing.MockValues.TEST_DATABASE_SUFFIX
        )
        self.test_db_path = self.test_db.name
        self.test_db.close()
        
        # Initialize test database with sample data
        with patch('main.config.database_path', self.test_db_path):
            init_database()
            self._insert_test_data()
    
    def teardown_method(self):
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)
    
    def _insert_test_data(self):
        """Insert test data into database using constants"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            f"INSERT INTO {Database.Tables.VENUES} ({Database.Columns.VENUE_ID}, {Database.Columns.VENUE_NAME}) VALUES (?, ?)",
            (Testing.MockValues.TEST_VENUE_ID, Testing.MockValues.TEST_VENUE_NAME)
        )
        
        cursor.execute(f"""
            INSERT INTO {Database.Tables.GAMES}
            ({Database.Columns.GAME_ID}, {Database.Columns.HOME_TEAM}, {Database.Columns.AWAY_TEAM}, {Database.Columns.DATE}, {Database.Columns.GAME_VENUE_ID}) 
            VALUES (?, ?, ?, ?, ?)
        """, (Testing.MockValues.TEST_GAME_ID, Testing.MockValues.TEST_TEAM_A,
              Testing.MockValues.TEST_TEAM_B, Testing.MockValues.TEST_DATE, Testing.MockValues.TEST_VENUE_ID))
        
        for i in range(Testing.TestData.DEFAULT_TEST_SIMULATIONS):
            cursor.execute(f"""
                INSERT INTO {Database.Tables.SIMULATIONS}
                ({Database.Columns.TEAM_ID}, {Database.Columns.TEAM}, {Database.Columns.SIMULATION_RUN}, {Database.Columns.RESULTS}) 
                VALUES (?, ?, ?, ?)
            """, (0, Testing.MockValues.TEST_TEAM_A, i+1, Testing.MockValues.DEFAULT_HOME_SCORE + i))
            
            cursor.execute(f"""
                INSERT INTO {Database.Tables.SIMULATIONS} 
                ({Database.Columns.TEAM_ID}, {Database.Columns.TEAM}, {Database.Columns.SIMULATION_RUN}, {Database.Columns.RESULTS}) 
                VALUES (?, ?, ?, ?)
            """, (1, Testing.MockValues.TEST_TEAM_B, i+1, Testing.MockValues.DEFAULT_AWAY_SCORE + i))
        
        conn.commit()
        conn.close()
    
    def test_root_endpoint(self):
        """Test root endpoint returns API status"""
        with patch('main.config.database_path', self.test_db_path):
            response = client.get("/")
            assert response.status_code == HTTPStatus.OK
            data = response.json()
            assert "message" in data
            assert "environment" in data
            assert "version" in data
    
    def test_get_venues(self):
        """Test venues endpoint"""
        with patch('main.config.database_path', self.test_db_path):
            response = client.get("/venues")
            assert response.status_code == HTTPStatus.OK
            venues = response.json()
            assert len(venues) == 1
            assert venues[0]["name"] == Testing.MockValues.TEST_VENUE_NAME
    
    def test_get_games(self):
        """Test games endpoint"""
        with patch('main.config.database_path', self.test_db_path):
            response = client.get("/games")
            assert response.status_code == HTTPStatus.OK
            games = response.json()
            assert len(games) == 1
            assert games[0][Database.Columns.HOME_TEAM] == Testing.MockValues.TEST_TEAM_A
    
    def test_get_game_by_id(self):
        """Test get specific game by ID"""
        with patch('main.config.database_path', self.test_db_path):
            response = client.get(f"/games/{Testing.MockValues.TEST_GAME_ID}")
            assert response.status_code == HTTPStatus.OK
            game = response.json()
            assert game[Database.Columns.HOME_TEAM] == Testing.MockValues.TEST_TEAM_A
            assert game[Database.Columns.AWAY_TEAM] == Testing.MockValues.TEST_TEAM_B
    
    def test_get_game_by_id_not_found(self):
        """Test get game by ID when game doesn't exist"""
        with patch('main.config.database_path', self.test_db_path):
            response = client.get("/games/999")
            assert response.status_code == HTTPStatus.NOT_FOUND
            assert ErrorMessages.GAME_NOT_FOUND in response.json()["detail"]
    
    def test_get_game_analysis(self):
        """Test game analysis endpoint"""
        with patch('main.config.database_path', self.test_db_path):
            response = client.get(f"/games/{Testing.MockValues.TEST_GAME_ID}/analysis")
            assert response.status_code == HTTPStatus.OK
            analysis = response.json()
            assert "game" in analysis
            assert "simulations" in analysis
            assert "home_win_probability" in analysis
            assert "total_simulations" in analysis
            assert analysis["total_simulations"] == Testing.TestData.DEFAULT_TEST_SIMULATIONS
    
    def test_get_histogram_data(self):
        """Test histogram data endpoint"""
        with patch('main.config.database_path', self.test_db_path):
            response = client.get(f"/games/{Testing.MockValues.TEST_GAME_ID}/histogram-data")
            assert response.status_code == HTTPStatus.OK
            histogram = response.json()
            assert Database.Columns.HOME_TEAM in histogram
            assert Database.Columns.AWAY_TEAM in histogram
            assert "home_scores" in histogram
            assert "away_scores" in histogram
            assert "score_range" in histogram
    
    def test_get_teams(self):
        """Test teams endpoint"""
        with patch('main.config.database_path', self.test_db_path):
            response = client.get("/teams")
            assert response.status_code == HTTPStatus.OK
            teams = response.json()
            assert Testing.MockValues.TEST_TEAM_A in teams
            assert Testing.MockValues.TEST_TEAM_B in teams
    
    def test_get_team_simulations(self):
        """Test team simulations endpoint"""
        with patch('main.config.database_path', self.test_db_path):
            response = client.get(f"/simulations/{Testing.MockValues.TEST_TEAM_A}")
            assert response.status_code == HTTPStatus.OK
            simulations = response.json()
            assert len(simulations) == Testing.TestData.DEFAULT_TEST_SIMULATIONS
            assert all(sim[Database.Columns.TEAM] == Testing.MockValues.TEST_TEAM_A for sim in simulations)
    
    def test_get_team_simulations_not_found(self):
        """Test team simulations when team doesn't exist"""
        with patch('main.config.database_path', self.test_db_path):
            response = client.get("/simulations/NonexistentTeam")
            assert response.status_code == HTTPStatus.NOT_FOUND
            assert ErrorMessages.NO_SIMULATIONS_FOR_TEAM in response.json()["detail"]
    
    def test_health_check(self):
        """Test health check endpoint"""
        with patch('main.config.database_path', self.test_db_path):
            response = client.get("/health")
            assert response.status_code == HTTPStatus.OK
            health = response.json()
            assert health["status"] == API.ResponseMessages.HEALTH_STATUS_HEALTHY
            assert health["database"] == API.ResponseMessages.DATABASE_CONNECTED
    
    def test_debug_data_status(self):
        """Test debug data status endpoint"""
        with patch('main.config.database_path', self.test_db_path):
            response = client.get("/debug/data-status")
            assert response.status_code == HTTPStatus.OK
            status = response.json()
            assert "config" in status
            assert "files_status" in status
            assert "tables_info" in status
            
            # Check tables info using constants
            tables_info = status["tables_info"]
            assert Database.Tables.VENUES in tables_info
            assert Database.Tables.GAMES in tables_info
            assert Database.Tables.SIMULATIONS in tables_info

class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_database_connection_error(self):
        """Test handling of database connection errors"""
        with patch('main.get_database_connection') as mock_conn:
            mock_conn.side_effect = sqlite3.Error("Database connection failed")
            response = client.get("/venues")
            assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    
    def test_invalid_game_id_type(self):
        """Test handling of invalid game ID types"""
        response = client.get("/games/invalid_id")
        assert response.status_code == 422

class TestBusinessLogicCalculations:
    """Test business logic calculations using constants"""
    
    def setup_method(self):
        self.test_db = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=Testing.MockValues.TEST_DATABASE_SUFFIX
        )
        self.test_db_path = self.test_db.name
        self.test_db.close()
        
        with patch('main.config.database_path', self.test_db_path):
            init_database()
            self._insert_win_probability_test_data()
    
    def teardown_method(self):
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)
    
    def _insert_win_probability_test_data(self):
        """Insert specific test data for win probability calculations"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Insert test venue
        cursor.execute(
            f"INSERT INTO {Database.Tables.VENUES} ({Database.Columns.VENUE_ID}, {Database.Columns.VENUE_NAME}) VALUES (?, ?)",
            (Testing.MockValues.TEST_VENUE_ID, Testing.MockValues.TEST_VENUE_NAME)
        )
        
        # Insert test game
        cursor.execute(f"""
            INSERT INTO {Database.Tables.GAMES}
            ({Database.Columns.GAME_ID}, {Database.Columns.HOME_TEAM}, {Database.Columns.AWAY_TEAM}, {Database.Columns.DATE}, {Database.Columns.GAME_VENUE_ID}) 
            VALUES (?, ?, ?, ?, ?)
        """, (Testing.MockValues.TEST_GAME_ID, Testing.MockValues.TEST_TEAM_A,
              Testing.MockValues.TEST_TEAM_B, Testing.MockValues.TEST_DATE, Testing.MockValues.TEST_VENUE_ID))
        
        # Insert simulations where home team always wins (for predictable testing)
        for i in range(Testing.TestData.DEFAULT_TEST_SIMULATIONS):
            # Home team scores higher
            cursor.execute(f"""
                INSERT INTO {Database.Tables.SIMULATIONS} 
                ({Database.Columns.TEAM_ID}, {Database.Columns.TEAM}, {Database.Columns.SIMULATION_RUN}, {Database.Columns.RESULTS}) 
                VALUES (?, ?, ?, ?)
            """, (0, Testing.MockValues.TEST_TEAM_A, i+1, Testing.MockValues.DEFAULT_HOME_SCORE + 20))
            
            # Away team scores lower
            cursor.execute(f"""
                INSERT INTO {Database.Tables.SIMULATIONS} 
                ({Database.Columns.TEAM_ID}, {Database.Columns.TEAM}, {Database.Columns.SIMULATION_RUN}, {Database.Columns.RESULTS}) 
                VALUES (?, ?, ?, ?)
            """, (1, Testing.MockValues.TEST_TEAM_B, i+1, Testing.MockValues.DEFAULT_AWAY_SCORE))
        
        conn.commit()
        conn.close()
    
    def test_win_probability_calculation(self):
        """Test win probability calculation uses correct constants"""
        with patch('main.config.database_path', self.test_db_path):
            response = client.get(f"/games/{Testing.MockValues.TEST_GAME_ID}/analysis")
            assert response.status_code == HTTPStatus.OK
            analysis = response.json()
            
            # As home team always wins in our test data, probability should be 100%
            expected_probability = BusinessLogic.WinProbability.PERCENTAGE_MULTIPLIER
            assert analysis["home_win_probability"] == expected_probability
            
            # Checks decimal places using constant
            probability_str = str(analysis["home_win_probability"])
            if '.' in probability_str:
                decimal_places = len(probability_str.split('.')[1])
                assert decimal_places <= BusinessLogic.WinProbability.DECIMAL_PLACES

if __name__ == "__main__":
    pytest.main([__file__])