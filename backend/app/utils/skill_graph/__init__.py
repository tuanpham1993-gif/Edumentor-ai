"""Skill graph tooling: curated IT prerequisite graph, role candidate skills, and simulation.

Files:
- catalogue.py         Load skill_table.json / skill_alias.json / job_roles.json and resolve names to canonical IDs.
- graph_source.py      Curated source of truth: prerequisite / extension / related edges and role candidates (by name).
- build_skill_graph.py Resolve names, validate the graph, write datajson/skill_relation.json and role_candidate_skills.json.
- graph_ops.py         Backward prerequisite retrieval and learner-based trimming (pure functions).
- simulate_roles.py    Build a learning graph for every role and for sample learner profiles; write a report.
- role_matcher.py      Free-text target role -> role_id (exact, alias, level-word removal, fuzzy, optional Qdrant).
"""
