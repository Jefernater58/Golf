# golf.py - Frederick Rayner
# https://github.com/Jefernater58/Golf

import random
from termcolor import colored
from tabulate import tabulate

HAND_SIZE = 6  # number of cards a player has. MUST BE EVEN!!!


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
    def __init__(self, hidden, cards=None):
        self.hidden = hidden
        if cards is None:
            cards = []
        self.cards = cards

    def fill_deck(self):
        self.cards = ([Card("Spades", rank) for rank in range(1, 14)] + [Card("Hearts", rank) for rank in range(1, 14)] +
                      [Card("Diamonds", rank) for rank in range(1, 14)] + [Card("Clubs", rank) for rank in range(1, 14)] +
                      [Card("Joker") for _ in range(2)])

    def append_card(self, card):
        self.cards.append(card)

    def add_to_top(self, card):
        self.cards.insert(0, card)

    def get_size(self):
        return len(self.cards)

    def remove_top(self):
        return self.cards.pop(0)

    def shuffle(self):
        random.shuffle(self.cards)

    def create_top_card_string(self):
        if len(self.cards) > 0:
            if self.hidden:
                return "Hidden Card"
            return self.cards[0].create_string()
        else:
            return "Empty"


class Hand:
    def __init__(self, draw_p):
        self.width = HAND_SIZE // 2
        self.cards = [[None for _ in range(self.width)] for _ in range(2)]
        self.face_up = [[False for _ in range(self.width)] for _ in range(2)]
        for row in range(2):
            for card in range(self.width):
                self.cards[row][card] = draw_p.remove_top()

    def render(self):
        render_array = [["" for _ in range(self.width)] for _ in range(2)]
        for row in range(2):
            for card in range(self.width):
                if self.face_up[row][card]:
                    render_array[row][card] = self.cards[row][card].create_string()
                else:
                    render_array[row][card] = "Hidden Card"

        return tabulate(render_array, tablefmt="simple_grid", stralign="center").splitlines()

    def calculate_score(self):
        score = 0
        for card in range(self.width):
            c1 = self.cards[0][card]
            c2 = self.cards[1][card]
            if c1.rank == c2.rank:
                continue
            else:
                score += c1.score + c2.score
        return score


draw_pile = Pile(True)
draw_pile.fill_deck()
draw_pile.shuffle()

discard_pile = Pile(False)
discard_pile.append_card(draw_pile.remove_top())

print("GOLF.PY - by Freddie Rayner\nWelcome Human. Are you ready to play? I will let you go first...\n")

player_hand = Hand(draw_pile)
computer_hand = Hand(draw_pile)

while True:
    turn_row = input(">> In what row is the first card to turn over [0-1]? ")
    turn_column = input(f">> What column is this card [0-{player_hand.width - 1}]? ")
    if not turn_row.isdigit() or not turn_column.isdigit() or not (0 <= int(turn_row) <= 1) or not (
            0 <= int(turn_column) <= player_hand.width - 1):
        print("Invalid input, try again.")
        continue
    else:
        player_hand.face_up[int(turn_row)][int(turn_column)] = True
        break

while True:
    turn_row = input(">> In what row is the second card to turn over [0-1]? ")
    turn_column = input(f">> What column is this card [0-{player_hand.width - 1}]? ")
    if not turn_row.isdigit() or not turn_column.isdigit() or not (0 <= int(turn_row) <= 1) or not (
            0 <= int(turn_column) <= player_hand.width - 1):
        print("Invalid input, try again.")
        continue
    else:
        player_hand.face_up[int(turn_row)][int(turn_column)] = True
        break

game_over = False
while not game_over:
    draw_pile_render = tabulate([[draw_pile.create_top_card_string()]], tablefmt="simple_grid", stralign="center").splitlines()
    discard_pile_render = tabulate([[discard_pile.create_top_card_string()]], tablefmt="simple_grid", stralign="center").splitlines()
    print(f"DRAW PILE ({draw_pile.get_size()} cards)    " + colored(f"DISCARD PILE ({discard_pile.get_size()})", "dark_grey"))

    for line in range(len(draw_pile_render)):
        print(draw_pile_render[line].ljust(len(f"DRAW PILE ({draw_pile.get_size()} cards)    ")) + colored(discard_pile_render[line], "dark_grey"))

    player_hand_render = player_hand.render()
    computer_hand_render = computer_hand.render()

    print(colored("\n YOUR CARDS", "white").ljust(len(player_hand_render[0]) + 13) + colored(" COMPUTER'S CARDS", "blue"))
    for line in range(len(player_hand_render)):
        print(colored(player_hand_render[line], "white")+ "    " + colored(computer_hand_render[line], "blue"))

    print()
    while True:
        player_turn = input(">> Its your turn! Draw from the draw pile [0] or discard pile [1]? ")
        if not player_turn.isdigit() or int(player_turn) not in (0, 1):
            print("Invalid input, try again.")
            continue
        player_turn = int(player_turn)
        if player_turn == 0:
            if draw_pile.get_size() == 0:
                print("The draw pile is empty!")
                continue
            draw_card = draw_pile.remove_top()
        else:
            if discard_pile.get_size() == 0:
                print("The discard pile is empty!")
                continue
            draw_card = discard_pile.remove_top()
        break

    print(f"\nYou drew: {draw_card.create_string()}")

    take = input(">> Do you want this card [y/n]? ").lower()
    print()
    if take == "y":
        temp_card = None
        while True:
            place_row = input(">> What row do you want to place this card [0-1]? ")
            place_column = input(f">> What column do you want to place this card [0-{player_hand.width - 1}]? ")
            if not place_row.isdigit() or not place_column.isdigit() or not (0 <= int(place_row) <= 1) or not (0 <= int(place_column) <= player_hand.width - 1):
                print("Invalid input, try again.")
                continue
            else:
                temp_card = player_hand.cards[int(place_row)][int(place_column)]
                player_hand.cards[int(place_row)][int(place_column)] = draw_card
                discard_pile.add_to_top(temp_card)
                break

    else:
        discard_pile.add_to_top(draw_card)
