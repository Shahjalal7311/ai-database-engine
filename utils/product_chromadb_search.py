import openai
import chromadb
from chromadb.utils import embedding_functions
from database.connection import db_connection
from config.settings import settings
from sqlalchemy import text

class ProductChromaDBSearch:
    def __init__(self):
        self.engine = db_connection.get_engine()
        self.api_key = settings.OPENAI_API_KEY
        self.chroma_client = chromadb.Client()
        try:
            self.collection = self.chroma_client.get_or_create_collection(
                name="products",
                embedding_function=embedding_functions.OpenAIEmbeddingFunction(
                    api_key=self.api_key,
                    model_name="text-embedding-ada-002"
                )
            )
        except Exception as e:
            if "already exists" in str(e):
                self.collection = self.chroma_client.get_collection(name="products")
            else:
                raise
        # Only add products if collection is empty
        if not self._collection_has_data():
            self._load_products_and_build_index()

    def _collection_has_data(self):
        # Try to fetch a single document; if exists, collection is not empty
        try:
            result = self.collection.query(query_texts=["test"], n_results=1)
            return bool(result.get('ids'))
        except Exception:
            return False

    def _load_products_and_build_index(self):
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT id, name, search_text, products_tags, description FROM products"))
            products = result.fetchall()
            for row in products:
                prod_id = str(row[0])
                text_val = f"{row[1]} {row[2]} {row[3]} {row[4]}"
                self.collection.add(
                    ids=[prod_id],
                    documents=[text_val],
                    metadatas=[{"name": row[1], "search_text": row[2], "products_tags": row[3], "description": row[4]}]
                )

    def search(self, query, top_k=5):
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        # Return product metadata for top results
        return results['metadatas'][0] if results['metadatas'] else []

    def rag_search(self, query, top_k=5):
        # Step 1: Retrieve top product documents
        results = self.search(query, top_k=top_k)
        if not results:
            return "No relevant products found."
        # Step 2: Build context from retrieved products
        context = "\n".join([
            f"Name: {prod.get('name', '')}\nDescription: {prod.get('description', '')}\nTags: {prod.get('products_tags', '')}\nSearch Text: {prod.get('search_text', '')}"
            for prod in results
        ])
        # Step 3: Construct prompt for LLM
        prompt = (
            f"You are a helpful assistant. Based on the following product information, answer the user's query.\n"
            f"User Query: {query}\n\nProduct Information:\n{context}\n\nProvide a concise and relevant answer:"
        )
        # Step 4: Call OpenAI GPT for generation
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            api_key=self.api_key
        )
        return response['choices'][0]['message']['content'].strip()
