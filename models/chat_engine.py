from database.connection import db_connection
from chains.direct_query_generator import DirectQueryGenerator
from utils.safety_checker import QuerySafetyChecker
from utils.formatters import format_results
from config.settings import settings
from sqlalchemy import text
from langchain_core.prompts import PromptTemplate

class DatabaseChatEngine:
    def __init__(self):
        self.engine = db_connection.get_engine()
        self.query_generator = DirectQueryGenerator()
        self.chat_history = []
    
    def execute_query(self, query: str):
        """Execute SQL query safely with table restrictions"""
        safe_query = QuerySafetyChecker.add_safety_limits(query)
        
        if not QuerySafetyChecker.is_query_safe(safe_query):
            return None, "Query contains forbidden operations or accesses restricted tables"
        
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(safe_query))
                rows = result.fetchall()  # Always fetch all results
                columns = result.keys()
                result.close()  # Explicitly close result set for MySQL
                return columns, rows
        except Exception as e:
            return None, f"Query execution failed: {str(e)}"
    
    def generate_natural_response(self, question: str, query: str, results: str):
        """Generate natural language response from results"""
        from langchain_community.chat_models import ChatOpenAI
        
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        response_template = """
        You are a helpful data analyst assistant. Given a user question about articles,
        the SQL query used to answer it, and the query results, provide a clear response.
        
        Question: {question}
        SQL Query: {query}
        Results: {results}
        
        Provide a helpful and concise response:
        """
        
        prompt = PromptTemplate(
            input_variables=["question", "query", "results"],
            template=response_template
        )
        
        chain = prompt | llm
        response = chain.invoke({
            "question": question,
            "query": query,
            "results": results
        })
        
        return response.content
    
    def chat(self, question: str):
        """Main chat method for articles queries only"""
        try:
            sql_query = self.query_generator.generate_sql_query(question)           
            print(f"Generated SQL: {sql_query}")
            columns, rows = self.execute_query(sql_query)            
            if isinstance(rows, str):  # Error case
                return f"Error: {rows}"           
            formatted_results = format_results(columns, rows, settings.MAX_ROWS)
            response = self.generate_natural_response(
                question, sql_query, formatted_results
            )
            self.chat_history.append({
                "question": question,
                "response": response,
                "query": sql_query
            })
            
            return response
            
        except Exception as e:
            return f"Error processing your request: {str(e)}"
    
    def clear_history(self):
        """Clear chat history"""
        self.chat_history = []
    
    def get_history(self):
        """Get chat history"""
        return self.chat_history
    
    def get_allowed_tables(self):
        """Return list of allowed tables"""
        return settings.ALLOWED_TABLES
    
    # def search_products_by_vector(self, query, top_k=5):
    #     """Search products using OpenAI embeddings and FAISS vector search"""
    #     from utils.product_vector_search import ProductVectorSearch
    #     vector_search = ProductVectorSearch()
    #     results = vector_search.search(query, top_k=top_k)
    #     if not results:
    #         return "No similar products found."
    #     # Fetch product details for the top results
    #     with self.engine.connect() as conn:
    #         product_ids = [str(pid) for pid, _ in results]
    #         sql = f"SELECT id, name, description FROM products WHERE id IN ({', '.join(product_ids)})"
    #         rows = conn.execute(sql).fetchall()
    #         return [dict(id=row[0], name=row[1], description=row[2]) for row in rows]
    
    # def search_products_by_chromadb(self, query, top_k=5):
    #     """Search products using ChromaDB vector search"""
    #     from utils.product_chromadb_search import ProductChromaDBSearch
    #     chroma_search = ProductChromaDBSearch()
    #     results = chroma_search.search(query, top_k=top_k)
    #     if not results:
    #         return "No similar products found in ChromaDB."
    #     return results