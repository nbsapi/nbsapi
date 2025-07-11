from nbsapi import models

from .user import CurrentUserDep


async def validate_is_authenticated(
    current_user: CurrentUserDep,
) -> models.User:
    """
    This just returns as the CurrentUserDep dependency already throws if there is an issue with the auth token.
    """  # noqa: D401, D404
    return current_user
