import uuid


# User class
class User:
    def __init__(self, username, id=""):
        # Main initialiser
        self.username = username
        self.id = uuid.uuid4().hex if not id else id

    @classmethod
    def make_from_dict(cls, d):
        # Initialise User object from a dictionary
        return cls(d["username"], d["id"])

    def dict(self):
        # Return dictionary representation of the object
        return {"id": self.id, "username": self.username}

    def display_name(self):
        # Return concatenation of name components
        return self.username

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    def get_id(self):
        return self.id
