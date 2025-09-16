import warnings
from models.chat_engine import DatabaseChatEngine
from database.connection import db_connection
from langchain.utilities.sql_database import SQLDatabase
import argparse

def main():
    warnings.filterwarnings("ignore", 
      message="Cannot correctly sort tables.*",
      category=UserWarning,
      module="langchain.utilities.sql_database")
    # Test database connection
    if not db_connection.test_connection():
        print("Database connection test failed. Please check your connection settings.")
        return
    
    # Initialize chat engine
    chat_engine = DatabaseChatEngine()
    
    print("=" * 60)
    print("PRODUCTS DATABASE CHAT ENGINE")
    print("=" * 60)
    print("This chat engine can only query the PRODUCTS table")
    print("Type your questions about products")
    print("Type 'history' to see chat history")
    print("Type 'clear' to clear history")
    print("Type 'tables' to see allowed tables")
    # print("Type 'vector <your query>' to search for similar products using vector search")
    # print("Type 'chromadb <your query>' to search for similar products using ChromaDB vector search")
    print("Type 'quit', 'exit', or 'q' to exit")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            elif user_input.lower() == 'history':
                history = chat_engine.get_history()
                if not history:
                    print("No chat history yet.")
                else:
                    for i, item in enumerate(history, 1):
                        print(f"\n[{i}] Q: {item['question']}")
                        print(f"   A: {item['response']}")
                        if 'query' in item:
                            print(f"   SQL: {item['query']}")
            elif user_input.lower() == 'clear':
                chat_engine.clear_history()
                print("Chat history cleared.")
            elif user_input.lower() == 'tables':
                tables = chat_engine.get_allowed_tables()
                print(f"Allowed tables: {', '.join(tables)}")
            # elif user_input.lower().startswith('vector '):
            #     query = user_input[7:].strip()
            #     results = chat_engine.search_products_by_vector(query)
            #     if isinstance(results, str):
            #         print(results)
            #     else:
            #         print("\nTop similar products:")
            #         for prod in results:
            #             print(f"- {prod['id']}: {prod['name']} | {prod['description']}")
            # elif user_input.lower().startswith('chromadb '):
            #     query = user_input[9:].strip()
            #     results = chat_engine.search_products_by_chromadb(query)
            #     if isinstance(results, str):
            #         print(results)
            #     else:
            #         print("\nTop similar products from ChromaDB:")
            #         for prod in results:
            #             print(f"- {prod.get('name', '')}: {prod.get('description', '')}")
            elif user_input:
                allowed_tables = chat_engine.get_allowed_tables()
                if 'articles' not in [t.lower() for t in allowed_tables]:
                    print("Error: ARTICLES table is not allowed for queries.")
                    continue
                # Optional: warn if input doesn't mention articles
                if not any(word in user_input.lower() for word in ['article', 'articles', 'item', 'stock']):
                    print("Warning: Your question may not be about the ARTICLES table. The assistant will only answer using ARTICLES data.")
                response = chat_engine.chat(user_input)
                print(f"\nAssistant: {response}")
            else:
                print("Please enter a question.")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Articles Database Chat Engine')
    parser.add_argument('--test', action='store_true', help='Test database connection')
    args = parser.parse_args()
    
    if args.test:
        if db_connection.test_connection():
            print("Database connection test: SUCCESS")
        else:
            print("Database connection test: FAILED")
    else:
        main()