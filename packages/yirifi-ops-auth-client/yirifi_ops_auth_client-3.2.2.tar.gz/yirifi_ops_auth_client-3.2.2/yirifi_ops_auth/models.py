"""Data models for auth client."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AuthUser:
    """Authenticated user information with RBAC support."""

    user_id: str  # Immutable UUID, use for storage in domain tables
    id: int  # Internal ID (kept for backward compatibility)
    email: str
    display_name: str
    is_admin: bool  # deprecated - use has_permission() instead
    microsites: list[str]

    # RBAC fields
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    effective_role: Optional[str] = None

    def has_access_to(self, microsite_id: str) -> bool:
        """Check if user has access to a microsite."""
        if self.is_admin:
            return True
        return microsite_id in self.microsites

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission.

        Admin users automatically have all permissions.

        Args:
            permission: Permission code (e.g., 'report:create')

        Returns:
            True if user has the permission
        """
        if self.is_admin:
            return True
        return permission in self.permissions

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role.

        Admin users automatically have all roles.

        Args:
            role: Role code (e.g., 'editor')

        Returns:
            True if user has the role
        """
        if self.is_admin:
            return True
        return role in self.roles

    def has_any_permission(self, *permissions: str) -> bool:
        """Check if user has any of the specified permissions.

        Admin users automatically have all permissions.

        Args:
            *permissions: Permission codes to check

        Returns:
            True if user has at least one of the permissions
        """
        if self.is_admin:
            return True
        return any(p in self.permissions for p in permissions)

    def has_all_permissions(self, *permissions: str) -> bool:
        """Check if user has all of the specified permissions.

        Admin users automatically have all permissions.

        Args:
            *permissions: Permission codes to check

        Returns:
            True if user has all of the permissions
        """
        if self.is_admin:
            return True
        return all(p in self.permissions for p in permissions)


@dataclass
class VerifyResult:
    """Result from auth verification."""

    valid: bool
    user: Optional[AuthUser] = None
    error: Optional[str] = None
    redirect_url: Optional[str] = None
    has_access: bool = True
    role: Optional[str] = None  # deprecated - use user.effective_role instead
