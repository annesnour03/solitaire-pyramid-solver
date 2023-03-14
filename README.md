# Pyramid Solver

This program tries to find a solution for the pyramid solitaire game. It works with any version, but is build with [Microsoft's game](https://play.google.com/store/apps/details?id=com.microsoft.microsoftsolitairecollection&hl=nl&gl=US) on mobile in mind.

## Usage

You can run the program by running `python3 pyramid.py cases/simple.input`. The content of the input file need to be in a specific format. The first 28 cards are the cards in the pyramid, from top to bottom, left to right.
The rest of the cards, are the cards that are present in the initial stack.

Example:
```
KH QH AH JH 2H TH 3H 9H 4H 8H 5H 6H 7H 5S 8S 4S 9S 3S TS 2S JS QS AS 6S 7S KS KD KC
2D QD 7C JC 3D 9C 5C 4D AD 3C 2C 9D 8D 6C 7D 4C QC 5D AC 8C TC JD TD 6D

```
Here the seperation of pyramid and stack cards is seperated by a newline for readability.

The program will try to find a solution using BFS. If it finds a solution, it would look something like this:
```
1. Pop king from pyramid
2. Pop king from pyramid
3. Pop king from pyramid
4. Match J♠ 2♠
5. Match A♠ Q♠
6. Match 7♠ 6♠
7. Match 9♠ 4♠
8. Match T♠ 3♠
9. Match 7♥ 6♥
10. Match 8♠ 5♠
11. Match 4♥ 9♥
12. Match 5♥ 8♥
13. Match 3♥ T♥
14. Match 2♥ J♥
15. Match A♥ Q♥
16. Pop king from pyramid
```

During the calculation the current state of the board is being printed out. If you want to disable this, you need to call the solve function with `solve(verbose=False)`

## Future
- Increase speed of the algorithm
    - Representing state in bytes instead of full classes
- Explore more paths in order to be able to always solve the most difficult variants of the game.