import os
import json
import faiss
from sentence_transformers import SentenceTransformer

class VectorStore:
    def __init__(self, vector_store_path, embedding_model_name):
        self.vector_store_path = vector_store_path
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.vector_dim = self.embedding_model.get_sentence_embedding_dimension()
        self.vector_index = None
        self.vector_ids = []
        self.vector_texts = []
        self._load_or_init()
        
    def _load_or_init(self):
        if os.path.exists(f"{self.vector_store_path}.faiss") and os.path.exists(f"{self.vector_store_path}.json"):
            self.vector_index = faiss.read_index(f"{self.vector_store_path}.faiss")
            with open(f"{self.vector_store_path}.json", 'r') as f:
                vector_data = json.load(f)
                self.vector_ids = vector_data["ids"]
                self.vector_texts = vector_data["texts"]
        else:
            self.vector_index = faiss.IndexFlatL2(self.vector_dim)
            self.vector_ids = []
            self.vector_texts = []
        
    def save(self):
        os.makedirs(os.path.dirname(self.vector_store_path), exist_ok=True)
        faiss.write_index(self.vector_index, f"{self.vector_store_path}.faiss")
        with open(f"{self.vector_store_path}.json", 'w') as f:
            json.dump({"ids": self.vector_ids, "texts": self.vector_texts}, f)
        
    def add(self, chat_id, text):
        embedding = self.embedding_model.encode([text])[0]
        embedding = embedding.reshape(1, -1).astype('float32')
        self.vector_index.add(embedding)
        self.vector_ids.append(chat_id)
        self.vector_texts.append(text)
        self.save()
        
    def search(self, query, top_k=5):
        if self.vector_index.ntotal == 0:
            return []
        query_embedding = self.embedding_model.encode([query])[0]
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        distances, indices = self.vector_index.search(query_embedding, min(top_k, self.vector_index.ntotal))
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.vector_ids) and idx >= 0:
                chat_id = self.vector_ids[idx]
                text = self.vector_texts[idx]
                distance = distances[0][i]
                results.append((chat_id, text, distance))
        return results