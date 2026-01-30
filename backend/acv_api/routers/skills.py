from fastapi import APIRouter

router = APIRouter()

@router.get("")
async def list_skills():
    """List all skills."""
    from acv_cli.skills import SkillManager
    mgr = SkillManager()
    return mgr.list_skills()

@router.get("/{skill_id}")
async def get_skill(skill_id: str):
    """Get skill details."""
    from acv_cli.skills import SkillManager
    mgr = SkillManager()
    skill = mgr.load_skill(skill_id)
    if not skill:
        return {"error": f"Skill not found: {skill_id}"}
    return skill.model_dump()

@router.post("/{skill_id}/validate")
async def validate_skill(skill_id: str):
    """Validate a skill."""
    from acv_cli.skills import SkillManager
    mgr = SkillManager()
    return mgr.validate_skill(skill_id)
