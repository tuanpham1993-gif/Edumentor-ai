"""G1Output -> NormalizedG1Output (Phase 3 normalization + G2 skill linking).

Pure mapping. The lookups are passed in so this module needs no database or Qdrant:
    link_skills(names)        -> list[SkillLink]       one per name, same order
    match_role(raw_name)      -> RoleMatch             (skill_graph/role_matcher.py)
    match_entity(kind, name)  -> EntityMatch           kind: certification | technical_domain | industry
The service (app/services/skill_linking_service.py) provides the real implementations.

Every skill name is linked once (skill_profiles, target technologies and practical-experience
skills share one batch), so the same wording always gets the same skill_id.
"""
from __future__ import annotations

from typing import Callable

from app.utils.learner_analyzer.schemas import (
    EntityMatch,
    G1Output,
    LinkedSkillProfile,
    MatchMethod,
    NormalizedCareerBackground,
    NormalizedG1Output,
    NormalizedGoal,
    NormalizedPracticalExperience,
    NormalizedTargetRole,
    ResolutionStatus,
    SkillLink,
)
from app.utils.skill_graph.role_matcher import RoleMatch

LinkSkills = Callable[[list[str]], list[SkillLink]]
MatchRole = Callable[[str | None], RoleMatch]
MatchEntity = Callable[[str, str], EntityMatch]


def role_to_entity(m: RoleMatch) -> EntityMatch:
    """A job title / previous role matched against job roles, as an EntityMatch (canonical_id = role_id)."""
    return EntityMatch(raw_name=m.raw_name, canonical_name=m.canonical_name, canonical_id=m.role_id,
                       match_method=MatchMethod(m.match_method) if m.match_method else None,
                       match_score=m.match_score, resolution_status=ResolutionStatus(m.resolution_status),
                       candidate_ids=m.candidate_ids)


def normalize_g1(out: G1Output, link_skills: LinkSkills, match_role: MatchRole,
                 match_entity: MatchEntity) -> NormalizedG1Output:
    goal, cb = out.goal, out.career_background

    names = list(dict.fromkeys(
        [s.skill_name for s in out.skill_profiles]
        + list(goal.target_technologies)
        + [r for p in out.practical_experience for r in p.related_skills]
    ))
    links = dict(zip(names, link_skills(names))) if names else {}

    raw_role = goal.target_role.raw_name
    if raw_role and raw_role.strip():
        rm = match_role(raw_role)
        target_role = NormalizedTargetRole(**{**rm.to_normalized_target_role(), "raw_name": raw_role})
    else:
        target_role = NormalizedTargetRole(raw_name=None)

    def role_entity(name: str | None) -> EntityMatch | None:
        return role_to_entity(match_role(name)) if name and name.strip() else None

    return NormalizedG1Output(
        goal=NormalizedGoal(
            original_query=goal.original_query,
            target_role=target_role,
            target_technologies=[links[t] for t in dict.fromkeys(goal.target_technologies)],
            goal_type=goal.goal_type,
        ),
        career_background=NormalizedCareerBackground(
            career_level=cb.career_level,
            current_job_title=role_entity(cb.current_job_title),
            industry=match_entity("industry", cb.industry) if cb.industry else None,
            technical_domains=[match_entity("technical_domain", d) for d in cb.technical_domains],
            certifications=[match_entity("certification", c) for c in cb.certifications],
            previous_job_roles=[e for e in (role_entity(r) for r in cb.previous_job_roles) if e],
            relevant_it_work_experience=cb.relevant_it_work_experience,
        ),
        skill_profiles=[
            LinkedSkillProfile(skill_name=s.skill_name, proficiency_level=s.proficiency_level,
                               experience_duration=s.experience_duration, evidence_type=s.evidence_type,
                               link=links[s.skill_name])
            for s in out.skill_profiles
        ],
        status=out.status,
        practical_experience=[
            NormalizedPracticalExperience(description=p.description,
                                          related_skills=[links[r] for r in p.related_skills],
                                          evidence_type=p.evidence_type)
            for p in out.practical_experience
        ],
        learning_constraints=out.learning_constraints,
        clarification_required=out.clarification_required,
        unknown_fields=out.unknown_fields,
    )
