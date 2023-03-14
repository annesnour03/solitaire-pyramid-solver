import sys
import time
from collections import deque
from constants import *
from dataclasses import dataclass
from termcolor import colored
from copy import deepcopy


@dataclass
class Pair:
    first: tuple[int, int]
    second: tuple[int, int]

    def __eq__(self, __o) -> bool:
        if isinstance(__o, Pair):
            if self.first == __o.first and self.second == __o.second:
                return True
            return self.first == __o.second and self.second == __o.first
        return False


class Move():
    MATCH = "Match {} {}"
    MATCH_WITH_NEW_STACK = "Match with use of new stack: {} {}"
    MATCH_WITH_DISCARD_STACK = "Match with use of discard stack: {} {}"
    MATCH_CARDS_STACK = "Match {} {} on the stacks"

    POP_KING_NEW_STACK = "Pop king from new stack"
    POP_KING_DISCARD_STACK = "Pop king from discard stack"
    POP_KING_PYRAMID = "Pop king from pyramid"

    REMOVE_TOP_CARD = "Remove top of stack"
    RESET = "Reset the stacks"


class Card:
    rank: int
    suite: str
    value: int

    def __init__(self, value) -> None:
        self.rank = value[0]
        self.suite = value[1]
        self.value = RANKS.index(self.rank) + 1

    @staticmethod
    def counter_part(value: int):
        return KING - value

    def is_counter_part(self, __o) -> bool:
        if __o == None:
            return self.value == KING
        return self.value + __o.value == KING

    def __hash__(self) -> int:
        return self.value + ord(self.suite)

    def __str__(self) -> str:
        symbol: str = ''
        match self.suite.upper():
            case 'S':
                symbol = SPADE
            case 'D':
                symbol = DIAMOND
            case 'C':
                symbol = CLUB
            case 'H':
                symbol = HEART

        return str(self.rank) + symbol

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Card):
            return self.value == __o.value and self.suite == __o.suite
        return self.value == __o

    def __repr__(self) -> str:
        return str(self)


class Pyramid:
    cards: list[list[Card | None]] = []
    new_stack: list[Card] = []
    discard_stack: list[Card] = []
    remaining_deck_flips: int = 3

    @property
    def top_new_stack(self) -> Card | None:
        if not self.new_stack:
            return
        return self.new_stack[0]

    @property
    def top_discard_stack(self) -> Card | None:
        if not self.discard_stack:
            return
        return self.discard_stack[0]

    def __eq__(self, __o: object) -> bool:
        return hash(self) == hash(__o)

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        self.__dict__['discard_stack'] = deepcopy(self.discard_stack)
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def __hash__(self) -> int:
        return sum([hash(a) for e in self.cards for a in e]) + \
            sum(hash(e) for e in self.new_stack) + 1

    def load_from_file(self, path_to_file: str) -> None:
        all_values: list[Card] = list(
            map(Card, open(path_to_file, 'r').readline().split()))
        pyramid: list[Card] = all_values[0:28]
        self.new_stack: list[Card] = all_values[28:]
        start_indexes: list[int] = [n_th_triangle(n) for n in range(HEIGHT)]
        spl: list[list[Card]] = [pyramid[st:st+idx + 1]
                                 for idx, st in enumerate(start_indexes)]
        self.cards = spl

    def get_free_idx(self) -> list[tuple[int, int]]:
        res: list[tuple[int, int]] = []
        for idx, row in enumerate(self.cards):
            if idx == HEIGHT - 1:
                res = res + [(last, idx) for last in range(HEIGHT)
                             if self.cards[idx][last] != None]
                break
            for i in range(idx + 1):
                if self.cards[idx][i] == None:
                    continue
                if self.cards[idx + 1][i] == None and self.cards[idx + 1][i + 1] == None:
                    res.append((i, idx))
        return res

    def get_matches_card(self, card=None) -> list[tuple[int, int]]:
        free_indexes: list[tuple[int, int]] = self.get_free_idx()
        res: list[tuple[int, int]] = []
        for (x, y) in free_indexes:
            if self.cards[y][x].is_counter_part(card):  # type: ignore
                res.append((x, y))
        return res

    def get_matches_in_pyramid(self) -> list[Pair]:
        free_indexes: list[tuple[int, int]] = self.get_free_idx()
        values: list[Card] = [self.cards[y][x]
                              for (x, y) in free_indexes]  # type: ignore
        converted_values: list[int] = list(map(lambda x: x.value, values))
        res: list[Pair] = []
        for idx, value in enumerate(converted_values):
            counter_part: int = Card.counter_part(value)
            try:
                counter_idx: int = converted_values.index(counter_part)
                created: Pair = Pair(
                    free_indexes[counter_idx], free_indexes[idx])
                if created not in res:
                    res.append(created)
            except ValueError:
                pass

        return res

    def get_open_kings(self):
        free_indexes: list[tuple[int, int]] = self.get_free_idx()
        values: list[Card] = [self.cards[y][x]
                              for (x, y) in free_indexes]  # type: ignore
        converted_values: list[int] = list(map(lambda x: x.value, values))
        res: list[tuple[int, int]] = []
        for idx, card in enumerate(converted_values):
            if card is KING:
                res.append(free_indexes[idx])
        return res

    def get_match_in_stack(self) -> bool:
        # If there is a match in new stack + old stack, we return true
        if not self.new_stack:
            return False
        return Card.counter_part(self.top_new_stack.value) == self.top_discard_stack

    def get_match_stacks_pyramid(self, stack) -> list[tuple[int, int]]:
        free_indexes: list[tuple[int, int]] = self.get_free_idx()
        values: list[Card] = [self.cards[y][x]
                              for (x, y) in free_indexes]  # type: ignore
        converted_values: list[int] = list(map(lambda x: x.value, values))
        res: list[tuple[int, int]] = []
        for idx, value in enumerate(converted_values):
            counter_part: int = Card.counter_part(value)
            if stack == counter_part:
                res.append(free_indexes[idx])
        return res

    def get_match_new_pyramid(self) -> list[tuple[int, int]]:
        return self.get_match_stacks_pyramid(self.top_new_stack)

    def get_match_disc_pyramid(self) -> list[tuple[int, int]]:
        return self.get_match_stacks_pyramid(self.top_discard_stack)

    @property
    def is_complete(self) -> bool:
        for row in self.cards:
            if None not in row:
                return False
        return True

    def match(self, pair: Pair) -> None:
        self.cards[pair.first[1]][pair.first[0]] = None
        self.cards[pair.second[1]][pair.second[0]] = None

    def move_top_stock(self) -> None:
        new: Card = self.new_stack.pop(0)
        assert(new not in self.discard_stack)
        self.discard_stack.insert(0, new)
        assert(new not in self.new_stack)

    def flip_decks(self) -> None:
        if self.remaining_deck_flips > 0:
            self.new_stack, self.discard_stack = self.discard_stack[::-
                                                                    1], self.new_stack
            self.remaining_deck_flips -= 1
        else:
            raise Exception("No more flips left...")

    def solve(self,verbose=True) -> list[str] | None:
        """
        This function is the heart of the pyramid class.
        It solves a given instance of the game, by preforming a BFS search for
        the winning game state.

        A few optimalisations were made in order to minimise the width of the search.
        For example, whenever we see a king, there is no better option than to remove it,
        so that is the only possibility considered.

        It also keeps track of previous positions, by hashing the gamestate instances
        and keeping them in a dict. This way we don't do double calculations, which improved performance
        by a lot.
        """
        res: deque[MovePyramid] = deque()
        new = deepcopy(self)
        res.append(MovePyramid(new, []))
        seen: dict[Pyramid, bool] = dict()
        while res:
            tmp: MovePyramid = res.popleft()
            pyr: Pyramid = tmp.pyr
            log: list[str] = tmp.move

            # It is nice to see what the program is trying out, remove to increase performance
            if verbose:
                print(pyr)
            if pyr in seen:
                continue
            seen[pyr] = True

            if pyr.is_complete:
                return log
            open_kings = pyr.get_open_kings()
            if open_kings:
                moved = deepcopy(pyr)
                new_log = deepcopy(log)
                for match in open_kings:
                    moved.cards[match[1]][match[0]] = None
                    new_log.append(Move.POP_KING_PYRAMID)
                res.append(MovePyramid(moved, new_log))
                continue
            # Simply remove the king
            if pyr.top_new_stack == KING:
                moved = deepcopy(pyr)
                new_log = deepcopy(log)
                moved.new_stack.pop(0)
                new_log.append(Move.POP_KING_NEW_STACK)
                res.append(MovePyramid(moved, new_log))
                continue
            # Simply remove the king
            if pyr.top_discard_stack == KING:
                moved = deepcopy(pyr)
                new_log = deepcopy(log)
                moved.discard_stack.pop(0)
                new_log.append(Move.POP_KING_DISCARD_STACK)
                res.append(MovePyramid(moved, new_log))
                continue
            # con = False  # For a complete search this needs to be disabled
            for match in pyr.get_matches_in_pyramid():
                # Try all possible matches in pyramid
                moved = deepcopy(pyr)
                new_log = deepcopy(log)
                first: Card | None = moved.cards[match.first[1]
                                                 ][match.first[0]]
                second: Card | None = moved.cards[match.second[1]
                                                  ][match.second[0]]
                moved.match(match)
                new_log.append(Move.MATCH.format(first, second))
                res.append(MovePyramid(moved, new_log))
                # con = True
            # if con:
                # continue
            if pyr.get_match_in_stack():
                moved = deepcopy(pyr)
                new_log = deepcopy(log)

                new_removed = moved.new_stack.pop(0)
                disc_removed: Card = moved.discard_stack.pop(0)
                new_log.append(Move.MATCH_CARDS_STACK.format(
                    new_removed, disc_removed))
                res.append(MovePyramid(moved, new_log))
            for pos in pyr.get_match_new_pyramid():
                moved = deepcopy(pyr)
                new_log = deepcopy(log)
                new_removed: Card = moved.new_stack.pop(0)
                pyr_removed: Card | None = moved.cards[pos[1]][pos[0]]
                moved.cards[pos[1]][pos[0]] = None
                new_log.append(Move.MATCH_WITH_NEW_STACK.format(
                    new_removed, pyr_removed))
                res.append(MovePyramid(moved, new_log))

            for pos in pyr.get_match_disc_pyramid():
                moved = deepcopy(pyr)
                new_log = deepcopy(log)
                new_removed = moved.discard_stack.pop(0)
                pyr_removed = moved.cards[pos[1]][pos[0]]
                moved.cards[pos[1]][pos[0]] = None
                new_log.append(Move.MATCH_WITH_DISCARD_STACK.format(
                    new_removed, pyr_removed))
                res.append(MovePyramid(moved, new_log))

            if len(pyr.new_stack) > 0:
                # We just simply move it over.
                moved: Pyramid = deepcopy(pyr)
                new_log: list[str] = deepcopy(log)
                moved.move_top_stock()

                new_log.append(Move.REMOVE_TOP_CARD)
                res.append(MovePyramid(moved, new_log))
            if len(pyr.new_stack) == 0 and pyr.remaining_deck_flips > 0:
                moved = deepcopy(pyr)
                new_log = deepcopy(log)

                moved.flip_decks()
                new_log.append(Move.RESET)
                res.append(MovePyramid(moved, new_log))

    def __str__(self) -> str:
        spaces = 6
        for i in self.cards:
            for idx, card in enumerate(i):
                if not idx:
                    for _ in range(spaces):
                        print(' ', end='')
                if card == None:
                    print('0⍟', end=' ')
                else:
                    print(card, end=' ')
            print()
            spaces -= 1
        return ''

    def __repr__(self) -> str:
        return str(self)


@dataclass
class MovePyramid:
    pyr: Pyramid
    move: list[str]

    def __iter__(self):
        yield self.pyr
        yield self.move


def n_th_triangle(n: int) -> int:
    return n * (n + 1) // 2


def print_log(logs: list[str]):
    for num, log in enumerate(logs):
        print(f"{num + 1}. ", end='')
        for char in log:
            if char == DIAMOND or char == HEART:
                print(colored(char, 'red'), end='')
            else:
                print(char, end='')

        print()


def main():
    argv: list[str] = sys.argv[1:]
    case: str = argv[0]
    pyr: Pyramid = Pyramid()
    pyr.load_from_file(case)
    t0: float = time.time()
    result: list[str] | None = pyr.solve()

    if result:
        print_log(result)
    else:
        print("No result found!")
    print("time taken: ", "\x1b[2;30;42m", time.time() - t0, "\x1b[0m")


if __name__ == "__main__":
    main()
