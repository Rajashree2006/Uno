from flask import Flask, jsonify, request, render_template
import random
from groq import Groq



app = Flask(__name__)
import os 
API_KEY= os.getenv("API_KEY")



# =====================
# UNO GAME CLASS
# =====================
class UnoGame:

    def __init__(self):
        self.colors = ["Red", "Blue", "Green", "Yellow"]
        self.target_score = 500
        self.start_match()

    # =====================
    # MATCH / ROUND
    # =====================
    def start_match(self):
        self.player_score = 0
        self.system_score = 0
        self.start_round()

    def start_round(self):

        self.create_deck()

        self.player_hand = [self.draw_card() for _ in range(7)]
        self.system_hand = [self.draw_card() for _ in range(7)]

        self.discard = []
        self.round_over = False
        self.winner = None
        self.wild_color = None

        card = self.draw_card()

        while card.startswith("Wild_Draw_4"):
            self.deck.append(card)
            random.shuffle(self.deck)
            card = self.draw_card()

        self.current_card = card

        if card.startswith("Wild"):
            self.current_color = random.choice(self.colors)
        else:
            self.current_color = card.split("_")[0]

        self.turn = "player"
        self.message = ""
        self.uno_called = False

    # =====================
    # DECK
    # =====================
    def create_deck(self):
        self.deck = []

        for color in self.colors:
            for i in range(10):
                self.deck.append(f"{color}_{i}.jpg")

            self.deck.append(f"{color}_Skip.jpg")
            self.deck.append(f"{color}_Reverse.jpg")
            self.deck.append(f"{color}_Draw_2.jpg")

        for _ in range(4):
            self.deck.append("Wild.jpg")
            self.deck.append("Wild_Draw_4.jpg")

        random.shuffle(self.deck)

    def draw_card(self):
        if not self.deck:
            return None
        return self.deck.pop()

    # =====================
    # PLAYABLE
    # =====================
    def playable(self, card):

        if card.startswith("Wild"):
            return True

        color = card.split("_")[0]
        value = card.replace(".jpg", "").split("_")[-1]
        top_value = self.current_card.replace(".jpg", "").split("_")[-1]

        return color == self.current_color or value == top_value

    # =====================
    # PLAYER MOVE
    # =====================
    def player_play(self, card, chosen_color):

        if self.round_over:
            return False

        if card not in self.player_hand or not self.playable(card):
            return False

        self.player_hand.remove(card)
        self.discard.append(self.current_card)
        self.current_card = card
        self.wild_color = None

        if card.startswith("Wild"):
            self.current_color = chosen_color
        else:
            self.current_color = card.split("_")[0]

        extra_turn = self.apply_action(card, "system")

        # UNO logic
        if len(self.player_hand) == 1:
            self.uno_called = False

        if len(self.player_hand) == 0:
            self.finish_round("player")
            return True

        # LIVE SCORE UPDATE
        self.update_live_score()

        if not extra_turn:
            self.system_turn()

        return True

    # =====================
    # SYSTEM TURN
    # =====================
    def system_turn(self):

        if self.round_over:
            return

        playable_cards = [c for c in self.system_hand if self.playable(c)]

        if playable_cards:

            card = playable_cards[0]
            self.system_hand.remove(card)

            self.discard.append(self.current_card)
            self.current_card = card

            if card.startswith("Wild"):
                color = random.choice(self.colors)
                self.current_color = color
                self.wild_color = color
                self.message = f"System played Wild"
            else:
                self.current_color = card.split("_")[0]
                self.message = f"System played {card}"

            extra_turn = self.apply_action(card, "player")

            if len(self.system_hand) == 0:
                self.finish_round("system")
                return

            # LIVE SCORE UPDATE
            self.update_live_score()

            if extra_turn:
                self.system_turn()
            else:
                self.turn = "player"

        else:
            new = self.draw_card()
            if new:
                self.system_hand.append(new)
                self.message = "System draws a card"

            self.turn = "player"

    # =====================
    # ACTION RULES
    # =====================
    def apply_action(self, card, target):

        hand = self.player_hand if target == "player" else self.system_hand

        # Skip / Reverse (2-player same effect)
        if "Skip" in card or "Reverse" in card:
            self.message = f"{target} skipped"
            return True

        # Draw 2
        if "Draw_2" in card:
            for _ in range(2):
                hand.append(self.draw_card())
            self.message = f"{target} draws 2 cards"
            return True

        # Draw 4
        if "Wild_Draw_4" in card:
            for _ in range(4):
                hand.append(self.draw_card())
            self.message = f"{target} draws 4 cards"
            return True

        return False

    # =====================
    # UNO
    # =====================
    def call_uno(self):
        if len(self.player_hand) == 1:
            self.uno_called = True
            return True
        return False

    # =====================
    # LIVE SCORE (RUNNING)
    # =====================
    def update_live_score(self):
        self.player_score = self.calculate_hand_score(self.system_hand)
        self.system_score = self.calculate_hand_score(self.player_hand)

    def calculate_hand_score(self, hand):
        total = 0
        for c in hand:
            name = c.replace(".jpg", "")
            if "Wild" in name:
                total += 50
            elif any(x in name for x in ["Skip", "Reverse", "Draw_2"]):
                total += 20
            else:
                total += int(name.split("_")[-1])
        return total

    # =====================
    # ROUND END
    # =====================
    def finish_round(self, winner):
        self.round_over = True
        self.winner = winner
        self.update_live_score()

    # =====================
    # AI HINT
    # =====================
    def ai_hint(self):

        playable_cards = [c for c in self.player_hand if self.playable(c)]

        if not playable_cards:
            return "Draw"

        return playable_cards[0]


game = UnoGame()

# =====================
# ROUTES
# =====================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/start")
def start():
    game.start_match()
    return state()


@app.route("/next")
def next_round():
    game.start_round()
    return state()


@app.route("/state")
def state():
    return jsonify({

        "player_hand": game.player_hand,
        "system_count": len(game.system_hand),

        "current_card": game.current_card,
        "current_color": game.current_color,

        "player_score": game.player_score,
        "system_score": game.system_score,

        "turn": game.turn,
        "message": game.message,

        "wild_color": game.wild_color,

        "round_over": game.round_over,
        "winner": game.winner
    })


@app.route("/play", methods=["POST"])
def play():
    data = request.json
    success = game.player_play(data.get("card"), data.get("color"))

    if not success:
        return jsonify({"error": "Invalid move"})

    return state()


@app.route("/draw")
def draw():
    c = game.draw_card()
    if c:
        game.player_hand.append(c)

    game.update_live_score()
    game.system_turn()

    return state()


@app.route("/uno")
def uno():
    return jsonify({"success": game.call_uno()})


@app.route("/hint")
def hint():
    return jsonify({"hint": game.ai_hint()})


if __name__ == "__main__":
    app.run(debug=True)











