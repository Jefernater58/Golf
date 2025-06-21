# Golf.py
![](https://hackatime-badge.hackclub.com/U091J0C0QSJ/Golf) ![](https://img.shields.io/github/created-at/Jefernater58/Golf) ![](https://img.shields.io/github/last-commit/Jefernater58/Golf)

Golf is a multiplayer card game in which every player competes to finish with the lowest score. Golf.py is a python command-line game where the user battles the computer in a game of virtual Golf! May the best golfer win!

## Install
1. Download `golf.py` from the [latest release](https://github.com/Jefernater58/Golf/releases/latest)
2. Install necessary modules `pip install tabulate termcolor`
3. Run with python `python3 golf.py`

## How to play
### The aim
In Golf.py, the aim is to finish the game with a lower score than the computer.

### The card game
1. In the card version of the game, each player is dealt 6 cards face down in two rows of 3.
2. Each player chooses 2 of their cards to turn over before the game starts.
3. In the middle of the table, there is a face-down draw pile, and a face-up discard pile. The discard pile starts with one card, and the draw pile has the rest.
4. Player 1 can choose whether to take the top card from the draw pile, or from the discard pile.
5. Player 1 can then choose whether to swap any of their cards with the chosen card, or place it ontop of the discard pile.
6. If the player swaps a card, the swapped card is placed on the discard pile.
7. Then, it's Player 2's turn. This repeats in a circle until a player has all cards face-up, at which point every player gets one more turn before the game ends.
8. The player with the lowest score wins.

### Golf.py
Golf.py is a command-line version of the Golf card game. The user is Player 1, the computer is Player 2.
1. First, the user is prompted to choose the coordinates of the two cards to flip over before the game starts.
2. Then, the game begins like normal.
3. Once either the computer or user has all cards face-up, the other player has one more turn, then the game will end.

### Scoring
- The score of a number card is equal to its rank, for example, 9 of Spades = 9 points
- The score of an Ace is one, for example, Ace of Diamonds = 1 point
- The score of any picture card, excluding a King, is ten. For example, Jack of Hearts = 10 points
- The score of a King is zero, for example, King of Spades = 0 points
- The score of a Joker is -2 points

If two cards of the same rank, excluding Jokers, are vertically adjacent, the total score for that column is 0.

#### Example
The score for the below hand is 12.
```
┌─────────────┬───────────────┬────────────────┐
│ 4 of Hearts │ 9 of Diamonds │ King of Hearts │
├─────────────┼───────────────┼────────────────┤
│    Joker    │  9 of Spades  │ Queen of Clubs │
└─────────────┴───────────────┴────────────────┘
     4-2=2       same rank, 0       0+10=10
```
