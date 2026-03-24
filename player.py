# ---------------- PLAYER CLASS ----------------

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def draw_card(self, deck, count=1):
        for _ in range(count):
            card = deck.draw_card()
            if card:
                self.hand.append(card)

    def play_card(self, index):
        return self.hand.pop(index)

    def show_hand(self):
        print(f"\n{self.name}'s Hand:")
        for i, card in enumerate(self.hand):
            print(f"{i}: {card}")

    def has_no_cards(self):
        return len(self.hand) == 0


# ---------------- TEST CODE (RUNS DIRECTLY) ----------------

if __name__ == "__main__":
    print("✅ player.py is running correctly")

    # Minimal Card + Deck for testing
    class Card:
        def __init__(self, color, value):
            self.color = color
            self.value = value

        def __str__(self):
            return f"{self.color} {self.value}"

    class Deck:
        def __init__(self):
            self.cards = [
                Card("Red", 3),
                Card("Blue", 5),
                Card("Green", 7),
                Card("Yellow", "Skip"),
                Card("Wild", "Wild")
            ]

        def draw_card(self):
            return self.cards.pop(0) if self.cards else None

    # Run test
    deck = Deck()
    player = Player("Test Player")

    player.draw_card(deck, 5)
    player.show_hand()

    print("\n🎉 player.py test completed successfully")




