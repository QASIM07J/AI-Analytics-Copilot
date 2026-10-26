"""
Schema Vector RAG (Retrieval-Augmented Generation) Engine.

Indexes database schema metadata, business metrics, and golden SQL benchmarks.
Uses dense vector embeddings (FastEmbed / ONNX) to semantically retrieve the most
relevant columns, business definitions, and few-shot SQL examples for user queries.
"""

import os
import json
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from fastembed import TextEmbedding


class SchemaRetriever:
    """
    In-memory Vector RAG retriever for database schema and SQL few-shot examples.
    """

    def __init__(
        self,
        schema_path: str = os.path.join("data", "schema_metadata.json"),
        benchmarks_path: str = os.path.join("data", "golden_benchmarks.json"),
    ):
        self.schema_path = schema_path
        self.benchmarks_path = benchmarks_path
        self.embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

        self.documents: List[Dict[str, Any]] = []
        self.doc_embeddings: Optional[np.ndarray] = None
        self._build_index()

    def _build_index(self) -> None:
        """Loads metadata and benchmarks, creates text chunks, and computes dense embeddings."""
        docs = []

        # 1. Index Schema Columns
        if os.path.exists(self.schema_path):
            with open(self.schema_path, "r", encoding="utf-8") as f:
                schema_data = json.load(f)

            for col in schema_data.get("columns", []):
                text = f"Column: {col['name']} ({col['type']}). Description: {col['description']}"
                docs.append({
                    "type": "column",
                    "title": col["name"],
                    "text": text,
                    "payload": col,
                })

            for metric in schema_data.get("business_metrics", []):
                text = f"Business Metric: {metric['metric']}. Formula: {metric['formula']}. Description: {metric['description']}"
                docs.append({
                    "type": "metric",
                    "title": metric["metric"],
                    "text": text,
                    "payload": metric,
                })

        # 2. Index Few-Shot Golden Benchmarks
        if os.path.exists(self.benchmarks_path):
            with open(self.benchmarks_path, "r", encoding="utf-8") as f:
                benchmarks = json.load(f)

            for bm in benchmarks:
                text = f"Question: {bm['question']} | Verified SQL: {bm['sql']}"
                docs.append({
                    "type": "example",
                    "title": bm["category"],
                    "text": text,
                    "payload": bm,
                })

        self.documents = docs

        # Compute embeddings for all documents
        doc_texts = [d["text"] for d in docs]
        embeddings = list(self.embedding_model.embed(doc_texts))
        self.doc_embeddings = np.array(embeddings, dtype=np.float32)

        # Normalize embeddings for cosine similarity
        norms = np.linalg.norm(self.doc_embeddings, axis=1, keepdims=True)
        self.doc_embeddings = self.doc_embeddings / np.maximum(norms, 1e-9)

    def retrieve(self, query: str, top_k_schema: int = 5, top_k_examples: int = 2) -> Dict[str, List[Dict[str, Any]]]:
        """
        Performs semantic vector search across schema definitions and few-shot examples.
        """
        query_emb = list(self.embedding_model.embed([query]))[0]
        query_vec = np.array(query_emb, dtype=np.float32)
        query_norm = np.linalg.norm(query_vec)
        if query_norm > 0:
            query_vec = query_vec / query_norm

        # Compute cosine similarities
        scores = np.dot(self.doc_embeddings, query_vec)

        schema_results = []
        example_results = []

        # Sort indices by descending score
        ranked_indices = np.argsort(scores)[::-1]

        for idx in ranked_indices:
            doc = self.documents[idx]
            score = float(scores[idx])

            if doc["type"] in ("column", "metric") and len(schema_results) < top_k_schema:
                schema_results.append({**doc, "score": score})
            elif doc["type"] == "example" and len(example_results) < top_k_examples:
                example_results.append({**doc, "score": score})

            if len(schema_results) >= top_k_schema and len(example_results) >= top_k_examples:
                break

        return {
            "schema_context": schema_results,
            "few_shot_examples": example_results,
        }

    def format_augmented_context(self, query: str) -> str:
        """
        Builds a rich, dynamic context string to inject into the LLM system prompt.
        """
        retrieved = self.retrieve(query)

        lines = ["\n### Dynamically Retrieved Schema & Context:"]
        for item in retrieved["schema_context"]:
            lines.append(f"- {item['text']}")

        if retrieved["few_shot_examples"]:
            lines.append("\n### Relevant Few-Shot SQL Examples:")
            for ex in retrieved["few_shot_examples"]:
                bm = ex["payload"]
                lines.append(f"Question: {bm['question']}")
                lines.append(f"SQL: {bm['sql']}\n")

        return "\n".join(lines)


# Global singleton instance
_retriever_instance: Optional[SchemaRetriever] = None


def get_schema_retriever() -> SchemaRetriever:
    """Returns or initializes the singleton SchemaRetriever."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = SchemaRetriever()
    return _retriever_instance
