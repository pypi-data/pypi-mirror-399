import attr


@attr.s(auto_attribs=True, frozen=True)
class User:
    """
    Represents an authenticated Pocket Casts user.

    Attributes:
        email (str): User's email address.
        uuid (str): Unique user identifier.
        is_new (bool): Indicates if the user is new.
        access_token (str): Authentication token for API requests.
        token_type (str): Token type (e.g., "Bearer").
        expires_in (int): Token expiry in seconds.
        refresh_token (str): Token for refreshing authentication.
    """

    email: str
    uuid: str
    is_new: bool
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
