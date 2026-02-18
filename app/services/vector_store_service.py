import faiss
import numpy as np
import os
import json
from app.services.embedding_service import EmbeddingService


class VectorStoreService:

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
        vector = np.array([embedding]).astype("float32")
        self.index.add(vector)
        self.texts.append(text)

    def search(self, embedding, k=3):
        if self.index.ntotal == 0:
            return []

        vector = np.array([embedding]).astype("float32")
        distances, indices = self.index.search(vector, k)

        results = []
        for idx in indices[0]:
            if 0 <= idx < len(self.texts):
                results.append(self.texts[idx])

        return results
