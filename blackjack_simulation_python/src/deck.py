import random

class Deck:
    def __init__(self, ndecks=1, with_stop_token=True):
        self.ranks = ['A'] + [str(n) for n in range(2, 11)] + ['J', 'Q', 'K']
        self.suits = ['♠', '♥', '♦', '♣']
        self.ndecks = ndecks
        self.with_stop_token = with_stop_token
        self.build_deck()

    def build_deck(self):
        self.cards = [rank + suit for rank in self.ranks for suit in self.suits] * self.ndecks
        random.shuffle(self.cards)
        if self.with_stop_token:
            stop_index = min(max(2, int(random.gauss(len(self.cards) / 2, len(self.cards) / 8))), len(self.cards) - 1)
            self.cards.insert(stop_index, "Stop")

    def draw(self, ncards=1):
        drawn = []
        for _ in range(ncards):
            if not self.cards:
                self.build_deck()  # auto-reshuffle if empty
            card = self.cards.pop(0)
            if card == "Stop":
                self.build_deck()
                card = self.cards.pop(0)
            drawn.append(card)
        return drawn if ncards > 1 else drawn[0]

