"""
Airgapped On-Device Vector Embedding Engine for MRPL Sovereign AI Workbench.
Runs 100% locally with zero external API calls or outbound network sockets.
"""

import math
import re
from typing import List, Union

class LocalEmbeddings:
    """
    On-premise dense vector embedding engine.
    Computes deterministic semantic dense embeddings (dim=384) with subword hash pooling,
    n-gram lexical features, and L2 unit-norm projection.
    
    Compatible with standard cosine similarity search without requiring cloud models or torch downloads.
    """
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self._cache = {}

    def _tokenize(self, text: str) -> List[str]:
        # Clean text, extract lowercase word tokens and domain technical terms (e.g. cru-c-101, 7.82mm, api-510)
        cleaned = re.sub(r'[^\w\s\-\.]', ' ', text.lower())
        tokens = [t.strip('.-') for t in cleaned.split() if len(t.strip('.-')) > 1]
        return tokens

    def _hash_token(self, token: str, seed: int) -> int:
        h = seed
        for char in token:
            h = ((h << 5) - h + ord(char)) & 0xFFFFFFFF
        return h

    def embed_text(self, text: str) -> List[float]:
        """Compute 384-dimensional dense vector representation for a text string."""
        if not text or not text.strip():
            return [0.0] * self.dimension

        cached = self._cache.get(text)
        if cached:
            return cached

        tokens = self._tokenize(text)
        if not tokens:
            return [0.0] * self.dimension

        vector = [0.0] * self.dimension

        # Generate dense representations using multi-hash subword & character n-grams
        for i, token in enumerate(tokens):
            # Positional decay weighting
            pos_weight = 1.0 / (1.0 + 0.05 * math.log1p(i))

            # Domain keyword amplification (refinery, thickness, corrosion, api, sop, pressure, etc.)
            domain_weight = 1.0
            if any(k in token for k in ['cru', 'c-101', 'thickness', 'corrosion', 'asme', '510', '402', 'retirement', 'vul', 'bar', 'temperature', 'lethal', 'quench', 'pump', 'vibration', 'flange', 'permit']):
                domain_weight = 1.8

            token_weight = pos_weight * domain_weight

            # 3 independent hash projections into vector space
            for seed in [131, 1313, 13131]:
                h = self._hash_token(token, seed)
                idx = h % self.dimension
                sign = 1.0 if ((h >> 16) & 1) == 0 else -1.0
                vector[idx] += sign * token_weight

            # Character n-grams (tri-grams) for robust morphological matching
            if len(token) >= 3:
                for j in range(len(token) - 2):
                    ngram = token[j:j+3]
                    h_ng = self._hash_token(ngram, 5381)
                    idx_ng = h_ng % self.dimension
                    sign_ng = 1.0 if ((h_ng >> 12) & 1) == 0 else -1.0
                    vector[idx_ng] += sign_ng * 0.4 * token_weight

        # L2 Normalization (unit norm projection for cosine similarity)
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0.0:
            vector = [v / norm for v in vector]

        if len(self._cache) < 2000:
            self._cache[text] = vector

        return vector

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Compute embeddings for a batch of texts."""
        return [self.embed_text(t) for t in texts]

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """Compute cosine similarity between two unit vectors."""
        if len(vec_a) != len(vec_b):
            raise ValueError(f"Vector dimensions mismatch: {len(vec_a)} vs {len(vec_b)}")
        # If both are L2 normalized, dot product equals cosine similarity
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        # Ensure clamped between -1.0 and 1.0
        return max(-1.0, min(1.0, dot))
