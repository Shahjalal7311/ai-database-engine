from langchain.chains import create_sql_query_chain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from database.connection import db_connection
from database.manual_schema import ManualSchemaProvider
from config.settings import settings

class QueryChainManager:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.db = db_connection.get_db()
        self.schema_provider = ManualSchemaProvider()
    
    def create_query_prompt(self):
        """Create proper prompt for SQL query generation"""
        prompt_template = """
        You are an expert SQL developer. Given an input question, create a syntactically correct {dialect} query.
        Only return the SQL query, nothing else.

        IMPORTANT RULES:
        1. Only use SELECT queries
        2. Only query from the 'articles' table
        3. Never use DROP, DELETE, UPDATE, INSERT, or ALTER
        4. Always include a LIMIT clause if not specified
        5. For "latest" articles, use ORDER BY created_at DESC or updated_at DESC

        Database schema:
        {schema}

        Question: {question}

        SQL Query:
        """
        
        return PromptTemplate(
            input_variables=["question", "dialect", "schema"],
            template=prompt_template
        )
    
    def get_query_chain(self):
        """Get the SQL query generation chain"""
        prompt = self.create_query_prompt()
        
        # Use create_sql_query_chain but with our manual schema
        from langchain.chains import LLMChain
        
        return LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_key="query"
        )
    
    def generate_query(self, question):
        """Generate SQL query using manual schema"""
        schema_info = self.schema_provider.get_table_schema()
        chain = self.get_query_chain()
        result = chain.run({
            "question": question,
            "dialect": settings.DATABASE_TYPE,
            "schema": schema_info
        })
        
        return result.strip()