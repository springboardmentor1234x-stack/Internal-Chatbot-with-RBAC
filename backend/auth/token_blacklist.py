class TokenBlacklist:
    """
    In-memory token blacklist.
    Used to invalidate JWTs before expiry (logout, forced logout).
    """

    def __init__(self):
        self.blacklisted_tokens = set()

    def blacklist(self, token: str):
        self.blacklisted_tokens.add(token)

    def is_blacklisted(self, token: str) -> bool:
        return token in self.blacklisted_tokens


# Singleton instance
token_blacklist = TokenBlacklist()
