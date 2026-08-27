from functools import wraps
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request
from utils.helpers import error


def roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('role') not in roles:
                return error('You do not have permission to perform this action.', 403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


photographer_required = roles_required('photographer', 'administrator')
administrator_required = roles_required('administrator')


def current_user_id() -> str:
    return str(get_jwt_identity())


def current_role() -> str:
    return str(get_jwt().get('role') or '')


def can_manage_owner(owner_id: str) -> bool:
    """Administrators can manage all records; photographers can manage only their own."""
    return current_role() == 'administrator' or str(owner_id) == current_user_id()
