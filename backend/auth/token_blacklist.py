class TokenBlacklist:
    def __init__(self):
        self.blacklisted_tokens = set()

    def blacklist(self, token: str):
        self.blacklisted_tokens.add(token)

    def is_blacklisted(self, token: str) -> bool:
        return token in self.blacklisted_tokens

token_blacklist = TokenBlacklist()