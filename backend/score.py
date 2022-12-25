import uuid

# Score class
class Score:
    def __init__(self, user, card, last, score, id=""):
        self.id = uuid.uuid4().hex if not id else id
        self.user = user
        self.card = card
        self.last = last
        self.score = score

    # Return dictionary representation of object
    def dict(self):
        return {
            "id": self.id,
            "user": self.user,
            "card": self.card,
            "last": self.last,
            "score": self.score,
        }

    @classmethod
    def make_from_dict(cls, d):
        # Initialise User object from a dictionary
        return cls(d["user"], d["card"], d["last"], d["score"], d["id"])
