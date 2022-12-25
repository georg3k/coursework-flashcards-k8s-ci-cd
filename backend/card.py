import uuid

# Card class
class Card:
    def __init__(self, front, back, deck, id=""):
        self.id = uuid.uuid4().hex if not id else id
        self.front = front
        self.back = back
        self.deck = deck

    # Return dictionary representation of object
    def dict(self):
        return {
            "id": self.id,
            "front": self.front,
            "back": self.back,
            "deck": self.deck,
        }

    @classmethod
    def make_from_dict(cls, d):
        # Initialise User object from a dictionary
        return cls(d["front"], d["back"], d["deck"], d["id"])
