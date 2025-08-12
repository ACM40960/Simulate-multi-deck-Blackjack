import re

class Hand:
    def __init__(self):
        self.cards = []

    def get(self, card):
        self.cards.append(card)

    def clear(self):
        self.cards = []

    def score(self, first_card_only=False):
        cards = self.cards[:1] if first_card_only else self.cards
        values = [self.card_value(c) for c in cards]
        total = sum(values)
        aces = sum(1 for c in cards if c.startswith('A'))
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def is_hard(self):
        total = sum(self.card_value(c) for c in self.cards)
        aces = sum(1 for c in self.cards if c.startswith('A'))
        return not (total <= 11 and aces > 0)

    def can_split(self):
        if len(self.cards) != 2:
            return False
        stripped = [re.sub(r'[^\dA]', '', c) for c in self.cards]
        return stripped[0] == stripped[1]

    def split(self):
        if not self.can_split():
            raise ValueError("Cannot split this hand.")
        h1 = Hand()
        h2 = Hand()
        h1.get(self.cards[0])
        h2.get(self.cards[1])
        return h1, h2

    def card_value(self, card):
        rank = re.sub(r'[^\dA-Z]', '', card)
        if rank == 'A':
            return 11
        elif rank in ['J', 'Q', 'K']:
            return 10
        else:
            return int(rank)
