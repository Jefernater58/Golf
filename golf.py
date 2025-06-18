# golf.py - Frederick Rayner
# https://github.com/Jefernater58/Golf

import random


class Card:
    def __init__(self, suit, value=-1):
        self.suit = suit
        self.rank = value

        self.score = -1
        if suit == "joker":
            self.score = -2
        elif 1 <= value <= 10:
            self.score = value
        elif value <= 12:
            self.score = 10
        elif value == 13:
            self.score = 0
        else:
            print(f"error: card rank is invalid: {self.rank}, {self.suit}")

    def create_string(self):
        if self.suit == "Joker":
            return "Joker"

        value_names = {11: "Jack", 12: "Queen", 13: "King", 1: "Ace"}
        if 2 <= self.rank <= 10:
            return f"{self.rank} of {self.suit}"
        return f"{value_names[self.rank]} of {self.suit}"


class Pile:
    def __init__(self, cards=[]):
        self.cards = cards

    def fill_deck(self):
        self.cards = ([Card("Spades", rank) for rank in range(1, 14)] + [Card("Hearts", rank) for rank in range(1, 14)] +
                      [Card("Diamonds", rank) for rank in range(1, 14)] + [Card("Clubs", rank) for rank in range(1, 14)] +
                      [Card("Joker") for _ in range(2)])

    def append_card(self, card):
        self.cards.append(card)

    def remove_top(self):
        return self.cards.pop(0)

    def shuffle(self):
        random.shuffle(self.cards)


deck = Pile()
deck.fill_deck()
deck.shuffle()

print("Welcome to Golf! ")
