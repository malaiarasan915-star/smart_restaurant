from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps

def role_required(allowed_roles):
    """
    Decorator for views that checks whether a user has a specific role.
    If the user does not have the role, raise PermissionDenied (403).
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]
        
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped_view
    return decorator
