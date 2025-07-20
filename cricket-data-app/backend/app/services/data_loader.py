import os
import pandas as pd
from typing import Dict, Any
from app.config import get_environment_settings
from app.database.connection import db_manager
from app.constants import Database, Logging, ErrorMessages, format_error_message


class DataLoaderService:
    """Service for loading CSV data into database."""
    
    def __init__(self):
        self.config = get_environment_settings()
    
    def load_all_csv_data(self) -> bool:
        """Load all CSV files into database."""
        try:
            success = True
            success &= self._load_venues()
            success &= self._load_games()
            success &= self._load_simulations()
            
            if success:
                print(Logging.Messages.STARTUP_COMPLETE)
            
            return success
        except Exception as e:
            print(format_error_message(ErrorMessages.ERROR_LOADING_CSV, error=str(e)))
            return False
    
    def _load_venues(self) -> bool:
        """Load venues CSV data."""
        return self._load_csv_file(
            self.config.venues_path,
            Database.Tables.VENUES,
            "venues"
        )
    
    def _load_games(self) -> bool:
        """Load games CSV data."""
        if not os.path.exists(self.config.games_path):
            return False
        
        try:
            games_df = pd.read_csv(self.config.games_path)
            
            # Add ID column if not present
            if Database.Columns.GAME_ID not in games_df.columns:
                games_df = games_df.reset_index()
                games_df[Database.Columns.GAME_ID] = games_df.index + 1
            
            return self._save_dataframe_to_db(games_df, Database.Tables.GAMES, "games")
        except Exception as e:
            print(format_error_message(ErrorMessages.ERROR_LOADING_CSV, error=str(e)))
            return False
    
    def _load_simulations(self) -> bool:
        """Load simulations CSV data."""
        return self._load_csv_file(
            self.config.simulations_path,
            Database.Tables.SIMULATIONS,
            "simulations"
        )
    
    def _load_csv_file(self, file_path: str, table_name: str, data_type: str) -> bool:
        """Generic CSV file loading method."""
        if not os.path.exists(file_path):
            return False
        
        try:
            df = pd.read_csv(file_path)
            return self._save_dataframe_to_db(df, table_name, data_type)
        except Exception as e:
            print(format_error_message(ErrorMessages.ERROR_LOADING_CSV, error=str(e)))
            return False
    
    def _save_dataframe_to_db(self, df: pd.DataFrame, table_name: str, data_type: str) -> bool:
        """Save DataFrame to database table."""
        try:
            conn = db_manager.get_connection()
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            conn.close()
            
            print(Logging.Messages.CSV_LOADED.format(
                count=len(df),
                type=data_type,
                path=f"{data_type}.csv"
            ))
            return True
        except Exception as e:
            print(format_error_message(ErrorMessages.ERROR_LOADING_CSV, error=str(e)))
            return False
    
    def get_data_status(self) -> Dict[str, Any]:
        """Get status of all data files and database tables."""
        try:
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            # Check file existence
            files_status = {
                "venues_csv": os.path.exists(self.config.venues_path),
                "games_csv": os.path.exists(self.config.games_path),
                "simulations_csv": os.path.exists(self.config.simulations_path)
            }
            
            # Check table data
            tables_info = {}
            for table in [Database.Tables.VENUES, Database.Tables.GAMES, Database.Tables.SIMULATIONS]:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    tables_info[table] = {"row_count": count, "exists": True}
                except Exception:
                    tables_info[table] = {"row_count": 0, "exists": False}
            
            conn.close()
            
            return {
                "config": {
                    "database_path": self.config.database_path,
                    "data_directory": self.config.data_directory
                },
                "files_status": files_status,
                "tables_info": tables_info
            }
        except Exception as e:
            return {"error": str(e)}