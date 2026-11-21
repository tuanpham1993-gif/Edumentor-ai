"""Pipeline tìm kỹ năng theo tên → skill_id (module 09 · Tuấn · G1, 21/11/2026 — docs/Review-Skill-Search.md).

5.893 kỹ năng, nhiều tên trùng ("JavaScript" / "Javascript" / "JavaScript (Programming Language)"). Chỉ tìm bằng vector
thì sai với từ ngắn ("java" → ZOWE 0,90 — thử 17/11) → HYBRID: khớp nguyên văn + BM25 (chữ) + vector (nghĩa), gộp
bằng Reciprocal Rank Fusion, gom tên trùng, không tự chọn khi mơ hồ. Chạy trên runner kiểu n8n (trace từng khối):

  0 input → 1 normalize → 2 exact → 3 keyword (BM25) → 4 vector → 5 fuse (RRF) → 6 group → 7 decide → 8 trace
Chỉ ĐỌC tên kỹ năng (bảng skills của Hòa / Khôi), không sửa dữ liệu.
"""

import difflib
import re
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass, field

from app.ai.review.bm25 import BM25, tokenize
from app.ai.review.pipeline.runner import Node, Step, run_pipeline

MAX_QUERY = 100
CANDIDATES = 20  # mỗi nguồn lấy top 20
RRF_K = 60
CONFIDENT_COSINE = 0.85  # không khớp nguyên văn: chỉ "chắc chắn" khi vector rất gần …
CONFIDENT_MARGIN = 1.5  # … VÀ nhóm đứng đầu bỏ xa nhóm thứ hai (điểm RRF gấp ≥ 1,5 lần)
FUZZY_CUTOFF = 0.8  # độ giống tối thiểu để sửa lỗi gõ (difflib ratio)

_BRACKETS = re.compile(r"\([^)]*\)")
_NON_WORD = re.compile(r"[^0-9a-zà-ỹđ+#]+")


def normalize(name: str) -> str:
    """'JavaScript (Programming Language)' → 'javascript'. Chữ thường, NFC, bỏ phần trong ngoặc, bỏ ký tự thừa."""
    text = unicodedata.normalize("NFC", name or "").lower()
    text = _BRACKETS.sub(" ", text)
    return " ".join(_NON_WORD.sub(" ", text).split())


@dataclass
class SkillIndex:
    """Chỉ mục tìm kỹ năng, dựng một lần từ bảng skills (+ vector tên nếu có cache)."""

    ids: list[int]
    names: list[str]
    norms: list[str]
    bm25: BM25
    by_norm: dict[str, list[int]]  # tên chuẩn hóa → vị trí (các id trùng tên)
    vectors: object = None  # numpy (n, d) đã chuẩn hóa độ dài 1, hoặc None (chưa có cache / chưa có mô hình)

    @property
    def vocabulary(self) -> list[str]:
        if not hasattr(self, "_vocab"):
            self._vocab = sorted(self.bm25.idf)
        return self._vocab

    @classmethod
    def build(cls, rows: list[tuple[int, str]], vectors=None) -> "SkillIndex":
        ids = [r[0] for r in rows]
        names = [r[1] for r in rows]
        norms = [normalize(n) for n in names]
        by_norm: dict[str, list[int]] = {}
        for i, n in enumerate(norms):
            by_norm.setdefault(n, []).append(i)
        return cls(ids, names, norms, BM25([tokenize(n) for n in norms]), by_norm, vectors)


@dataclass
class SearchCtx:
    query: str
    index: SkillIndex
    limit: int = 5
    embed: Callable[[str], list[float] | None] | None = None  # None → bỏ khối vector
    counts: Callable[[list[int]], dict[int, tuple[int, int]]] = lambda ids: {}  # id → (câu đang bật, câu chờ duyệt)
    normalized: str = ""
    exact: list[int] = field(default_factory=list)
    keyword: list[tuple[int, float]] = field(default_factory=list)
    vector: list[tuple[int, float]] = field(default_factory=list)
    fused: list[tuple[int, float]] = field(default_factory=list)
    groups: list[dict] = field(default_factory=list)
    confident: bool = False
    results: list[dict] = field(default_factory=list)
    trace: list = field(default_factory=list)
    done: bool = False


def _input(ctx: SearchCtx):
    ctx.query = (ctx.query or "").strip()[:MAX_QUERY]
    if not ctx.query:
        ctx.done = True
    return Step(output={"query": ctx.query})


def _normalize(ctx: SearchCtx):
    ctx.normalized = normalize(ctx.query)
    if not ctx.normalized:
        ctx.done = True
    return Step(output={"normalized": ctx.normalized})


def _exact(ctx: SearchCtx):
    ctx.exact = list(ctx.index.by_norm.get(ctx.normalized, []))
    return Step(output={"hits": len(ctx.exact)})


def _keyword(ctx: SearchCtx):
    tokens, fixed = [], {}
    for t in tokenize(ctx.normalized):
        if t in ctx.index.bm25.idf or len(t) < 4:
            tokens.append(t)
            continue
        # Gõ sai chính tả ("pyhton") → từ gần nhất có trong tên kỹ năng (difflib, thư viện chuẩn)
        close = difflib.get_close_matches(t, ctx.index.vocabulary, n=1, cutoff=FUZZY_CUTOFF)
        tokens.append(close[0] if close else t)
        if close:
            fixed[t] = close[0]
    ctx.keyword = ctx.index.bm25.top(tokens, CANDIDATES)
    return Step(output={"top": [ctx.index.ids[i] for i, _ in ctx.keyword[:5]], "typo": fixed})


def _vector(ctx: SearchCtx):
    vectors = ctx.index.vectors
    if vectors is None or ctx.embed is None:
        return Step(output={"skipped": "chưa có vector / mô hình"})
    query_vec = ctx.embed(ctx.query)  # câu gốc (giữ dấu tiếng Việt) — mô hình đa ngôn ngữ
    if query_vec is None:
        return Step(output={"skipped": "không mã hóa được truy vấn"})
    import numpy as np

    scores = vectors @ np.asarray(query_vec, dtype=vectors.dtype)
    top = np.argsort(-scores)[:CANDIDATES]
    ctx.vector = [(int(i), float(scores[i])) for i in top if scores[i] > 0]  # không gần nghĩa chút nào → bỏ
    return Step(output={"top": [(ctx.index.ids[i], round(s, 3)) for i, s in ctx.vector[:5]]})


def _fuse(ctx: SearchCtx):
    """Reciprocal Rank Fusion: điểm = Σ 1 / (60 + hạng) qua các nguồn — không phải cân hai thang điểm khác nhau."""
    scores: dict[int, float] = {}
    for ranked in (ctx.exact, [i for i, _ in ctx.keyword], [i for i, _ in ctx.vector]):
        for rank, i in enumerate(ranked, start=1):
            scores[i] = scores.get(i, 0.0) + 1 / (RRF_K + rank)
    ctx.fused = sorted(scores.items(), key=lambda x: (-x[1], ctx.index.ids[x[0]]))
    return Step(output={"candidates": len(ctx.fused)})


def _group(ctx: SearchCtx):
    """Gom id trùng tên chuẩn hóa thành một nhóm; đại diện = id có NHIỀU câu đang bật nhất (bằng nhau → id nhỏ nhất)."""
    index = ctx.index
    order: list[str] = []
    best: dict[str, float] = {}
    for i, score in ctx.fused:
        norm = index.norms[i]
        if norm not in best:
            order.append(norm)
            best[norm] = score
    order = order[: max(ctx.limit * 2, 10)]
    members = {n: index.by_norm[n] for n in order}
    counts = ctx.counts([index.ids[i] for n in order for i in members[n]])
    keyword_pos = {i for i, _ in ctx.keyword}
    vector_cos = dict(ctx.vector)
    groups = []
    for n in order:
        pos = sorted(members[n], key=lambda i: (-counts.get(index.ids[i], (0, 0))[0], index.ids[i]))
        rep = pos[0]
        sources = []
        if n == ctx.normalized:
            sources.append("exact")
        if any(i in keyword_pos for i in pos):
            sources.append("keyword")
        if any(i in vector_cos for i in pos):
            sources.append("vector")
        active, pending = counts.get(index.ids[rep], (0, 0))
        groups.append(
            {
                "skill_id": index.ids[rep],
                "skill": index.names[rep],
                "score": round(best[n], 6),
                "match": "exact" if "exact" in sources else ("hybrid" if len(sources) > 1 else sources[0]),
                "cosine": round(max((vector_cos[i] for i in pos if i in vector_cos), default=0.0), 4),
                "aliases": [{"skill_id": index.ids[i], "skill": index.names[i]} for i in pos[1:]],
                "active_questions": active,
                "pending_questions": pending,
            }
        )
    ctx.groups = groups
    return Step(output={"groups": len(groups)})


def _decide(ctx: SearchCtx):
    """Chắc chắn khi khớp nguyên văn; hoặc vector rất gần VÀ bỏ xa nhóm thứ hai. Không thì trả top để người dùng chọn."""
    groups = ctx.groups
    if not groups:
        ctx.confident = False
    elif groups[0]["match"] == "exact":
        ctx.confident = True
    else:
        top = groups[0]
        margin_ok = len(groups) == 1 or top["score"] >= CONFIDENT_MARGIN * groups[1]["score"]
        ctx.confident = top["cosine"] >= CONFIDENT_COSINE and margin_ok
    ctx.results = groups[: ctx.limit]
    return Step(output={"confident": ctx.confident})


def _trace(ctx: SearchCtx):
    return Step(output={"top": [(g["skill_id"], g["match"], g["score"], g["cosine"]) for g in ctx.results]})


NODES = [
    Node("0_input", _input),
    Node("1_normalize", _normalize),
    Node("2_exact", _exact),
    Node("3_keyword", _keyword),
    Node("4_vector", _vector),
    Node("5_fuse", _fuse),
    Node("6_group", _group),
    Node("7_decide", _decide),
    Node("8_trace", _trace),
]


def run(ctx: SearchCtx) -> SearchCtx:
    return run_pipeline(NODES, ctx)
