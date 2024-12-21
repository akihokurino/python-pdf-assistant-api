from datetime import datetime


class User:
    def __init__(self, _id: str, name: str, created_at: datetime):
        self.id = _id
        self.name = name
        self.created_at = created_at
