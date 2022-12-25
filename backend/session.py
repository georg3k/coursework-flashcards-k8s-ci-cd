import uuid

# Session class
class Session:
    def __init__(self, user, deck, cards, id=""):
        self.id = uuid.uuid4().hex if not id else id
        self.user = user
        self.deck = deck
        self.cards = cards

    # Return dictionary representation of object
    def dict(self):
        return {
            "id": self.id,
            "user": self.user,
            "deck": self.deck,
            "cards": self.cards,
        }

    @classmethod
    def make_from_dict(cls, d):
        # Initialise User object from a dictionary
        return cls(d["user"], d["deck"], d["cards"], d["id"])
