from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from config.settings import settings

class DatabaseConnection:
    def __init__(self):
        self.db_url = settings.DATABASE_URL
        self.setup_connection()
    
    def setup_connection(self):
        """Initialize database connection without LangChain utilities"""
        try:
            self.engine = create_engine(
                self.db_url,
                poolclass=NullPool,
                connect_args={'charset': 'utf8mb4'}
            )
            print(f"Connected to {settings.DATABASE_TYPE} database successfully")
        except Exception as e:
            print(f"Database connection failed: {e}")
            raise
    
    def get_engine(self):
        return self.engine
    
    def test_connection(self):
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
db_connection = DatabaseConnection()