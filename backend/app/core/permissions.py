from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class AccessContext:
    account_active: bool
    user_active: bool
    is_system_admin: bool
    permissions: Mapping[str, bool]
    plan_features: frozenset[str]


def can_access(context: AccessContext, *, permission: str, feature: str = "core") -> bool:
    if not context.account_active or not context.user_active:
        return False
    if feature not in context.plan_features:
        return False
    if context.is_system_admin:
        return True
    return context.permissions.get(permission, False)
