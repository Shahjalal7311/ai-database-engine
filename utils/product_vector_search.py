import openai
import faiss
import numpy as np
from database.connection import db_connection
from config.settings import settings
from sqlalchemy import text

class ProductVectorSearch:
    def __init__(self):
        self.engine = db_connection.get_engine()
        self.api_key = settings.OPENAI_API_KEY
        self.embeddings = None
        self.product_ids = None
        self.index = None
        self._load_products_and_build_index()

    def _get_openai_embedding(self, ptxt):
        try:
            response = openai.Embedding.create(
                input=ptxt,
                model="text-embedding-ada-002",
                api_key=self.api_key
            )
            return np.array(response['data'][0]['embedding'], dtype=np.float32)
        except Exception as e:
            print(f"OpenAI embedding error: {e}")
            return np.zeros(1536, dtype=np.float32)  # fallback shape for ada-002

    def _load_products_and_build_index(self):
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT id, name, description FROM products"))
            rows = result.fetchall()
            result.close()
            if not rows:
                self.product_ids = []
                self.embeddings = np.zeros((0, 1536), dtype=np.float32)
                self.index = faiss.IndexFlatL2(1536)
                return
            product_texts = [f"{row[1]} {row[2]}" for row in rows]
            self.product_ids = [row[0] for row in rows]
            self.embeddings = np.array([
                self._get_openai_embedding(ptxt) for ptxt in product_texts
            ])
            self.index = faiss.IndexFlatL2(self.embeddings.shape[1])
            self.index.add(self.embeddings)

    def search(self, query, top_k=5):
        query_vec = self._get_openai_embedding(query)
        D, I = self.index.search(np.array([query_vec]), top_k)
        results = [(self.product_ids[i], float(D[0][idx])) for idx, i in enumerate(I[0])]
        return results

    def rag_search(self, query, top_k=5):
        # Step 1: Retrieve top product documents
        results = self.search(query, top_k=top_k)
        if not results:
            return "No relevant products found."
        # Step 2: Build context from retrieved products
        with self.engine.connect() as conn:
            product_ids = [str(pid) for pid, _ in results]
            sql = f"SELECT id, name, description FROM products WHERE id IN ({', '.join(product_ids)})"
            rows = conn.execute(text(sql)).fetchall()
            context = "\n".join([
                f"Name: {row[1]}\nDescription: {row[2]}" for row in rows
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
