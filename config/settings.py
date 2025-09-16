import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL')
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'mysql')
    MAX_ROWS = int(os.getenv('MAX_ROWS', 100))
    
    # Safety settings
    ALLOWED_OPERATIONS = ['SELECT']
    FORBIDDEN_KEYWORDS = ['DROP', 'DELETE', 'TRUNCATE', 'UPDATE', 'INSERT', 'ALTER']
    
    # Table restrictions
    ALLOWED_TABLES = ['articles']  # Only allow queries on articles table
    RESTRICTED_TABLES = []  # Empty since we're using allowlist approach

settings = Settings()