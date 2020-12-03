# AUTH_ADMIN-* requires MENU-ADMIN-AUTH
# MENU-ADMIN-AUTH requires MENU-ADMIN


PERMS = [
    # ADMIN
    'MENU-ADMIN-AUTH',
    'AUTH_ADMIN-USER-CREATE',
    'AUTH_ADMIN-USER-READ',
    'AUTH_ADMIN-USER-LIST',
    'AUTH_ADMIN-USER-ROLES',
    'AUTH_ADMIN-USER-EDIT',
    'AUTH_ADMIN-USER-DELETE',
    'AUTH_ADMIN-USER-RESET_FAILED_LOGINS',
    'AUTH_ADMIN-ROLE-CREATE',
    'AUTH_ADMIN-ROLE-READ',
    'AUTH_ADMIN-ROLE-LIST',
    'AUTH_ADMIN-ROLE-EDIT',
    'AUTH_ADMIN-ROLE-DELETE',
    'AUTH_ADMIN-ROLE-USERS',
    'AUTH_ADMIN-PERMISSION-LIST',
    'AUTH_ADMIN-PERMISSION-READ',
    # Normal
    'AUTH-PERMISSION_MISSING',
    # ATTENTION: You do not want permissions to be created/changed through
    # the Admin interface since no route would check for those permissions.
    # 'AUTH_PERMISSION_CREATE',
    # 'AUTH_PERMISSION_UPDATE',
    # 'AUTH_PERMISSION_DELETE',
]


def run_install():
    """Is run by `Rune-Basis` when install is clicked."""
    pass


def run_remove():
    """Is run by `Rune-Basis` when uninstall is clicked."""
    pass
