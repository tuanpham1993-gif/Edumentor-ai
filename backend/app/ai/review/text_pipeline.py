"""Tiền xử lý văn bản tiếng Anh — KHỐI 1 của pipeline chấm tự luận (module 09 · Tuấn · B1, 14/11/2026).

Theo bài NLP pipeline của thầy (BA-nhom/pipeline/Session01/nlp-pipeline.py):
    tách từ → chuẩn hóa → bỏ stopwords → gán từ loại (POS) → đưa về dạng gốc (lemmatize)
nhưng sửa cho bài toán CHẤM BÀI (đã thử trên NLTK 3.10, xem docs/Review-AI-Grading.md B1):

  1. Giữ phủ định. Danh sách stopwords của NLTK có "not", "no", "nor" — bỏ đi thì
     "tuples cannot be changed" thành "tuple change": nghĩa bị đảo. NLTK còn tách
     "can't" → "ca" + "n't", "cannot" → "can" + "not" → đổi "n't" thành "not".
  2. Giữ vài từ đổi nghĩa câu ("only", "all", "both", "same", "but", "again") dù nằm trong stopwords.
     Giữ TỪ KHÓA PYTHON (for, while, if, in, is, and, or...) — stopwords NLTK có chúng (sửa 14/11 khi làm B3).
  3. Lemmatize THEO TỪ LOẠI (demo cố định pos='v' — "lists" là danh từ, không đưa về gốc được).
     Từ "-ing" / "-ed" bị gán nhầm danh từ / tính từ ("looping") → thử thêm dạng gốc động từ.
  4. Thuật ngữ lập trình WordNet không biết ("tuples") → tự bỏ đuôi số nhiều theo luật.
  5. Giữ ký hiệu lập trình ("[", "]", "(", ")", "=", "==", "//", "!="...) vì barem có ý "list dùng [ ]";
     ghép toán tử NLTK tách đôi ("!" "=" → "!="); giữ số thập phân ("3.5"); bỏ dấu câu (". , : ; ! ?").
     Tên biến "a", "i" (trùng stopword) giữ lại khi đứng cạnh ký hiệu ("a = 7", "total + i") — sửa 14/11 khi duyệt B2.

Dùng ở: chấm từ khóa tiếng Anh (B3), Verifier so câu trích (B8), phát hiện chép đề (B8).
Dữ liệu NLTK cần tải trước (một lần): punkt_tab, stopwords, wordnet, averaged_perceptron_tagger_eng
    python -m nltk.downloader punkt_tab stopwords wordnet averaged_perceptron_tagger_eng
Không tải lúc chạy server; thiếu dữ liệu → lỗi rõ ràng khi GỌI hàm (không làm hỏng lúc import).
"""

import keyword
import re
import unicodedata
from functools import lru_cache

from nltk import pos_tag
from nltk.tokenize import word_tokenize

NEGATIONS = frozenset({"not", "no", "nor", "never", "none", "nothing", "neither", "nobody", "nowhere"})
# Từ khóa Python (for, while, if, in, is, and, or, ...) — stopwords của NLTK có nhiều từ này; bỏ đi thì
# "while loop" chỉ còn "loop" → không phân biệt được for / while. Giữ nguyên, KHÔNG lemmatize ("is" giữ là "is").
PYTHON_KEYWORDS = frozenset(k.lower() for k in keyword.kwlist)
# Có trong stopwords của NLTK nhưng làm đổi nghĩa câu khi chấm → giữ lại.
MEANINGFUL = frozenset({"only", "all", "both", "same", "but", "more", "most", "before", "after", "again"})
# Ký hiệu lập trình được giữ; dấu câu khác bị bỏ.
CODE_SYMBOLS = frozenset(
    {"[", "]", "(", ")", "{", "}", "=", "==", "!=", "<", ">", "<=", ">=", "+", "-", "*", "/", "%", "+=", "-="}
    | {"//", "**", "*=", "/=", "%=", "//=", "**="}
)
# word_tokenize tách "!=" → "!" "=", "**" → "*" "*", "<=" → "<" "=" — ghép lại (bỏ "!" thì "!=" thành "=": sai nghĩa).
_JOINABLE = frozenset({"!", "<", ">", "=", "+", "-", "*", "/", "%", "//", "**"})
_NUMBER = re.compile(r"\d+\.\d+")  # số thập phân "3.5" (isalnum() trả False)
# Tách ký hiệu toán tử khỏi chữ / số trước word_tokenize: NLTK coi "n+1", "x+=1", "tong=0" là MỘT từ rồi bị bỏ.
# Không đụng "-" giữa hai chữ ("read-only") và "." (số thập phân, "a.append").
_OPERATOR_CHARS = re.compile(r"([+*/%=<>!()\[\]{}]|(?<![a-z])-|-(?![a-z]))")
# Dấu nháy cong (gõ từ Word / điện thoại) → nháy thẳng, để "can’t" tách giống "can't".
_QUOTES = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})
_SPACES = re.compile(r"\s+")
# "a is 7": mạo từ "a" không đứng trước các động từ này → "a" là tên biến (xem _is_code_variable).
_VALUE_VERBS = frozenset({"is", "becomes", "equals"})


# ─────────────── dữ liệu NLTK (nạp lần đầu dùng) ───────────────


@lru_cache(maxsize=1)
def _stopwords() -> frozenset[str]:
    from nltk.corpus import stopwords

    return frozenset(stopwords.words("english")) - NEGATIONS - MEANINGFUL - PYTHON_KEYWORDS


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
    """Tách từ bằng word_tokenize; "n't" → "not"; ghép lại toán tử bị tách ("!" "=" → "!="); giữ chữ, số
    (cả số thập phân "3.5") và ký hiệu lập trình, bỏ dấu câu."""
    tokens = []
    for token in _merge_operators(word_tokenize(_OPERATOR_CHARS.sub(r" \1 ", text))):
        if token == "n't":
            token = "not"
        if token.isalnum() or token in CODE_SYMBOLS or _NUMBER.fullmatch(token) or _is_word(token):
            tokens.append(token)
    return tokens


def remove_stopwords(tokens: list[str]) -> list[str]:
    """Bỏ stopwords tiếng Anh, NHƯNG giữ phủ định (NEGATIONS) và từ đổi nghĩa (MEANINGFUL).

    Tên biến một chữ cái trùng stopword ("a", "i") được giữ khi đứng gần ký hiệu lập trình (cách ≤ 2 từ):
    "a = 7" không được thành "= 7" (khớp nhầm "b = 7"), "total + i" không thành "total +"."""
    stop = _stopwords()
    return [t for i, t in enumerate(tokens) if t not in stop or _is_code_variable(tokens, i)]


def lemmatize(tokens: list[str]) -> list[str]:
    """Đưa về dạng gốc THEO TỪ LOẠI. Ký hiệu, số giữ nguyên; danh từ WordNet không biết → bỏ đuôi số nhiều."""
    lemmatizer = _lemmatizer()
    out = []
    for token, tag in pos_tag(tokens):
        if not token.isalpha() or token in PYTHON_KEYWORDS:
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


def _is_code_variable(tokens: list[str], i: int) -> bool:
    """Từ một chữ cái là tên biến khi: có ký hiệu lập trình trong phạm vi 2 từ hai bên ("a, b = b, a"), hoặc
    đứng ngay trước "is" / "becomes" / "equals" ("a is 7" — mạo từ "a" không bao giờ đứng trước động từ)."""
    if len(tokens[i]) != 1 or not tokens[i].isalpha():
        return False
    if i + 1 < len(tokens) and tokens[i + 1] in _VALUE_VERBS:
        return True
    return any(t in CODE_SYMBOLS for t in tokens[max(0, i - 2) : i + 3])


def _merge_operators(tokens: list[str]) -> list[str]:
    """Ghép toán tử bị word_tokenize tách đôi khi ghép lại ra một toán tử Python hợp lệ ("!" + "=" → "!=")."""
    out: list[str] = []
    for token in tokens:
        if out and out[-1] in _JOINABLE and out[-1] + token in CODE_SYMBOLS:
            out[-1] += token
        else:
            out.append(token)
    return out


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
