# ==============================================================================
# HTTP STATUS CODES
# ==============================================================================

class HTTPStatus:
    """HTTP status codes used throughout the API"""
    OK = 200
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503


# ==============================================================================
# ERROR MESSAGES
# ==============================================================================

class ErrorMessages:
    """Standard error messages for consistent API responses"""
    GAME_NOT_FOUND = "Game not found"
    SIMULATION_DATA_NOT_FOUND = "Simulation data not found for one or both teams"
    NO_SIMULATIONS_FOR_TEAM = "No simulations found for this team"
    DATABASE_ERROR = "Database error occurred"
    SERVICE_UNAVAILABLE = "Service unavailable: {error}"
    DEBUG_ERROR = "Debug error: {error}"
    
    # Data loading errors
    ERROR_LOADING_CSV = "Error loading CSV data: {error}"
    ERROR_FETCHING_VENUES = "Error fetching venues: {error}"
    ERROR_FETCHING_GAMES = "Error fetching games: {error}"
    ERROR_FETCHING_GAME = "Error fetching game: {error}"
    ERROR_ANALYZING_GAME = "Error analyzing game: {error}"
    ERROR_GENERATING_HISTOGRAM = "Error generating histogram data: {error}"
    ERROR_FETCHING_TEAMS = "Error fetching teams: {error}"
    ERROR_FETCHING_SIMULATIONS = "Error fetching simulations: {error}"


# ==============================================================================
# DATABASE CONSTANTS
# ==============================================================================

class Database:
    """Database-related constants"""
    
    # Default database file
    DEFAULT_DATABASE_NAME = "cricket_data.db"
    
    # Table names
    class Tables:
        VENUES = "venues"
        GAMES = "games"
        SIMULATIONS = "simulations"
    
    # Column names
    class Columns:
        # Venues table
        VENUE_ID = "venue_id"
        VENUE_NAME = "venue_name"
        
        # Games table
        GAME_ID = "id"
        HOME_TEAM = "home_team"
        AWAY_TEAM = "away_team"
        DATE = "date"
        GAME_VENUE_ID = "venue_id"
        
        # Simulations table
        SIMULATION_ID = "id"
        TEAM_ID = "team_id"
        TEAM = "team"
        SIMULATION_RUN = "simulation_run"
        RESULTS = "results"
        
        # Generic columns
        COUNT = "count"
        TEAM_ALIAS = "team"
    
    # SQL queries
    class Queries:
        # Table creation
        CREATE_VENUES_TABLE = """
            CREATE TABLE IF NOT EXISTS venues (
                venue_id INTEGER PRIMARY KEY,
                venue_name TEXT NOT NULL
            )
        """
        
        CREATE_GAMES_TABLE = """
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                date TEXT,
                venue_id INTEGER,
                FOREIGN KEY (venue_id) REFERENCES venues (venue_id)
            )
        """
        
        CREATE_SIMULATIONS_TABLE = """
            CREATE TABLE IF NOT EXISTS simulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER,
                team TEXT,
                simulation_run INTEGER,
                results INTEGER
            )
        """
        
        # Data selection
        SELECT_VENUES = "SELECT venue_id as id, venue_name as name FROM venues"
        
        SELECT_GAMES_WITH_VENUES = """
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
        
        SELECT_GAME_BY_ID = """
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
        
        SELECT_TEAM_SIMULATIONS = "SELECT results FROM simulations WHERE team = ?"
        
        SELECT_ALL_TEAMS = """
            SELECT DISTINCT home_team as team FROM games
            UNION
            SELECT DISTINCT away_team as team FROM games
            ORDER BY team
        """
        
        SELECT_TEAM_SIMULATION_DETAILS = """
            SELECT * FROM simulations WHERE team = ? ORDER BY simulation_run
        """
        
        # Debug queries
        COUNT_RECORDS = "SELECT COUNT(*) as count FROM {table}"
        SAMPLE_RECORDS = "SELECT * FROM {table} LIMIT {limit}"
        
        # Health check
        HEALTH_CHECK = "SELECT 1"


# ==============================================================================
# FILE PATHS AND CSV CONFIGURATION
# ==============================================================================

class FilePaths:
    """File paths and CSV configuration"""
    
    # Default directory structure
    DEFAULT_DATA_DIRECTORY = "data"
    
    # CSV file names
    class CSVFiles:
        GAMES = "games.csv"
        VENUES = "venues.csv"
        SIMULATIONS = "simulations.csv"
    
    # CSV column mappings for validation
    class CSVColumns:
        # Expected columns in games.csv
        GAMES_REQUIRED = ["home_team", "away_team", "venue_id"]
        GAMES_OPTIONAL = ["date", "id"]
        
        # Expected columns in venues.csv
        VENUES_REQUIRED = ["venue_id", "venue_name"]
        
        # Expected columns in simulations.csv
        SIMULATIONS_REQUIRED = ["team_id", "team", "simulation_run", "results"]


# ==============================================================================
# API CONFIGURATION
# ==============================================================================

class API:
    """API configuration constants"""
    
    # Default API settings
    DEFAULT_TITLE = "Cricket Data API"
    DEFAULT_VERSION = "1.0.0"
    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 8000
    
    # Environment values
    class Environments:
        DEVELOPMENT = "development"
        PRODUCTION = "production"
        VALID_ENVIRONMENTS = [DEVELOPMENT, PRODUCTION]
    
    # CORS settings
    class CORS:
        DEFAULT_ORIGINS_DEV = "http://localhost:3000,http://localhost:5500"
        DEFAULT_ORIGINS_PROD = "https://your-production-domain.com"
        ALLOWED_METHODS = ["*"]
        ALLOWED_HEADERS = ["*"]
    
    # Response messages
    class ResponseMessages:
        API_RUNNING = "{title} is running"
        HEALTH_STATUS_HEALTHY = "healthy"
        DATABASE_CONNECTED = "connected"


# ==============================================================================
# BUSINESS LOGIC CONSTANTS
# ==============================================================================

class BusinessLogic:
    """Business logic and calculation constants"""
    
    # Histogram configuration
    class Histogram:
        DEFAULT_BIN_SIZE = 10  # Score ranges of 10 points (e.g., 120-129, 130-139)
        DEFAULT_BAR_WIDTH = 40
        DEFAULT_BAR_GAP = 10
        DEFAULT_CHART_HEIGHT = 300
        DEFAULT_LEFT_MARGIN = 80
        DEFAULT_RIGHT_MARGIN = 20
        
        # Chart styling
        GRID_LINE_COLOR = "#e5e7eb"
        GRID_LINE_WIDTH = "1"
        HOME_TEAM_COLOR = "#3b82f6"  # Blue
        AWAY_TEAM_COLOR = "#ef4444"  # Red
        TEXT_COLOR = "#666"
        LABEL_FONT_SIZE = "10"
        TITLE_FONT_SIZE = "12"
        
        # Y-axis configuration
        DEFAULT_Y_TICKS = 5
        Y_AXIS_ROUNDING = 5  # Round up to nearest 5 for max percentage
    
    # Win probability calculation
    class WinProbability:
        PERCENTAGE_MULTIPLIER = 100
        DECIMAL_PLACES = 2
    
    # Data limits and validation
    class DataLimits:
        MAX_SIMULATION_RUNS = 10000
        MIN_SIMULATION_RUNS = 1
        MAX_TEAMS_PER_GAME = 2
        MAX_SCORE = 500  # Reasonable cricket score limit
        MIN_SCORE = 0
        DEFAULT_SAMPLE_LIMIT = 3


# ==============================================================================
# FRONTEND INTEGRATION CONSTANTS
# ==============================================================================

class Frontend:
    """Constants for frontend integration"""
    
    # API base URLs
    class BaseURLs:
        DEVELOPMENT = "http://localhost:8000"
        PRODUCTION = "https://api.your-domain.com"
    
    # Chart dimensions (for consistency with frontend)
    class ChartDimensions:
        MIN_SVG_WIDTH = 640
        RESPONSIVE_BREAKPOINT = 768
    
    # Data format expectations
    class DataFormats:
        DATE_FORMAT = "%Y-%m-%d"
        SCORE_STRING_FORMAT = "{score}"  # Scores converted to strings for frontend


# ==============================================================================
# TESTING CONSTANTS
# ==============================================================================

class Testing:
    """Constants for testing and mocking"""
    
    # Test data limits
    class TestData:
        SAMPLE_RECORD_LIMIT = 3
        TEST_TEAM_COUNT = 10
        TEST_VENUE_COUNT = 5
        TEST_SIMULATION_COUNT = 100
        DEFAULT_TEST_SIMULATIONS = 5
    
    # Mock values
    class MockValues:
        TEST_DATABASE_SUFFIX = ".db"
        TEST_GAME_ID = 1
        TEST_TEAM_NAME = "Test Team"
        TEST_VENUE_NAME = "Test Ground"
        TEST_VENUE_ID = 0
        TEST_TEAM_A = "Team A"
        TEST_TEAM_B = "Team B"
        TEST_DATE = "2024-01-01"
        
        # Default test scores
        DEFAULT_HOME_SCORE = 150
        DEFAULT_AWAY_SCORE = 145
        SCORE_VARIANCE = 25


# ==============================================================================
# LOGGING AND MONITORING
# ==============================================================================

class Logging:
    """Logging and monitoring constants"""
    
    # Log message templates
    class Messages:
        CSV_LOADED = "Loaded {count} {type} from {path}"
        DATABASE_INITIALIZED = "Database initialized successfully"
        STARTUP_COMPLETE = "Application startup complete"
        HEALTH_CHECK_PASSED = "Health check passed"
        HEALTH_CHECK_FAILED = "Health check failed: {error}"
    
    # Log levels
    class Levels:
        DEBUG = "DEBUG"
        INFO = "INFO"
        WARNING = "WARNING"
        ERROR = "ERROR"
        CRITICAL = "CRITICAL"


# ==============================================================================
# VALIDATION CONSTANTS
# ==============================================================================

class Validation:
    """Data validation constants"""
    
    # String length limits
    class StringLimits:
        MAX_TEAM_NAME_LENGTH = 100
        MAX_VENUE_NAME_LENGTH = 200
        MAX_ERROR_MESSAGE_LENGTH = 500
    
    # Numeric limits
    class NumericLimits:
        MAX_VENUE_ID = 9999
        MIN_VENUE_ID = 0
        MAX_TEAM_ID = 9999
        MIN_TEAM_ID = 0


# ==============================================================================
# PERFORMANCE CONSTANTS
# ==============================================================================

class Performance:
    """Performance-related constants"""
    
    # Database query limits
    class QueryLimits:
        DEFAULT_RECORD_LIMIT = 1000
        MAX_RECORD_LIMIT = 10000
        PAGINATION_SIZE = 50
    
    # Cache settings
    class Cache:
        DEFAULT_TTL = 300  # 5 minutes
        MAX_CACHE_SIZE = 1000
    
    # Connection settings
    class Connection:
        DEFAULT_TIMEOUT = 30  # seconds
        MAX_RETRIES = 3
        RETRY_DELAY = 1  # seconds


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def get_http_status_message(status_code: int) -> str:
    """Get human-readable message for HTTP status code"""
    status_messages = {
        HTTPStatus.OK: "Success",
        HTTPStatus.NOT_FOUND: "Resource not found",
        HTTPStatus.INTERNAL_SERVER_ERROR: "Internal server error",
        HTTPStatus.SERVICE_UNAVAILABLE: "Service unavailable"
    }
    return status_messages.get(status_code, f"HTTP {status_code}")


def format_error_message(template: str, **kwargs) -> str:
    """Format error message template with provided arguments"""
    try:
        return template.format(**kwargs)
    except KeyError as e:
        return f"Error formatting message template: missing key {e}"


def validate_environment(env: str) -> bool:
    """Validate if environment value is allowed"""
    return env.lower() in API.Environments.VALID_ENVIRONMENTS


# ==============================================================================
# VERSION INFO
# ==============================================================================

__version__ = "1.0.0"
__author__ = "Cricket Data App Team"
__description__ = "Centralized constants for the Cricket Data App"