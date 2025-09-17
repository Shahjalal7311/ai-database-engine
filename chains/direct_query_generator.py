from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from database.schema_inspector import SchemaInspector
from config.settings import settings

class DirectQueryGenerator:
    def __init__(self, table_name=None):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.schema_inspector = SchemaInspector()
        self.table_name = table_name or getattr(settings, 'DEFAULT_TABLE', None) or (settings.ALLOWED_TABLES[0] if settings.ALLOWED_TABLES else settings.DEFAULT_TABLE)
    
    def generate_sql_query(self, question: str):
        """Generate SQL query using direct prompt engineering"""
        # Dynamically get schemas for all allowed tables
        table_schemas = {}
        for table in settings.ALLOWED_TABLES:
            table_schemas[table] = self.schema_inspector.get_table_schema(table)
        # Build schema section for prompt
        schema_section = "\n".join([
            f"Database schema for {table} table:\n{{{table}_schema}}" for table in settings.ALLOWED_TABLES
        ])
        # Build dynamic JOIN instructions
        join_instructions = ""
        if hasattr(settings, "TABLE_RELATIONSHIPS"):
            join_instructions = "3. Use JOINs to relate tables as follows:\n"
            for rel in settings.TABLE_RELATIONSHIPS:
                join_instructions += f"   - {rel['from']} <-> {rel['to']}: {rel['on']}\n"
        prompt_template = f"""
        You are an expert SQL developer. Given an input question, create a syntactically correct {{dialect}} query.
        Only return the SQL query, nothing else. Do not include any explanations or additional text.

        IMPORTANT RULES:
        1. Only use SELECT queries
        2. You may query from the following tables: {', '.join(settings.ALLOWED_TABLES)}
        {join_instructions}4. Never use DROP, DELETE, UPDATE, INSERT, or ALTER
        5. Always include a LIMIT clause if not specified (default LIMIT 10)
        6. For "latest" records, use ORDER BY created_at DESC or updated_at DESC
        7. Use proper WHERE clauses to filter data

        {schema_section}

        Question: {{question}}

        SQL Query:
        """
        input_vars = ["question", "dialect"] + [f"{table}_schema" for table in settings.ALLOWED_TABLES]
        prompt = PromptTemplate(
            input_variables=input_vars,
            template=prompt_template
        )
        chain = prompt | self.llm
        inputs = {"question": question, "dialect": settings.DATABASE_TYPE}
        for table in settings.ALLOWED_TABLES:
            inputs[f"{table}_schema"] = table_schemas[table]
        response = chain.invoke(inputs)
        sql_query = response.content.strip()
        if sql_query.startswith('```sql'):
            sql_query = sql_query[6:].strip()
        if sql_query.startswith('```'):
            sql_query = sql_query[3:].strip()
        if sql_query.endswith('```'):
            sql_query = sql_query[:-3].strip()
        return sql_query