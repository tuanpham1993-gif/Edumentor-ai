"""Role matcher: free-text target role -> job_roles.role_id (app/utils/skill_graph/role_matcher.py)."""
import pytest

from app.utils.skill_graph.role_matcher import RoleMatcher, load_roles_from_json

MATCHER = RoleMatcher(load_roles_from_json())
NAME_TO_ID = {r.role_name: r.role_id for r in MATCHER.roles.values()}


@pytest.mark.parametrize("raw, expected", [
    # exact name / alias, case, punctuation and spacing
    ("frontend developer", "Frontend Developer"),
    ("FRONT-END DEVELOPER", "Frontend Developer"),
    ("front end dev", "Frontend Developer"),
    ("fullstack dev", "Full Stack Developer"),
    ("cyber security analyst", "Cybersecurity Analyst"),
    # abbreviations and symbols
    ("react dev", "React Developer"),
    ("nodejs dev", "Node.js Developer"),
    ("c++ dev", "C++ Developer"),
    ("C# developer", ".NET Developer"),
    (".net developer", ".NET Developer"),
    ("ml engineer", "Machine Learning Engineer"),
    ("network admin", "Network Administrator"),
    ("sysadmin", "System Administrator"),
    ("devops", "DevOps Engineer"),
    ("pentester", "Penetration Tester"),
    # level words are removed (career level is a separate G1 field)
    ("junior frontend developer", "Frontend Developer"),
    ("Senior Backend Engineer", "Backend Developer"),
    # filler words
    ("become a data engineer", "Data Engineer"),
    # typos and extra words (fuzzy)
    ("data scientst", "Data Scientist"),
    ("andriod developer", "Android Developer"),
    ("frontend web developer", "Frontend Developer"),
    # a career field names its primary role
    ("data analytics", "Data Analyst"),
    ("data science", "Data Scientist"),
    ("web development", "Web Developer"),
    ("NLP engineering", "NLP Engineer"),
    ("automation tester", "Automation Test Engineer"),
])
def test_matched(raw, expected):
    r = MATCHER.match(raw)
    assert r.resolution_status == "matched", (raw, r)
    assert r.role_id == NAME_TO_ID[expected]


@pytest.mark.parametrize("raw, must_include", [
    ("golang backend developer", {"Backend Developer", "Go Developer"}),
    ("cloud security", {"Cloud Security Engineer"}),
])
def test_ambiguous_offers_right_candidates(raw, must_include):
    r = MATCHER.match(raw)
    assert r.resolution_status == "ambiguous", (raw, r)
    assert r.role_id is None
    names = {MATCHER.roles[c].role_name for c in r.candidate_ids}
    assert must_include <= names
    # only roles sharing a meaningful word are offered
    assert "Game Developer" not in names and "QA Engineer" not in names


@pytest.mark.parametrize("raw", ["AI professional", "teacher", "developer", "", "   ", None])
def test_unresolved_never_guesses(raw):
    r = MATCHER.match(raw)
    assert r.role_id is None
    assert r.resolution_status in ("unresolved", "ambiguous")
    if raw in ("teacher", "developer", "", "   ", None):
        assert r.resolution_status == "unresolved" and r.candidate_ids == []


def test_semantic_hook_used_only_when_confident():
    target = NAME_TO_ID["Cloud Engineer"]
    confident = RoleMatcher(list(MATCHER.roles.values()), semantic_search=lambda q: [(target, 0.93), (1, 0.70)])
    assert confident.match("cloud guy").role_id == target
    assert confident.match("cloud guy").match_method == "semantic"
    close = RoleMatcher(list(MATCHER.roles.values()), semantic_search=lambda q: [(target, 0.90), (1, 0.88)])
    assert close.match("cloud guy").role_id is None


def test_output_fits_normalized_target_role():
    from app.utils.learner_analyzer.schemas import NormalizedTargetRole
    NormalizedTargetRole.model_validate(MATCHER.match("react dev").to_normalized_target_role())
    NormalizedTargetRole.model_validate(MATCHER.match("teacher").to_normalized_target_role())


@pytest.mark.parametrize("raw, expected", [
    ("lập trình viên backend", "Backend Developer"),
    ("lap trinh vien backend", "Backend Developer"),   # typed without accents
    ("dev backend", "Backend Developer"),              # Vietnamese word order
    ("kỹ sư dữ liệu", "Data Engineer"),
    ("chuyên viên phân tích dữ liệu", "Data Analyst"),
    ("trở thành data analyst", "Data Analyst"),
    ("làm tester", "QA Engineer"),
    ("kỹ sư devops", "DevOps Engineer"),
    ("quản trị mạng", "Network Administrator"),
    ("mảng data engineering", "Data Engineer"),
])
def test_vietnamese_matched(raw, expected):
    r = MATCHER.match(raw)
    assert r.resolution_status == "matched", (raw, r)
    assert r.role_id == NAME_TO_ID[expected]


@pytest.mark.parametrize("raw, must_include", [
    ("mảng AI", {"AI Engineer"}),                      # "mảng" (area) must not become "mạng" (network)
    ("ngành an ninh mạng", {"Cybersecurity Analyst", "Security Engineer"}),
])
def test_vietnamese_broad_fields_ask_for_clarification(raw, must_include):
    r = MATCHER.match(raw)
    assert r.resolution_status == "ambiguous" and r.role_id is None
    assert must_include <= {MATCHER.roles[c].role_name for c in r.candidate_ids}
