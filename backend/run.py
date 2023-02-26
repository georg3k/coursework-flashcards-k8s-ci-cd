# MODULE IMPORTS

# Flask modules
from flask import Flask, render_template, request, request
from flask_login import LoginManager, login_required, current_user
from flask_talisman import Talisman
from flask_bcrypt import Bcrypt
from bson.json_util import dumps
import datetime

# Other modules
from pymongo import MongoClient
import configparser
import json

# Local imports
from user import User
from score import Score
from deck import Deck
from session import Session
from card import Card

# Prometheus
from prometheus_flask_exporter import PrometheusMetrics

# Create app
app = Flask(__name__)
metrics = PrometheusMetrics(app)

# static information as metric
metrics.info('app_info', 'Flashcards App API Backend', version='1.0.0')

# Configuration
config = configparser.ConfigParser()
config.read("configuration.ini")
default = config["DEFAULT"]
app.config["MONGO_URI"] = default["MONGO_URI"]
app.secret_key = default["SECRET_KEY"]

# Create Pymongo
mongo = MongoClient(
    default["MONGO_URI"], username=default["MONGO_USER"], password=default["MONGO_PASS"]
)

# Create login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# API

# Initialize or get current user session for id deck
@login_required
def sessions_id(id):
    session = mongo.flashcards.sessions.find_one({"user": current_user.id, "deck": id})

    if session:
        response = app.response_class(
            response=dumps(session), status=200, mimetype="application/json"
        )
        return response
    else:
        cards = []
        prevs = []
        unseen = []
        all_scores = mongo.flashcards.scores

        for s in all_scores.find({"user": current_user.id}):
            score = Score.make_from_dict(s)
            card = Card.make_from_dict(
                mongo.flashcards.cards.find_one({"id": score.card})
            )
            last = datetime.datetime.strptime(score.last, "%Y-%m-%d")
            elps = (datetime.datetime.today() - last).days
            if (card.deck == id) and (elps >= int(score.score)):
                prevs.append(card)

        for c in mongo.flashcards.cards.find({"deck": id}):
            card = Card.make_from_dict(c)
            if card.id not in [
                s["card"] for s in all_scores.find({"user": current_user.id})
            ]:
                unseen.append(card)

        cards += prevs[0 : min(20, len(prevs))]
        cards += unseen[0 : min(20 - len(cards), len(unseen))]
        cards = [c.id for c in cards]

        for u in unseen[0 : min(20 - min(20, len(prevs)), len(unseen))]:
            new_score = Score(
                current_user.id, u.id, str(datetime.datetime.today().date()), "1"
            )
            mongo.flashcards.scores.insert_one(new_score.dict())

        session = Session(current_user.id, id, str(cards).replace("'", '"'))
        mongo.flashcards.sessions.insert_one(session.dict())

        response = app.response_class(
            response=dumps(session.dict()), status=200, mimetype="application/json"
        )
        return response


# Assert positive answer for a given card
@app.route("/api/sessions/<id>/<card>/yes", methods=["POST"])
@login_required
def sessions_id_card_yes(id, card):
    session = mongo.flashcards.sessions.find_one({"user": current_user.id, "deck": id})
    if session:
        s = Session.make_from_dict(session)
        s.cards = json.loads(s.cards)

        if card not in s.cards:
            response = app.response_class(status=404, mimetype="application/json")
            return response

        score = mongo.flashcards.scores.find_one(
            {"user": current_user.id, "card": card}
        )
        score = Score.make_from_dict(score)

        mongo.flashcards.scores.update_one(
            {"user": current_user.id, "card": card},
            {
                "$set": {
                    "score": str(int(score.score) * 2),
                    "last": str(datetime.datetime.today().date()),
                }
            },
        )

        s.cards.remove(card)
        mongo.flashcards.sessions.update_one(
            {"user": current_user.id, "deck": id},
            {"$set": {"cards": str(s.cards).replace("'", '"')}},
        )
        session = mongo.flashcards.sessions.find_one(
            {"user": current_user.id, "deck": id}
        )

        if len(s.cards) == 0:
            mongo.flashcards.sessions.delete_one({"user": current_user.id, "deck": id})
            response = app.response_class(
                response=dumps({"fin": "yes"}), status=200, mimetype="application/json"
            )
            return response

        response = app.response_class(
            response=dumps(session), status=200, mimetype="application/json"
        )
        return response
    else:
        response = app.response_class(status=404, mimetype="application/json")
        return response


# Assert negative answer for a given card
@app.route("/api/sessions/<id>/<card>/no", methods=["POST"])
@login_required
def sessions_id_card_no(id, card):
    session = mongo.flashcards.sessions.find_one({"user": current_user.id, "deck": id})
    if session:
        s = Session.make_from_dict(session)
        s.cards = json.loads(s.cards)

        if card not in s.cards:
            response = app.response_class(status=404, mimetype="application/json")
            return response

        score = mongo.flashcards.scores.find_one(
            {"user": current_user.id, "card": card}
        )
        score = Score.make_from_dict(score)

        mongo.flashcards.scores.update_one(
            {"user": current_user.id, "deck": id},
            {"$set": {"score": "1", "last": str(datetime.datetime.today().date())}},
        )

        s.cards.remove(card)
        mongo.flashcards.sessions.update_one(
            {"user": current_user.id, "deck": id},
            {"$set": {"cards": str(s.cards).replace("'", '"')}},
        )
        session = mongo.flashcards.sessions.find_one(
            {"user": current_user.id, "deck": id}
        )

        if len(s.cards) == 0:
            mongo.flashcards.sessions.delete_one({"user": current_user.id, "deck": id})
            response = app.response_class(
                response=dumps({"fin": "yes"}), status=200, mimetype="application/json"
            )
            return response

        response = app.response_class(
            response=dumps(session), status=200, mimetype="application/json"
        )
        return response
    else:
        response = app.response_class(status=404, mimetype="application/json")
        return response


# Get card info for given id
@app.route("/api/cards/<id>", methods=["GET"])
@login_required
def cards_id(id):
    card = mongo.flashcards.cards.find_one({"id": id})
    if card:
        response = app.response_class(
            response=dumps(card), status=200, mimetype="application/json"
        )
        return response
    else:
        response = app.response_class(status=404, mimetype="application/json")
        return response


# Get score info for given id
@app.route("/api/scores/<id>", methods=["GET"])
@login_required
def scores_id(id):
    score = mongo.flashcards.scores.find_one({"card": id})
    if score:
        response = app.response_class(
            response=dumps(score), status=200, mimetype="application/json"
        )
        return response
    else:
        response = app.response_class(status=404, mimetype="application/json")
        return response


# Get all decks
@app.route("/api/decks", methods=["GET"])
@login_required
def decks():
    decks = mongo.flashcards.decks.find({})
    if decks:
        response = app.response_class(
            response=dumps(decks), status=200, mimetype="application/json"
        )
        return response
    else:
        response = app.response_class(status=404, mimetype="application/json")
        return response


# Get specific deck
@app.route("/api/decks/<id>", methods=["GET"])
@login_required
def decks_id(id):
    decks = mongo.flashcards.decks.find({"id": id})
    if decks:
        response = app.response_class(
            response=dumps(decks), status=200, mimetype="application/json"
        )
        return response
    else:
        response = app.response_class(status=404, mimetype="application/json")
        return response


# Load user from user ID
@login_manager.user_loader
def load_user(userid):
    # Return user object or none
    users = mongo.flashcards.users
    user = users.find_one({"id": userid}, {"_id": 0})
    if user:
        return User.make_from_dict(user)
    return None


# Start server
app.run(host="0.0.0.0", port=8080, debug=True)
