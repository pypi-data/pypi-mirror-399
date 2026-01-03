from typing import List, Dict
from prlyn.models import (
    RedundancyScore,
    RedundancyCluster,
    ClassifiedSentence,
    SentenceLabel,
)
from sklearn.cluster import AgglomerativeClustering
from sentence_transformers import SentenceTransformer
import numpy as np


class RedundancyAnalyzer:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        # Threshold 0.70 distance roughly lower bound for similarity > 0.75
        self.threshold = 0.70

    def analyze(self, sentences: List[ClassifiedSentence]) -> RedundancyScore:
        clusters_found = []
        redundancy_count = 0

        # Group by label
        grouped: Dict[SentenceLabel, List[int]] = {}
        for idx, s in enumerate(sentences):
            # Only check Instructions, Constraints, Format
            if s.primary_label not in {
                SentenceLabel.INSTRUCTION,
                SentenceLabel.CONSTRAINT,
                SentenceLabel.FORMAT_SPEC,
            }:
                continue

            # Simple short sentence filter (< 5 words/tokens to avoid clustering "See below")
            # Using token count from struct
            if s.tokens < 5:
                continue

            line_length = s.primary_label
            if line_length not in grouped:
                grouped[line_length] = []
            grouped[line_length].append(idx)

        for line_length, indices in grouped.items():
            if len(indices) < 2:
                continue

            texts = [sentences[i].text for i in indices]
            embeddings = self.model.encode(texts)
            # Normalize for cosine similarity behavior with Euclidean distance
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

            # Agglomerative Clustering
            # distance_threshold: The linkage distance threshold above which, clusters will not be merged.
            clustering = AgglomerativeClustering(
                n_clusters=None,
                distance_threshold=self.threshold,
                metric="euclidean",  # For normalized vectors, euclidean is monotonic with cosine distance
                linkage="average",
            )
            clustering.fit(embeddings)

            # Group by cluster ID
            cluster_map: Dict[int, List[int]] = {}
            for idx, cluster_id in enumerate(clustering.labels_):
                if cluster_id not in cluster_map:
                    cluster_map[cluster_id] = []
                cluster_map[cluster_id].append(indices[idx])

            # Filter for actual clusters (size > 1)
            for cid, idxs in cluster_map.items():
                if len(idxs) > 1:
                    redundancy_count += len(idxs) - 1
                    # Pick shortest as representative? Or first?
                    # Let's pick the one with most tokens (detail) or first.
                    # Requirement says "Representative". Let's pick the first.
                    rep_text = sentences[idxs[0]].text

                    clusters_found.append(
                        RedundancyCluster(
                            label=line_length,
                            sentence_indices=idxs,
                            representative_text=rep_text,
                        )
                    )

        return RedundancyScore(
            clusters=clusters_found, redundancy_count=redundancy_count
        )

    def get_jaccard_similarity(self, str1: str, str2: str) -> float:
        a = set(str1.lower().split())
        b = set(str2.lower().split())
        c = a.intersection(b)
        return float(len(c)) / (len(a) + len(b) - len(c))
