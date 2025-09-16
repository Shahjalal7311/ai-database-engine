from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from database.schema_inspector import SchemaInspector
from config.settings import settings

class DirectQueryGenerator:
    def __init__(self, table_name='articles'):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.schema_inspector = SchemaInspector()
        self.table_name = table_name
    
    def generate_sql_query(self, question: str):
        """Generate SQL query using direct prompt engineering"""
        schema = self.schema_inspector.get_table_schema(self.table_name)
        prompt_template = f"""
        You are an expert SQL developer. Given an input question, create a syntactically correct {{dialect}} query.
        Only return the SQL query, nothing else. Do not include any explanations or additional text.

        IMPORTANT RULES:
        1. Only use SELECT queries
        2. Only query from the '{self.table_name}' table
        3. Never use DROP, DELETE, UPDATE, INSERT, or ALTER
        4. Always include a LIMIT clause if not specified (default LIMIT 10)
        5. For "latest" records, use ORDER BY created_at DESC or updated_at DESC
        6. Use proper WHERE clauses to filter data

        Database schema for {self.table_name} table:
        {{schema}}

        Question: {{question}}

        SQL Query:
        """
        prompt = PromptTemplate(
            input_variables=["question", "schema", "dialect"],
            template=prompt_template
        )
        chain = prompt | self.llm
        response = chain.invoke({
            "question": question,
            "schema": schema,
            "dialect": settings.DATABASE_TYPE
        })
        sql_query = response.content.strip()
        if sql_query.startswith('```sql'):
            sql_query = sql_query[6:].strip()
        if sql_query.startswith('```'):
            sql_query = sql_query[3:].strip()
        if sql_query.endswith('```'):
            sql_query = sql_query[:-3].strip()
        return sql_query