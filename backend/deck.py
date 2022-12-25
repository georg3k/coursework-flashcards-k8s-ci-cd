import uuid

# Deck class
class Deck:
    def __init__(self, title, description):
        self.id = uuid.uuid4().hex if not id else id
        self.title = title
        self.description = description

    # Return dictionary representation of object
    def dict(self):
        return {"id": self.id, "title": self.title, "description": self.description}
