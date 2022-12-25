from user import User
from score import Score
from deck import Deck
from session import Session
from card import Card
from pymongo import MongoClient
import datetime

mongo = MongoClient("localhost:27017", username="admin", password="pass")

id = "0"

cards = []
prevs = []
unseen = []
all_scores = mongo.flashcards.scores
# all_scores = all_scores.find({"user": "94e5d1369db6404f904ea76927ce52a9"})

for s in all_scores.find({"user": "94e5d1369db6404f904ea76927ce52a9"}):
    score = Score.make_from_dict(s)
    card = Card.make_from_dict(mongo.flashcards.cards.find_one({"id": str(score.card)}))
    last = datetime.datetime.strptime(score.last, "%Y-%m-%d")
    elps = (datetime.datetime.today() - last).days
    if (str(card.deck) == id) and (elps >= int(score.score)):
        prevs.append(card)

for c in mongo.flashcards.cards.find({"deck": id}):
    card = Card.make_from_dict(c)
    if card.id not in [
        s["card"] for s in all_scores.find({"user": "94e5d1369db6404f904ea76927ce52a9"})
    ]:
        unseen.append(card.id)

print(prevs)
print("")
print(unseen)
