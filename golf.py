# golf.py - Frederick Rayner
# https://github.com/Jefernater58/Golf

import random
import time
from termcolor import colored
import random
import os
from tabulate import tabulate

HAND_SIZE = 6  # number of cards a player has. Max 26. MUST BE EVEN!!!
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
TITLE_TEXT = colored("GOLF.PY - by Freddie Rayner", "yellow")

BOT_ACCEPTABLE_SCORE_FACE_UP_DIFFERENCE = 3
BOT_ACCEPTABLE_SCORE_FACE_DOWN_DIFFERENCE = 0
BOT_ACCEPTABLE_SCORE_EARLY_GAME_DIFFERENCE = -4
BOT_EARLY_GAME_NUM_FACE_UP = 3


class Card:
    def __init__(self, suit, rank=-1):
        self.suit = suit
        self.rank = rank

        self.score = -1
        if suit == "Joker":
            self.score = -2
        elif 1 <= rank <= 10:
            self.score = rank
        elif rank <= 12:
            self.score = 10
        elif rank == 13:
            self.score = 0
        else:
            print(f"error: card rank is invalid: {self.rank}, {self.suit}")

    def create_string(self, hidden=False):
        colour = "white"
        if not hidden:
            if self.suit in ("Diamonds", "Hearts"):
                colour = "red"
            else:
                colour = "dark_grey"

        if hidden:
            return (colored("┏━━━━━━━━━━━┓\n", colour) +
                    colored("┃░░░░░░░░░░░┃\n", colour) +
                    colored("┃░░░░░░░░░░░┃\n", colour) +
                    colored("┃░░░░░░░░░░░┃\n", colour) +
                    colored("┃░░░░░░░░░░░┃\n", colour) +
                    colored("┃░░░░░░░░░░░┃\n", colour) +
                    colored("┃░░░░░░░░░░░┃\n", colour) +
                    colored("┃░░░░░░░░░░░┃\n", colour) +
                    colored("┗━━━━━━━━━━━┛", colour))

        if self.suit == "Joker":
            name_string = "Joker"
            suit_string = ""
        else:
            ranks = {1: "A", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
                     11: "J", 12: "Q", 13: "K"}
            name_string = ranks[self.rank]

            suits = {"Spades": "♠", "Hearts": "♥", "Diamonds": "♦", "Clubs": "♣"}

            suit_string = suits[self.suit]

        return (colored("┏━━━━━━━━━━━┓\n", colour) +
                colored(f"┃{name_string.ljust(11)}┃\n", colour) +
                colored("┃           ┃\n", colour) +
                colored("┃           ┃\n", colour) +
                colored(f"┃{suit_string.center(11)}┃\n", colour) +
                colored("┃           ┃\n", colour) +
                colored("┃           ┃\n", colour) +
                colored(f"┃{name_string.rjust(11)}┃\n", colour) +
                colored("┗━━━━━━━━━━━┛", colour))


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
            return self.cards[0].create_string(self.hidden)
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
        render_array = [["" for _ in range(self.width + 1)] for _ in range(2)]
        for row in range(2):
            render_array[row][0] = "\n\n\n\n" + colored(str(row + 1), "white")
            for card in range(self.width):
                render_array[row][card + 1] = self.cards[row][card].create_string(not self.face_up[row][card])

        return tabulate(render_array, tablefmt="plain", stralign="center", headers=[ALPHABET[i] for i in range(self.width)]).splitlines()

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

    def calculate_turn(self, player_h, discard_p, draw_p):
        current_score = self.hand.calculate_score()
        current_player_score = player_h.calculate_score()

        losing = current_score < current_player_score

        possible_moves = []  # (take_pile, place_position, score_difference, replaces_face_up)

        # find the move with the lowest score from the discard pile
        discard_pile_top = discard_p.cards[0]
        initial_score = self.hand.calculate_score()
        for i in range(2):
            for j in range(self.hand.width):
                temp_c = self.hand.cards[i][j]
                self.hand.cards[i][j] = discard_pile_top
                temp_face_up = self.hand.face_up[i][j]
                self.hand.face_up[i][j] = True
                score_difference = initial_score - self.hand.calculate_score()
                self.hand.face_up[i][j] = temp_face_up
                self.hand.cards[i][j] = temp_c
                possible_moves.append((1, (i, j), score_difference, self.hand.face_up[i][j]))

        # remove all the bad ones
        best_face_up_moves = []
        best_face_down_moves = []
        highest_face_up_difference = 0  # i dont wanna replace a face-up card with a higher card
        highest_face_down_difference = -999
        for move in possible_moves:
            if move[3]:
                if move[2] > highest_face_up_difference:
                    best_face_up_moves = [move]
                    highest_face_up_difference = move[2]
                elif move[2] == highest_face_up_difference:
                    best_face_up_moves.append(move)
            else:
                if move[2] > highest_face_down_difference:
                    best_face_down_moves = [move]
                    highest_face_down_difference = move[2]
                elif move[2] == highest_face_down_difference:
                    best_face_down_moves.append(move)

        if highest_face_down_difference >= BOT_ACCEPTABLE_SCORE_FACE_DOWN_DIFFERENCE:
            chosen_move = random.choice(best_face_down_moves)
            return chosen_move[0], chosen_move[1], True
        elif highest_face_up_difference >= BOT_ACCEPTABLE_SCORE_FACE_UP_DIFFERENCE:
            chosen_move = random.choice(best_face_up_moves)
            return chosen_move[0], chosen_move[1], True

        # now lets do the same for the draw pile!
        possible_moves = []  # (take_pile, place_position, score_difference, replaces_face_up)

        # find the move with the lowest score from the discard pile
        draw_pile_top = draw_p.cards[0]
        initial_score = self.hand.calculate_score()
        for i in range(2):
            for j in range(self.hand.width):
                temp_c = self.hand.cards[i][j]
                self.hand.cards[i][j] = draw_pile_top
                temp_face_up = self.hand.face_up[i][j]
                self.hand.face_up[i][j] = True
                score_difference = initial_score - self.hand.calculate_score()
                self.hand.face_up[i][j] = temp_face_up
                self.hand.cards[i][j] = temp_c
                possible_moves.append((0, (i, j), score_difference, self.hand.face_up[i][j]))

        # remove all the bad ones
        best_face_up_moves = []
        best_face_down_moves = []
        highest_face_up_difference = 0  # i dont wanna replace a face-up card with a higher card
        highest_face_down_difference = -999
        for move in possible_moves:
            if move[3]:
                if move[2] > highest_face_up_difference:
                    best_face_up_moves = [move]
                    highest_face_up_difference = move[2]
                elif move[2] == highest_face_up_difference:
                    best_face_up_moves.append(move)
            else:
                if move[2] > highest_face_down_difference:
                    best_face_down_moves = [move]
                    highest_face_down_difference = move[2]
                elif move[2] == highest_face_down_difference:
                    best_face_down_moves.append(move)

        early_game = self.hand.get_num_face_up() <= BOT_EARLY_GAME_NUM_FACE_UP
        if (early_game and highest_face_down_difference > BOT_ACCEPTABLE_SCORE_EARLY_GAME_DIFFERENCE) or highest_face_down_difference >= BOT_ACCEPTABLE_SCORE_FACE_DOWN_DIFFERENCE:
            chosen_move = random.choice(best_face_down_moves)
            return chosen_move[0], chosen_move[1], True
        elif highest_face_up_difference >= BOT_ACCEPTABLE_SCORE_FACE_UP_DIFFERENCE:
            chosen_move = random.choice(best_face_up_moves)
            return chosen_move[0], chosen_move[1], True
        else:
            return 0, (0, 0), False


# get an input as an int and check it is between two values
def input_range(message, int_min, int_max):
    while True:
        answer = input(message)
        if not answer.isdigit() or not (int_min <= int(answer) <= int_max):
            print("Invalid input, try again.")
        else:
            return int(answer)


def input_2d(message, row_max, col_max):
    while True:
        answer = input(message)
        if answer[0].upper() not in ALPHABET:
            print("Invalid input, try again.")
            continue
        answer_col = ALPHABET.index(answer[0].upper())
        if not answer[1].isdigit():
            print("Invalid input, try again.")
            continue
        answer_row = int(answer[1]) - 1

        if not (0 <= answer_row <= row_max) or not (0 <= answer_col < col_max):
            print("Invalid input, try again.")
            continue

        return answer_row, answer_col
    return None


# clear all text from the console
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def render_game_state():
    # make it pretty :)
    clear_console()

    player_hand_render = player_hand.render()
    computer_hand_render = computer.hand.render()

    print(colored("\n YOUR CARDS", "white").ljust(len(player_hand_render[1]) + 2) + colored(" COMPUTER'S CARDS\n", "blue"))
    for line in range(len(player_hand_render)):
        print(player_hand_render[line] + ("        " if line != 0 else "              ") + computer_hand_render[line])

    print("\033[0m\n")


def render_piles():
    print(colored(f"DRAW PILE ({draw_pile.get_size()} cards)          DISCARD PILE ({discard_pile.get_size()} cards)", "white"))
    print(tabulate([[draw_pile.create_top_card_string().replace("\n", "               \n"),
                     discard_pile.create_top_card_string()]], tablefmt="plain"))
    print("\033[0m\n")


# create and initialise the draw pile and discard pile
draw_pile = Pile(True)
draw_pile.fill_deck()
draw_pile.shuffle()

discard_pile = Pile(False)
discard_pile.append_card(draw_pile.remove_top())

# print some stuff :)
clear_console()
print(TITLE_TEXT)
input("\nWelcome Human. Are you ready to play? Press [RETURN] to start: ")
print()

# create the player hand
player_hand = Hand(draw_pile)

# create and initialise the bot
# i need to make skill levels for dumb players
computer = Computer(Hand(draw_pile), 0)
computer.initialise_hand()

render_game_state()

print("Before the game starts, you must turn over two cards.")
turn_row_1, turn_column_1 = input_2d(">> Enter the position of the first card, (e.g., A1): ", 1, player_hand.width)
player_hand.face_up[turn_row_1][turn_column_1] = True

render_game_state()
print("Before the game starts, you must turn over two cards.")
while True:
    turn_row_2, turn_column_2 = input_2d(">> Enter the position of the second card, (e.g., B2): ", 1, player_hand.width)
    if turn_row_2 == turn_row_1 and turn_column_2 == turn_column_1:
        print("A different card must be selected. Please try again.")
    else:
        break

player_hand.face_up[turn_row_2][turn_column_2] = True

# main loop
game_over = False
while True:
    render_game_state()
    render_piles()

    # the player chooses which pile to take from
    # we need to check the pile isn't empty!
    if game_over:
        print(colored("All of the computer's cards are now face-up! The game will end after this turn.", "red"))
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

    render_game_state()
    print(colored(f"You drew:\n{draw_card.create_string()}\n", "green"))

    while True:
        take = input(">> Do you want to take this card [y/n]? ").lower()
        if take == "y" or take == "n":
            break
        print("Invalid input, try again")
    print()
    if take == "y":
        # replace the card in their hand with the card they picked up
        place_row, place_column = input_2d(">> Enter the position to place this card (e.g., A1): ", 1, player_hand.width)

        # place the old card on the discard pile
        temp_card = player_hand.cards[place_row][place_column]
        player_hand.cards[place_row][place_column] = draw_card
        player_hand.face_up[place_row][place_column] = True
        discard_pile.add_to_top(temp_card)

    else:
        discard_pile.add_to_top(draw_card)

    render_game_state()
    render_piles()

    if game_over:
        break
    if player_hand.get_num_face_up() == HAND_SIZE:
        print(colored("All your cards are now face-up! The game will end after the computer's last turn.", "red"))
        game_over = True

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
        print(f"[COMPUTER] Ok, I'll take this card and place it at {ALPHABET[c]}{r + 1}")
        discard_pile.add_to_top(computer.hand.cards[r][c])
        computer.hand.cards[r][c] = computer_take_card
        computer.hand.face_up[r][c] = True

    input("\n>> Press [RETURN] to continue: ")

    if game_over:
        break
    if computer.hand.get_num_face_up() == HAND_SIZE:
        game_over = True

for row in range(2):
    for column in range(player_hand.width):
        player_hand.face_up[row][column] = True
        computer.hand.face_up[row][column] = True

render_game_state()

player_score = player_hand.calculate_score()
computer_score = computer.hand.calculate_score()

input(">> The game has ended! Press [RETURN] to see the results: ")

print(f"\nYou scored {player_score}")
print(colored(f"The computer scored {computer_score}\n", "blue"))

if player_score < computer_score:
    print(colored("YOU WIN", "green"))
elif computer_score < player_score:
    print(colored("YOU LOSE", "red"))
else:
    print("DRAW", "yellow")

print()
