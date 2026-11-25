"""G3b — AI soạn câu ôn theo kỹ năng: khung, đoạn nguồn, câu trích, chống trùng, soạn lại kèm lỗi (Tuấn · 25/11/2026).

AI giả (không gọi mạng). Docs: docs/Review-AI-Tu-Soan-On-Tap.md mục 7.3.
Chạy:  python -m pytest tests/test_question_gen.py -v
"""

import pytest

from app.ai.prompts.review_generate import GEN_PROMPT_VERSION, build_question_prompt
from app.ai.review.grading_schema import AIOutputError
from app.ai.review.question_schema import GEMINI_QUESTION_SCHEMAS, check_questions
from app.models import KnowledgeChunk, ReviewQuestion, ReviewSkillScope, Skills
from app.services import question_gen_service as gen

SKILL = 80
P1 = "Docker images are read-only templates. A container is a running instance of an image with a writable layer."
P2 = "A Dockerfile begins with a FROM instruction that names the base image. RUN, COPY and ADD create new layers."
PASSAGES = [P1, P2]


STEMS = [
    "Which instruction sets the base image?",
    "How many layers does a RUN line add to an image?",
    "What does the build cache reuse between builds?",
    "Where is the writable layer of a running container stored?",
    "Which keyword documents the port an app listens on?",
    "What starts when you launch a container from this image?",
    "Which folder becomes the default for later instructions after WORKDIR?",
    "Why are images described as read-only templates?",
    "What is lost when a container without a volume is deleted?",
    "Which command copies local files into the image during a build?",
    "Predict the output of listing containers right after a stop.",
    "What does tagging an image change about its content?",
]


def mcq(level="recognize", n=0, *, passage=2, quote="a dockerfile begins with a from instruction", options=None):
    stem = STEMS[(n + (6 if level == "understand" else 0)) % len(STEMS)]
    return {"level": level, "passage": passage, "content": stem,
            "options": options or ["FROM", "BASE", "IMAGE", "RUN"], "correct_index": 0,
            "explanation": "FROM names the base image.", "source_quote": quote}  # fmt: skip


ESSAYS = {
    ("easy", 1): "Explain how an image differs from a container.",
    ("easy", 2): "Describe why a volume keeps database files safe.",
    ("advanced", 1): "Design a small Dockerfile for a web app and justify each layer.",
}


# (từ khóa từng ý, bài mẫu) — bài mẫu chứa đủ từ khóa (cổng G3c: bài mẫu ≥ 7/10), đề không chứa từ khóa (L7)
ESSAY_KEYS = {
    ("easy", 1): ([["read-only", "template"], ["running", "instance"]],
                  "An image is a read-only template. A container is a running instance of it."),
    ("easy", 2): ([["persist", "data"], ["removed", "survive"]],
                  "A volume lets data persist outside the container. The files survive when it is removed."),
    ("advanced", 1): ([["base", "python"], ["install", "requirements"], ["copy", "source"], ["start", "command"]],
                      "Use a python base. Install the requirements first. Then copy the source. Set the start command."),
}  # fmt: skip


def essay(level="easy", n=1):
    keys, answer = ESSAY_KEYS[(level, n)]
    points = [10 // len(keys) + (10 % len(keys) if i == 0 else 0) for i in range(len(keys))]
    rubric = [{"text": " ".join(k), "max_points": p, "main_keywords": k, "sub_keywords": []}
              for k, p in zip(keys, points, strict=True)]  # fmt: skip
    return {"level": level, "passage": 1, "content": ESSAYS[(level, n)], "rubric": rubric,
            "explanation": f"Model answer: {answer}", "source_quote": "A container is a running instance of an image"}  # fmt: skip


# ─────────────── check_questions ───────────────


def test_valid_mcq_passes():
    good, errors = check_questions({"questions": [mcq()]}, "mcq", {"recognize": 1}, passages=PASSAGES)
    assert errors == [] and good[0]["passage"] == 2 and good[0]["type"] == "mcq"


@pytest.mark.parametrize(
    ("question", "message"),
    [
        (mcq(quote="docker is the best tool for everything"), "not copied exactly"),
        (mcq(quote="from instruction"), "at least"),
        (mcq(passage=5), "passage must be"),
        (mcq(options=["FROM", "RUN", "All of the above", "COPY"]), "All / None"),
        (mcq(options=["FROM", "FROM", "RUN", "COPY"]), "trùng"),
        (mcq(level="easy"), "not requested"),
    ],
)
def test_bad_mcq_rejected(question, message):
    good, errors = check_questions({"questions": [question]}, "mcq", {"recognize": 1, "easy": 0}, passages=PASSAGES)
    assert good == [] and any(message in e for e in errors), errors


def test_quote_ignores_case_and_punctuation():
    q = mcq(quote="A Dockerfile begins with a FROM instruction, that names the base image!")
    assert check_questions({"questions": [q]}, "mcq", {"recognize": 1}, passages=PASSAGES)[1] == []


def test_duplicates_rejected_and_extras_dropped():
    existing = [mcq(n=1)["content"]]
    data = {"questions": [mcq(n=1), mcq(n=2), mcq(n=3)]}
    good, errors = check_questions(data, "mcq", {"recognize": 1}, passages=PASSAGES, existing=existing)
    assert len(good) == 1 and "repeats" in errors[0]  # câu 1 trùng; câu 2 nhận; câu 3 dư → bỏ, không báo lỗi
    assert len(errors) == 1


def test_essay_rubric_checked():
    bad = essay()
    bad["rubric"][0]["max_points"] = 1  # tổng ≠ 10
    good, errors = check_questions({"questions": [bad, essay("advanced")]}, "essay", {"easy": 1, "advanced": 1},
                                   passages=PASSAGES)  # fmt: skip
    assert [q["level"] for q in good] == ["advanced"] and "missing: 1 easy" in errors[-1]


def test_essay_l7_keywords_in_question_rejected():
    leaky = essay()
    leaky["content"] = "Describe the base image and the working directory of a Dockerfile."
    leaky["rubric"][0]["main_keywords"] = ["base image"]  # cả từ khóa của ý 1 nằm sẵn trong đề
    leaky["rubric"][1]["main_keywords"] = ["working directory", "WORKDIR"]  # thiếu "WORKDIR" trong đề → không lộ
    good, errors = check_questions({"questions": [leaky]}, "essay", {"easy": 1}, passages=PASSAGES)
    assert good == [] and "rubric item(s) [1]" in errors[0]


def test_leaked_items_matches_whole_words():
    from app.ai.review.question_schema import leaked_items

    rubric = [{"main_keywords": ["run"]}, {"main_keywords": ["not change", "layer"]}]
    assert leaked_items("Why does running twice not change the layer?", rubric) == [2]  # "running" ≠ "run"


def test_schema_mismatch():
    assert check_questions({"items": []}, "mcq", {"recognize": 1}, passages=PASSAGES)[1][0].startswith("answer did")


def test_gemini_schemas_and_prompt():
    assert GEMINI_QUESTION_SCHEMAS["mcq"]["properties"]["questions"]["items"]["properties"]["level"]["enum"] == [
        "recognize", "understand"]  # fmt: skip
    prompt = build_question_prompt("Docker", [{"title": "T", "content": P1}], {"recognize": 6}, ["Old?"], ["bad"])
    assert "[Passage 1] T" in prompt and "- Old?" in prompt and "6 multiple-choice, RECOGNIZE" in prompt
    assert "REJECTED BECAUSE:\n- bad" in prompt


# ─────────────── generate ───────────────


@pytest.fixture()
def gdb(db_session):
    db = db_session
    db.add(Skills(skill_id=SKILL, skill="Docker", is_active=True))
    db.flush()
    db.add(ReviewSkillScope(skill_id=SKILL, label="open", category="infra_security", source="admin"))
    db.add_all([KnowledgeChunk(chunk_id=11, skill_id=SKILL, title="Images", content=P1),
                KnowledgeChunk(chunk_id=12, skill_id=SKILL, title="Dockerfile", content=P2)])  # fmt: skip
    db.add(ReviewQuestion(skill_id=SKILL, type="mcq", level="recognize", content="Old question about volumes?",
                          options=["a", "b", "c", "d"], correct_index=0))  # fmt: skip
    db.commit()
    return db


class FakeAI:
    """Trả lần lượt các kết quả đã soạn sẵn theo kind; ghi lại tham số mỗi lần gọi."""

    def __init__(self, answers: dict[str, list]):
        self.answers = {k: list(v) for k, v in answers.items()}
        self.calls = []

    def __call__(self, skill, passages, kind, need, existing, feedback):
        self.calls.append({"kind": kind, "need": dict(need), "existing": list(existing), "feedback": list(feedback)})
        answer = self.answers[kind].pop(0) if self.answers.get(kind) else {"questions": []}  # hết → AI không soạn được
        if isinstance(answer, Exception):
            raise answer
        return answer


def test_generate_full_exam_two_calls(gdb):
    ai = FakeAI({"mcq": [{"questions": [mcq("recognize", i) for i in range(6)] +
                                       [mcq("understand", i) for i in range(6)]}],
                 "essay": [{"questions": [essay("easy", 1), essay("easy", 2), essay("advanced")]}]})  # fmt: skip
    out = gen.generate(gdb, SKILL, write=ai, model="gemini-x")
    assert len(out["questions"]) == 15 and out["calls"] == 2 and out["missing"] == {}
    assert {q["chunk_id"] for q in out["questions"] if q["type"] == "mcq"} == {12}  # passage 2 → chunk 12
    assert {q["chunk_id"] for q in out["questions"] if q["type"] == "essay"} == {11}
    gen_info = out["questions"][0]["ai_check"]["gen"]
    assert gen_info["prompt_version"] == GEN_PROMPT_VERSION and gen_info["model"] == "gemini-x"
    assert "passage" not in out["questions"][0] and "source_quote" not in out["questions"][0]
    assert ai.calls[0]["existing"] == ["Old question about volumes?"]  # gửi kèm câu đã có
    assert gdb.query(ReviewQuestion).count() == 1  # không lưu DB


def test_retry_only_missing_with_feedback(gdb):
    first = {"questions": [mcq("recognize", 1), mcq("recognize", 2, quote="totally invented sentence here ok")]}
    second = {"questions": [mcq("recognize", 3)]}
    ai = FakeAI({"mcq": [first, second]})
    out = gen.generate(gdb, SKILL, write=ai, need={"recognize": 2})
    assert len(out["questions"]) == 2 and out["calls"] == 2
    assert ai.calls[1]["need"] == {"recognize": 1}  # chỉ soạn lại phần thiếu
    assert any("not copied exactly" in f for f in ai.calls[1]["feedback"])
    assert ai.calls[1]["existing"][-1] == mcq("recognize", 1)["content"]  # câu vừa nhận cũng vào danh sách tránh trùng
    assert out["questions"][1]["ai_check"]["gen"]["attempt"] == 2


def test_gives_up_after_two_retries(gdb):
    bad = {"questions": [mcq(passage=9)]}
    ai = FakeAI({"mcq": [bad, AIOutputError("broken"), bad]})
    out = gen.generate(gdb, SKILL, write=ai, need={"recognize": 1})
    assert out["questions"] == [] and out["calls"] == 3 and out["missing"] == {"recognize": 1}
    assert len(out["rejected"]) == 3 and "not valid JSON" in ai.calls[2]["feedback"][0]


def test_requires_open_skill_and_chunks(gdb):
    gdb.get(ReviewSkillScope, SKILL).label = "closed"
    gdb.commit()
    with pytest.raises(gen.GenError) as err:
        gen.generate(gdb, SKILL, write=FakeAI({}))
    assert err.value.code == "not_open"
    gdb.get(ReviewSkillScope, SKILL).label = "open"
    gdb.query(KnowledgeChunk).delete()
    gdb.commit()
    with pytest.raises(gen.GenError) as err:
        gen.generate(gdb, SKILL, write=FakeAI({}))
    assert err.value.code == "no_source"
    with pytest.raises(gen.GenError):
        gen.generate(gdb, 999, write=FakeAI({}))


def test_ai_unavailable_propagates(gdb):
    from app.ai.review.base import AIUnavailableError

    with pytest.raises(AIUnavailableError):
        gen.generate(gdb, SKILL, write=FakeAI({"mcq": [AIUnavailableError("503")]}), need={"recognize": 1})
