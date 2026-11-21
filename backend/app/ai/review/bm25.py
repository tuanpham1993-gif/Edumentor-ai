"""BM25 nhỏ cho tên kỹ năng ngắn (module 09 · Tuấn · G1, 21/11/2026 — docs/Review-Skill-Search.md mục 4).

Tìm theo CHỮ: bắt được các ca tìm theo nghĩa (vector) bỏ lỡ với từ rất ngắn ("java", "if"). Không thêm thư viện.
    index = BM25([["java"], ["java", "ee"], ["javascript"]])
    index.top(["java"], 20) -> [(0, 1.23), (1, 0.98)]      # (vị trí tài liệu, điểm), điểm > 0, cao trước
"""

import math
import re
from collections import Counter

TOKEN = re.compile(r"[0-9a-zà-ỹđ+#]+")


def tokenize(text: str) -> list[str]:
    """Chữ thường, tách theo ký tự không phải chữ / số (giữ + và # cho "c++", "c#")."""
    return TOKEN.findall(text.lower())


class BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.docs = [Counter(d) for d in docs]
        self.lengths = [len(d) for d in docs]
        self.avg_len = (sum(self.lengths) / len(docs)) if docs else 0.0
        df: Counter = Counter()
        for d in self.docs:
            df.update(d.keys())
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}
        self.postings: dict[str, list[int]] = {}
        for i, d in enumerate(self.docs):
            for t in d:
                self.postings.setdefault(t, []).append(i)

    def top(self, query: list[str], k: int = 20) -> list[tuple[int, float]]:
        scores: dict[int, float] = {}
        for t in set(query):
            idf = self.idf.get(t)
            if idf is None:
                continue
            for i in self.postings[t]:
                tf = self.docs[i][t]
                norm = 1 - self.b + self.b * self.lengths[i] / self.avg_len
                scores[i] = scores.get(i, 0.0) + idf * tf * (self.k1 + 1) / (tf + self.k1 * norm)
        return sorted(scores.items(), key=lambda x: (-x[1], x[0]))[:k]
