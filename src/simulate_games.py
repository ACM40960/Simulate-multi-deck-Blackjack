import argparse
import os
from dataclasses import dataclass
from typing import List, Optional
import pandas as pd
from tqdm import tqdm

from .deck import Deck
from .hand import Hand

# --- Config dataclass ---------------------------------------------------------
@dataclass
class SimConfig:
    ndecks: int = 8
    soft17hit: bool = True
    max_rows: int = 1_000_000          # total rows (not games) to write
    nb_hands: int = 3                  # number of player hands per deal (before splits)
    chunk_write: int = 50_000          # write to CSV every N rows
    out_csv: str = os.path.join("data", "blackjack_games.csv")


# --- Helpers -----------------------------------------------------------------
def dealer_should_hit(dealer: Hand, soft17hit: bool) -> bool:
    score = dealer.score()
    if score < 17:
        return True
    if score == 17 and (not dealer.is_hard()) and soft17hit:
        return True
    return False


def draw_one(deck: Deck) -> str:
    # handles stop-token rebuild internally
    c = deck.draw()
    return c


def init_hands(deck: Deck, dealer: Hand, hands: List[Hand]):
    # clear & deal two to each player hand and dealer
    for h in hands + [dealer]:
        h.clear()
        h.get(draw_one(deck))
        h.get(draw_one(deck))


def play_player_hand(deck: Deck, dealer: Hand, hand: Hand) -> pd.DataFrame:
    
    recs = []
    # initial state row (before first potential hit)
    rec = dict(
        score=hand.score(),
        score_dealer=dealer.score(first_card_only=True),
        hard=hand.is_hard(),
        score_if_hit=None,
        score_fin_dealer=None,  # filled after dealer plays
        game_id=None,           # set by caller
        hard_if_hit=None,       # filled when we actually hit
    )
    
    tmp_rows = []

    score = hand.score()
    # If already >=21, we will just return the single row 
    if score >= 21:
        tmp_rows.append(rec.copy())
        return pd.DataFrame(tmp_rows)

    while score < 21:
        
        card = draw_one(deck)
        hand.get(card)
        new_score = hand.score()
        rec2 = rec.copy()
        rec2["score_if_hit"] = new_score
        rec2["hard_if_hit"] = hand.is_hard()
        tmp_rows.append(rec2)

        # start a fresh potential state from the new score (in case we were to hit again)
        rec = dict(
            score=new_score,
            score_dealer=dealer.score(first_card_only=True),
            hard=hand.is_hard(),
            score_if_hit=None,
            score_fin_dealer=None,
            game_id=None,
            hard_if_hit=None,
        )
        score = new_score

    if not tmp_rows:
        tmp_rows.append(rec.copy())

    return pd.DataFrame(tmp_rows)


def play_dealer(deck: Deck, dealer: Hand, soft17hit: bool) -> int:
    while dealer_should_hit(dealer, soft17hit):
        dealer.get(draw_one(deck))
    return dealer.score()


# --- Main simulation ----------------------------------------------------------
def simulate(cfg: SimConfig):
    os.makedirs(os.path.dirname(cfg.out_csv), exist_ok=True)

    deck = Deck(ndecks=cfg.ndecks, with_stop_token=True)
    _ = deck.draw()  # burn one

    dealer = Hand()
    hands = [Hand() for _ in range(cfg.nb_hands)]

    rows = []
    game_id = 0
    pbar = tqdm(total=cfg.max_rows, desc="Simulating rows")
    while True:
        init_hands(deck, dealer, hands)

        #if a hand can split, split into two separate temp hands
        effective_hands: List[Hand] = []
        for h in hands:
            if h.can_split():
                h1, h2 = h.split()
                effective_hands.extend([h1, h2])
            else:
                effective_hands.append(h)

        # collect rows for each player hand
        this_deal_rows = []
        for h in effective_hands:
            game_id += 1
            df = play_player_hand(deck, dealer, h)
            df["game_id"] = game_id
            this_deal_rows.append(df)

        # dealer plays out
        fin = play_dealer(deck, dealer, cfg.soft17hit)

        # stamp dealer final score into rows
        for df in this_deal_rows:
            df["score_fin_dealer"] = fin

        # accumulate
        pack = pd.concat(this_deal_rows, ignore_index=True)
        rows.append(pack)

        # write chunk
        total = sum(len(r) for r in rows)
        if total >= cfg.chunk_write:
            out = pd.concat(rows, ignore_index=True)
            write_header = not os.path.exists(cfg.out_csv)
            out.to_csv(cfg.out_csv, mode="a", header=write_header, index=False)
            rows = []
            pbar.update(cfg.chunk_write)

        # stop condition
        written = (os.path.getsize(cfg.out_csv) > 0) if os.path.exists(cfg.out_csv) else False
        approx_rows = pbar.n  # tracked rows
        if approx_rows >= cfg.max_rows:
            break

        
        dealer.clear()
        for h in hands:
            h.clear()

    # flush remainder
    if rows:
        out = pd.concat(rows, ignore_index=True)
        write_header = not os.path.exists(cfg.out_csv)
        out.to_csv(cfg.out_csv, mode="a", header=write_header, index=False)
        pbar.update(len(out))

    pbar.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ndecks", type=int, default=8)
    parser.add_argument("--soft17hit", type=int, default=1, help="1=yes, 0=no")
    parser.add_argument("--max_rows", type=int, default=500_000)
    parser.add_argument("--nb_hands", type=int, default=3)
    parser.add_argument("--chunk_write", type=int, default=50_000)
    parser.add_argument("--out_csv", type=str, default=os.path.join("data", "blackjack_games.csv"))
    args = parser.parse_args()

    cfg = SimConfig(
        ndecks=args.ndecks,
        soft17hit=bool(args.soft17hit),
        max_rows=args.max_rows,
        nb_hands=args.nb_hands,
        chunk_write=args.chunk_write,
        out_csv=args.out_csv,
    )
    simulate(cfg)


if __name__ == "__main__":
    main()
