from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ActorContext:
    actor_id: UUID
    run_id: UUID
    office_id: UUID
    role: str
    display_name: str
    barangay_id: UUID | None
    position: str | None
    household_id: UUID | None
    member_household_id: UUID | None
    identity_assurance: str = 'claimed_unverified'


def resolve_identity(db, selected_actor_id, *, system=False, historical=False):
    from .commands import DomainError
    try: selected_actor_id = UUID(str(selected_actor_id))
    except (ValueError,TypeError): raise DomainError(403,'actor_unavailable') from None
    row = db.execute('''SELECT a.*, v.status, v.barangay_id, v.position, r.state run_state,
        l.household_id, m.household_id member_household_id
        FROM actors a JOIN actor_versions v ON v.id=a.current_version_id
        JOIN evaluation_runs r ON r.id=a.run_id
        LEFT JOIN household_links l ON l.beneficiary_actor_id=a.id
        LEFT JOIN actor_member_links ml ON ml.id=a.current_member_link_id
        LEFT JOIN household_members m ON m.id=ml.member_id WHERE a.id=%s''',(selected_actor_id,)).fetchone()
    history_allowed=historical and row and row['role']=='auditor' and row['run_state']=='retired'
    if not row or row['status']!='active' or (row['run_state']!='active' and not history_allowed) or (row['role']=='system' and not system):
        raise DomainError(403,'actor_unavailable')
    return ActorContext(row['id'],row['run_id'],row['office_id'],row['role'],row['display_name'],row['barangay_id'],row['position'],row['household_id'],row['member_household_id'],
                        'system' if row['role']=='system' else 'claimed_unverified')


def require_role(context, *roles):
    from .commands import DomainError
    if context.role not in roles: raise DomainError(403,'action_not_permitted')


def require_independent(context, household_id):
    from .commands import DomainError
    if context.member_household_id==household_id or context.household_id==household_id:
        raise DomainError(403,'independent_actor_required')
