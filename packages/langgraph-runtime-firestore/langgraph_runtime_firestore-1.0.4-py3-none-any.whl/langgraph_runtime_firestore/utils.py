from starlette.exceptions import HTTPException

def _get_username_from_ctx() -> str:
    """Extract username from auth context."""

    # Try global auth context
    from langgraph_api.utils import get_auth_ctx

    ctx = get_auth_ctx()
    if ctx:
        user = getattr(ctx, "user", None)
        if user:
            identity = (
                user.get("identity")
                if isinstance(user, dict)
                else getattr(user, "identity", None)
            )
            if identity:
                return identity

    raise HTTPException(status_code=401, detail="Authentication required")