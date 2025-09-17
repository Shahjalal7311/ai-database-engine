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
    ALLOWED_TABLES = ['articles', 'article_categories', 'categories', 'article_tags', 'tags', 'article_comments', 'article_likes']  # Allow queries on both tables
    RESTRICTED_TABLES = []  # Empty since we're using allowlist approach
    DEFAULT_TABLE = 'articles'  # Default table to query
    
    # Table relationships for dynamic JOIN instructions
    TABLE_RELATIONSHIPS = [
        {
            "from": "articles",
            "to": "article_categories",
            "on": "articles.id = article_categories.article_id"
        },
        {
            "from": "categories",
            "to": "article_categories",
            "on": "categories.id = article_categories.category_id"
        },
        {
            "from": "articles",
            "to": "article_tags",
            "on": "articles.id = article_tags.article_id"
        },
        {
            "from": "tags",
            "to": "article_tags",
            "on": "tags.id = article_tags.tag_id"
        },
        {
            "from": "articles",
            "to": "article_comments",
            "on": "articles.id = article_comments.article_id"
        },
        {
            "from": "articles",
            "to": "article_likes",
            "on": "articles.id = article_likes.article_id"
        },
    ]

settings = Settings()