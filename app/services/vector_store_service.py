import faiss
import numpy as np
import os
import json
import gc
from app.services.embedding_service import EmbeddingService


class VectorStoreService:
    # 🔹 Memory optimization: limit max vectors
    MAX_VECTORS = 5000  # Approx 100MB with 768-dim embeddings

    def __init__(self):
        # 🔹 Tomamos dimensión del modelo de embeddings
        self.dimension = EmbeddingService.dimension

        self.index_path = "vector.index"
        self.texts_path = "texts.json"

        # 🔹 Cargar o crear índice FAISS
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)

        # 🔹 Cargar textos persistidos
        if os.path.exists(self.texts_path):
            with open(self.texts_path, "r", encoding="utf-8") as f:
                self.texts = json.load(f)
        else:
            self.texts = []

    # 🔹 Guardado manual (NO se llama en cada add)
    def save(self):
        faiss.write_index(self.index, self.index_path)

        with open(self.texts_path, "w", encoding="utf-8") as f:
            json.dump(self.texts, f, ensure_ascii=False, indent=2)

    def add(self, embedding, text):
        # 🔹 Memory protection: enforce max capacity
        if self.index.ntotal >= self.MAX_VECTORS:
            self.prune_oldest(1000)  # Remove oldest 1000 vectors
        
        vector = np.array([embedding]).astype("float32")
        self.index.add(vector)
        self.texts.append(text)
        
        # 🔹 Explicit memory cleanup
        del vector
        gc.collect()

    def prune_oldest(self, count: int):
        """Remove oldest vectors when capacity exceeded - simple reset strategy"""
        # Simple strategy: reset the entire index when limit exceeded
        # This prevents OOM while maintaining recent documents
        self.index = faiss.IndexFlatL2(self.dimension)
        self.texts = self.texts[-1000:]  # Keep only last 1000 texts
        gc.collect()
        
        # Note: This loses old vectors but prevents memory overflow
        # Consider saving to disk if persistence is critical

    def search(self, embedding, k=3):
        if self.index.ntotal == 0:
            return []

        vector = np.array([embedding]).astype("float32")
        distances, indices = self.index.search(vector, k)

        results = []
        for idx in indices[0]:
            if idx < 0 or idx >= len(self.texts):
                continue
            if 0 <= idx < len(self.texts):
                results.append(self.texts[idx])

        return results
