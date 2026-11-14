"""Tiền xử lý văn bản tiếng Anh — KHỐI 1 của pipeline chấm tự luận (module 09 · Tuấn · B1, 14/11/2026).

Theo bài NLP pipeline của thầy (BA-nhom/pipeline/Session01/nlp-pipeline.py):
    tách từ → chuẩn hóa → bỏ stopwords → gán từ loại (POS) → đưa về dạng gốc (lemmatize)
nhưng sửa cho bài toán CHẤM BÀI (đã thử trên NLTK 3.10, xem docs/Review-AI-Grading.md B1):

  1. Giữ phủ định. Danh sách stopwords của NLTK có "not", "no", "nor" — bỏ đi thì
     "tuples cannot be changed" thành "tuple change": nghĩa bị đảo. NLTK còn tách
     "can't" → "ca" + "n't", "cannot" → "can" + "not" → đổi "n't" thành "not".
  2. Giữ vài từ đổi nghĩa câu ("only", "all", "both", "same", "but") dù nằm trong stopwords.
  3. Lemmatize THEO TỪ LOẠI (demo cố định pos='v' — "lists" là danh từ, không đưa về gốc được).
     Từ "-ing" / "-ed" bị gán nhầm danh từ / tính từ ("looping") → thử thêm dạng gốc động từ.
  4. Thuật ngữ lập trình WordNet không biết ("tuples") → tự bỏ đuôi số nhiều theo luật.
  5. Giữ ký hiệu lập trình ("[", "]", "(", ")", "=", "=="...) vì barem có ý "list dùng [ ]";
     bỏ dấu câu (". , : ; ! ?").

Dùng ở: chấm từ khóa tiếng Anh (B3), Verifier so câu trích (B8), phát hiện chép đề (B8).
Dữ liệu NLTK cần tải trước (một lần): punkt_tab, stopwords, wordnet, averaged_perceptron_tagger_eng
    python -m nltk.downloader punkt_tab stopwords wordnet averaged_perceptron_tagger_eng
Không tải lúc chạy server; thiếu dữ liệu → lỗi rõ ràng khi GỌI hàm (không làm hỏng lúc import).
"""

import re
import unicodedata
from functools import lru_cache

from nltk import pos_tag
from nltk.tokenize import word_tokenize

NEGATIONS = frozenset({"not", "no", "nor", "never", "none", "nothing", "neither", "nobody", "nowhere"})
# Có trong stopwords của NLTK nhưng làm đổi nghĩa câu khi chấm → giữ lại.
MEANINGFUL = frozenset({"only", "all", "both", "same", "but", "more", "most", "before", "after"})
# Ký hiệu lập trình được giữ; dấu câu khác bị bỏ.
CODE_SYMBOLS = frozenset(
    {"[", "]", "(", ")", "{", "}", "=", "==", "!=", "<", ">", "<=", ">=", "+", "-", "*", "/", "%", "+=", "-="}
)
# Dấu nháy cong (gõ từ Word / điện thoại) → nháy thẳng, để "can’t" tách giống "can't".
_QUOTES = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})
_SPACES = re.compile(r"\s+")


# ─────────────── dữ liệu NLTK (nạp lần đầu dùng) ───────────────


@lru_cache(maxsize=1)
def _stopwords() -> frozenset[str]:
    from nltk.corpus import stopwords

    return frozenset(stopwords.words("english")) - NEGATIONS - MEANINGFUL


@lru_cache(maxsize=1)
def _lemmatizer():
    from nltk.stem import WordNetLemmatizer

    return WordNetLemmatizer()


def _wordnet_pos(tag: str) -> str:
    """Nhãn POS của NLTK (Penn Treebank) → nhãn WordNet: J tính từ, V động từ, R trạng từ, còn lại danh từ."""
    return {"J": "a", "V": "v", "R": "r"}.get(tag[:1], "n")


# ─────────────── 5 bước ───────────────


def normalize(text: str) -> str:
    """NFC + nháy cong → nháy thẳng + chữ thường + gộp khoảng trắng."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text).translate(_QUOTES)
    return _SPACES.sub(" ", text).strip().lower()


def tokenize(text: str) -> list[str]:
    """Tách từ bằng word_tokenize; "n't" → "not"; giữ chữ / số và ký hiệu lập trình, bỏ dấu câu."""
    tokens = []
    for token in word_tokenize(text):
        if token == "n't":
            token = "not"
        if token.isalnum() or token in CODE_SYMBOLS or _is_word(token):
            tokens.append(token)
    return tokens


def remove_stopwords(tokens: list[str]) -> list[str]:
    """Bỏ stopwords tiếng Anh, NHƯNG giữ phủ định (NEGATIONS) và từ đổi nghĩa (MEANINGFUL)."""
    stop = _stopwords()
    return [t for t in tokens if t not in stop]


def lemmatize(tokens: list[str]) -> list[str]:
    """Đưa về dạng gốc THEO TỪ LOẠI. Ký hiệu, số giữ nguyên; danh từ WordNet không biết → bỏ đuôi số nhiều."""
    lemmatizer = _lemmatizer()
    out = []
    for token, tag in pos_tag(tokens):
        if not token.isalpha():
            out.append(token)
            continue
        pos = _wordnet_pos(tag)
        lemma = lemmatizer.lemmatize(token, pos)
        if lemma == token and pos in ("n", "a") and token.endswith(("ing", "ed")):
            # Bộ gán từ loại hay coi "looping", "modified" là danh từ / tính từ → thử dạng gốc động từ.
            lemma = lemmatizer.lemmatize(token, "v")
        if lemma == token and pos == "n":
            lemma = _strip_plural(token)
        out.append(lemma)
    return out


def preprocess(text: str) -> list[str]:
    """Nối 4 bước — hàm các khối khác gọi. Bài trống → []."""
    tokens = tokenize(normalize(text))
    return lemmatize(remove_stopwords(tokens)) if tokens else []


# ─────────────── nội bộ ───────────────


def _is_word(token: str) -> bool:
    """Từ có gạch nối / gạch dưới như "read-only", "my_list" (isalnum() trả False)."""
    return bool(re.fullmatch(r"[a-z0-9]+(?:[-_][a-z0-9]+)+", token))


def _strip_plural(word: str) -> str:
    """Bỏ đuôi số nhiều cho từ WordNet không biết (thuật ngữ lập trình): tuples → tuple, classes → class,
    dictionaries → dictionary. Không đụng từ ngắn hoặc tận cùng "ss" / "us" / "is" (class, status, this)."""
    from nltk.corpus import wordnet

    if wordnet.synsets(word) or len(word) <= 3 or word.endswith(("ss", "us", "is")):
        return word
    if word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith(("sses", "xes", "zes", "ches", "shes")):
        return word[:-2]
    if word.endswith("s"):
        return word[:-1]
    return word
