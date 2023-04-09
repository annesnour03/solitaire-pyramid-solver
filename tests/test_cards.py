from pyramid import Card
from constants import RANKS


class TestCards:
    def setup_class(self):
        self.all_cards = []
        suites = ["S", "C", "H", "D"]
        for rank in RANKS:
            for suite in suites:
                self.all_cards.append(Card((rank, suite)))
        assert len(self.all_cards) == 52

    def test_create_simple(self):
        card = Card(("K", "S"))
        assert card.value == 13

    def test_cards_value(self):
        cards = [Card((val, "S")) for val in RANKS]
        for idx, card in enumerate(cards):
            assert card.value == idx + 1

    def test_case_card(self):
        card = Card(("A", "s"))
        card2 = Card(("A", "S"))
        card3 = Card(("a", "S"))
        assert card == card2 == card3

    def test_all_different_hash_card(self):
        hashed_cards = list(map(lambda x: hash(x), self.all_cards))
        assert len(hashed_cards) == len(set(hashed_cards))
