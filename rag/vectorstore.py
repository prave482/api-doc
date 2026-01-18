from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class VectorStore:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000
        )
        self.texts = []
        self.metadata = []
        self.embeddings = None

    def add_chunks(self, chunks):
        self.texts.extend([chunk["text"] for chunk in chunks])
        self.metadata.extend([chunk["metadata"] for chunk in chunks])

        # Fit TF-IDF on all documents
        self.embeddings = self.vectorizer.fit_transform(self.texts)

    def retrieve(self, query, k=5):
        if self.embeddings is None:
            return []

        query_vec = self.vectorizer.transform([query])
        scores = (self.embeddings @ query_vec.T).toarray().flatten()

        top_indices = scores.argsort()[::-1][:k]

        results = []
        for idx in top_indices:
            results.append({
                "text": self.texts[idx],
                "metadata": self.metadata[idx]
            })

        return results
