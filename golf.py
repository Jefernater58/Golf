# golf.py - Frederick Rayner
# https://github.com/Jefernater58/Golf

import random
import time
from termcolor import colored
import os
from tabulate import tabulate

HAND_SIZE = 6  # number of cards a player has. MUST BE EVEN!!!
TITLE_TEXT = colored("GOLF.PY - by Freddie Rayner", "yellow")

BOT_MAX_TAKE_THRESHOLD = 5  # highest score of a card the bot will pick up from the discard pile, if no better options
BOT_MAX_TAKE_EARLY_GAME_THRESHOLD = 6
BOT_MAX_LOSING_TAKE_THRESHOLD = 4
BOT_MIN_SWAP_DIFFERENCE = 3  # the minimum difference between a card and a card in the hand to swap them
BOT_MIN_SWAP_EARLY_GAME_DIFFERENCE = 5
BOT_EARLY_GAME_NUM_FACE_UP = 3  # the number of face-up cards consider it to be early game


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
        self.cards = (
                [Card("Spades", rank) for rank in range(1, 14)] + [Card("Hearts", rank) for rank in range(1, 14)] +
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
            if c1.rank == c2.rank and self.face_up[0][card] and self.face_up[1][card]:
                continue
            else:
                score += c1.score if self.face_up[0][card] else 0
                score += c2.score if self.face_up[1][card] else 0
        return score

    def get_num_face_up(self):
        total = 0
        for row in range(2):
            for card in self.face_up[row]:
                total += 1 if card else 0

        return total


class Computer:
    def __init__(self, hand, skill):
        self.hand = hand
        self.skill = skill

    def initialise_hand(self):
        self.hand.face_up[0][0] = True
        self.hand.face_up[1][2] = True

    def best_move(self, card, losing):
        place_position = -1, -1

        best_difference = 0
        match_found = False
        for i in range(self.hand.width):
            card_1, card_2 = self.hand.cards[0][i], self.hand.cards[1][i]
            face_up_1, face_up_2 = self.hand.face_up[0][i], self.hand.face_up[1][i]

            if (face_up_1 and face_up_2 and card_2.rank != card_1.rank) or not face_up_1 or not face_up_2:
                # check if the card on the discard pile has the same rank as a card in the computer's hand
                if face_up_1 and card_1.rank == card.rank:
                    # take from discard pile, put in card_2s position
                    place_position = 1, i
                    match_found = True
                    break
                elif face_up_2 and card_2.rank == card.rank:
                    # take from discard pile, put in card_1s position
                    place_position = 0, i
                    match_found = True
                    break

                # take from the discard pile if the score is lower than a current card
                if face_up_1 and card.score < card_1.score:
                    # take from discard pile, put in card_1s position
                    if card_1.score - card.score > best_difference:
                        best_difference = card_1.score - card.score
                        place_position = 0, i
                elif face_up_2 and card.score < card_2.score:
                    # take from discard pile, put in card_2s position
                    if card_2.score - card.score > best_difference:
                        best_difference = card_2.score - card.score
                        place_position = 1, i
                else:
                    continue

        print(card.create_string(), place_position, best_difference, match_found)

        face_up_cards = self.hand.get_num_face_up()
        swap_difference = BOT_MIN_SWAP_DIFFERENCE if face_up_cards > BOT_EARLY_GAME_NUM_FACE_UP else BOT_MIN_SWAP_EARLY_GAME_DIFFERENCE
        if not match_found and best_difference < swap_difference:
            place_position = -1, -1

        max_take = (BOT_MAX_LOSING_TAKE_THRESHOLD if losing else BOT_MAX_TAKE_THRESHOLD) if face_up_cards > BOT_EARLY_GAME_NUM_FACE_UP else BOT_MAX_TAKE_EARLY_GAME_THRESHOLD
        if place_position == (-1, -1) and card.score <= max_take:  # no good option found yet
            for i in range(len(self.hand.face_up)):
                for j in range(len(self.hand.face_up[i])):
                    # take from the discard pile if the score is below threshold
                    if not self.hand.face_up[i][j]:
                        place_position = (i, j)

        return place_position

    def calculate_turn(self, player_h, discard_p, draw_p):
        current_score = self.hand.calculate_score()
        current_player_score = player_h.calculate_score()

        losing = current_score < current_player_score  # oh no! let's play more carefully because i dont wanna lose

        taking_card = True

        place_position = self.best_move(discard_p.cards[0], losing)
        if place_position != (-1, -1):
            take_pile = 1

        else:
            # take from the draw pile
            take_pile = 0

            place_position = self.best_move(draw_p.cards[0], losing)

            if place_position == (-1, -1):
                taking_card = False

        return take_pile, place_position, taking_card


# get an input as an int and check it is between two values
def input_range(message, int_min, int_max):
    while True:
        answer = input(message)
        if not answer.isdigit() or not (int_min <= int(answer) <= int_max):
            print("Invalid input, try again.")
        else:
            return int(answer)


# clear all text from the console
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def render_game_state():
    # make it pretty :)
    clear_console()
    print(TITLE_TEXT + "\n")

    # render the current state of the game (decks, hands)
    draw_pile_render = tabulate([[draw_pile.create_top_card_string()]], tablefmt="simple_grid",
                                stralign="center").splitlines()
    discard_pile_render = tabulate([[discard_pile.create_top_card_string()]], tablefmt="simple_grid",
                                   stralign="center").splitlines()
    print(f"DRAW PILE ({draw_pile.get_size()} cards)    " + colored(f"DISCARD PILE ({discard_pile.get_size()})",
                                                                    "dark_grey"))

    for line in range(len(draw_pile_render)):
        print(draw_pile_render[line].ljust(len(f"DRAW PILE ({draw_pile.get_size()} cards)    ")) + colored(
            discard_pile_render[line], "dark_grey"))

    player_hand_render = player_hand.render()
    computer_hand_render = computer.hand.render()

    print(
        colored("\n YOUR CARDS", "white").ljust(len(player_hand_render[0]) + 13) + colored(" COMPUTER'S CARDS", "blue"))
    for line in range(len(player_hand_render)):
        print(colored(player_hand_render[line], "white") + "    " + colored(computer_hand_render[line], "blue"))

    print()


# create and initialise the draw pile and discard pile
draw_pile = Pile(True)
draw_pile.fill_deck()
draw_pile.shuffle()

discard_pile = Pile(False)
discard_pile.append_card(draw_pile.remove_top())

# print some stuff :)
clear_console()
print(TITLE_TEXT)
input("\nWelcome Human. Are you ready to play? ")
print()

# create the player hand and flip over 2 cards
player_hand = Hand(draw_pile)

print("Before the game starts, you must turn over two cards. Please enter the row and column of the first card.")
turn_row_1 = input_range(">> Row [0-1]: ", 0, 1)
turn_column_1 = input_range(f">> Column [0-{player_hand.width - 1}]: ", 0, player_hand.width - 1)

print("Now please enter the row and column of the second card.")
while True:
    turn_row_2 = input_range(">> Row [0-1]: ", 0, 1)
    turn_column_2 = input_range(f">> Column [0-{player_hand.width - 1}]: ", 0, player_hand.width - 1)
    if turn_row_2 == turn_row_1 and turn_column_2 == turn_column_1:
        print("A different card must be selected. Please try again.")
    else:
        break

player_hand.face_up[turn_row_1][turn_column_1] = True
player_hand.face_up[turn_row_2][turn_column_2] = True

# create and initialise the bot
# i need to make skill levels for dumb players
computer = Computer(Hand(draw_pile), 0)
computer.initialise_hand()

# main loop
game_over = False
while not game_over:
    render_game_state()

    # the player chooses which pile to take from
    # we need to check the pile isn't empty!
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

    print(colored(f"\nYou drew: {draw_card.create_string()}", "green"))

    take = input(">> Do you want this card [y/n]? ").lower()
    print()
    if take == "y":
        # replace the card in their hand with the card they picked up
        print("Please enter the row and column to place this card.")
        place_row = input_range(">> Row [0-1]: ", 0, 1)
        place_column = input_range(f">> Column [0-{player_hand.width - 1}]: ", 0, player_hand.width - 1)

        # place the old card on the discard pile
        temp_card = player_hand.cards[place_row][place_column]
        player_hand.cards[place_row][place_column] = draw_card
        player_hand.face_up[place_row][place_column] = True
        discard_pile.add_to_top(temp_card)

    else:
        discard_pile.add_to_top(draw_card)

    render_game_state()

    # computer's go now!
    print("[COMPUTER] Its my turn now!")
    computer_turn = computer.calculate_turn(player_hand, discard_pile, draw_pile)
    time.sleep(1)
    print("[COMPUTER] hmmm...")
    time.sleep(2)
    if computer_turn[0] == 0:
        print("[COMPUTER] I'll take my chances with the draw pile.")
        computer_take_card = draw_pile.remove_top()
    else:
        print("[COMPUTER] I'll take this card from the discard pile.")
        computer_take_card = discard_pile.remove_top()
    time.sleep(3)
    if not computer_turn[2]:
        print("[COMPUTER] I don't want this card, I'll put it on the discard pile.")
        discard_pile.add_to_top(computer_take_card)
    else:
        r, c = computer_turn[1]
        print(f"[COMPUTER] Ok, I'll take this card and put it on row {r}, column {c}")
        discard_pile.add_to_top(computer.hand.cards[r][c])
        computer.hand.cards[r][c] = computer_take_card
        computer.hand.face_up[r][c] = True

    input("\n>> Press [RETURN] to continue: ")
