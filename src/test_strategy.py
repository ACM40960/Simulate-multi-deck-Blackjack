import argparse
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from tqdm import trange

from .deck import Deck
from .hand import Hand

STRAT_PKL = os.path.join("data", "strategy.pkl")
OUTPNG = os.path.join("outputs", "strategy.png")


def dealer_should_hit(dealer: Hand, soft17hit: bool) -> bool:
    s = dealer.score()
    return (s < 17) or (s == 17 and (not dealer.is_hard()) and soft17hit)


def decision_for(hand: Hand, dealer: Hand, strat_df, splitdone=False):
    # lookup row by (score, score_dealer_upcard, hard)
    sc = hand.score()
    sd = dealer.score(first_card_only=True)
    hd = hand.is_hard()

    # exact match
    row = strat_df[
        (strat_df["score"] == sc) &
        (strat_df["score_dealer"] == sd) &
        (strat_df["hard"] == hd)
    ]
    if len(row) == 0:
        return "stand"
    row = row.iloc[0]
    if not splitdone and hand.can_split():
        if not np.isnan(row.get("should_split", np.nan)):
            if bool(row["should_split"]):
                return "split"
    return row["decision"] if isinstance(row["decision"], str) else "stand"


def earnings(score, score_dealer):
    
    if score > 21:
        return -1
    if score == 0 and score_dealer != 0:
        return 1.5
    if score != 0 and score_dealer == 0:
        return -1
    if (score > score_dealer) or (score_dealer > 21):
        return 1
    if score == score_dealer:
        return 0
    return -1


def run_sessions(ndecks=8, soft17hit=True, length_session=1000, n_session=1000, nb_hands=2):
    with open(STRAT_PKL, "rb") as f:
        strat = pickle.load(f)

    results = np.zeros((length_session, n_session), dtype=float)
    
    win_units = 0
    draw_units = 0
    loss_units = 0
    total_units = 0


    for i in trange(n_session, desc="Sessions"):
        deck = Deck(ndecks=ndecks, with_stop_token=True)
        _ = deck.draw()  # burn
        dealer = Hand()
        hands = [Hand() for _ in range(nb_hands)]

        for j in range(length_session):
            # deal
            for h in hands + [dealer]:
                h.clear()
                h.get(deck.draw())
                h.get(deck.draw())

            # players
            final_scores = []
            for h in hands:
                if h.score() == 21:
                    final_scores.append(0)  
                    continue
                dec = decision_for(h, dealer, strat)
                if dec == "split":
                    h1, h2 = h.split()
                    for s in (h1, h2):
                        d2 = decision_for(s, dealer, strat, splitdone=True)
                        if d2 == "double":
                            s.get(deck.draw())
                            final_scores.append(s.score())
                            final_scores.append(s.score())  # double stakes
                        else:
                            while s.score() < 21 and d2 != "stand":
                                s.get(deck.draw())
                                d2 = decision_for(s, dealer, strat, splitdone=True)
                            final_scores.append(s.score())
                elif dec == "double":
                    h.get(deck.draw())
                    final_scores.append(h.score())
                    final_scores.append(h.score())
                else:
                    while h.score() < 21 and dec != "stand":
                        h.get(deck.draw())
                        dec = decision_for(h, dealer, strat)
                    final_scores.append(h.score())

            # dealer plays
            while dealer_should_hit(dealer, soft17hit):
                dealer.get(deck.draw())
            sd = dealer.score()
            if sd == 21 and str(dealer.cards[0]).startswith("A"):
                sd = 0  # mark dealer blackjack as 0 like R

            
            earn = 0.0
            for sc in final_scores:
                ev = earnings(sc, sd)  
                earn += ev
                # Count “win/draw/loss” by sign of unit outcome
                if ev > 0:
                    win_units += 1
                elif ev == 0:
                    draw_units += 1
                else:
                    loss_units += 1
                total_units += 1

            results[j, i] = (results[j-1, i] if j > 0 else 0) + earn


    # summarize quantiles across sessions at each game step
    e_mean = results.mean(axis=1)
    e_min = results.min(axis=1)
    e_max = results.max(axis=1)
    q01 = np.quantile(results, 0.01, axis=1)
    q05 = np.quantile(results, 0.05, axis=1)
    q10 = np.quantile(results, 0.10, axis=1)
    q90 = np.quantile(results, 0.90, axis=1)
    q95 = np.quantile(results, 0.95, axis=1)
    q99 = np.quantile(results, 0.99, axis=1)

    x = np.arange(1, length_session+1)
    plt.figure(figsize=(10,6))
    plt.fill_between(x, e_min, e_max, alpha=0.3, label="min | max")
    plt.fill_between(x, q01, q99, alpha=0.3, label="1% | 99%")
    plt.fill_between(x, q05, q95, alpha=0.3, label="5% | 95%")
    plt.fill_between(x, q10, q90, alpha=0.3, label="10% | 90%")
    plt.plot(x, e_mean, label="Average")
    plt.xlabel("Game")
    plt.ylabel("Earnings (cumulative)")
    plt.legend()
    os.makedirs(os.path.dirname(OUTPNG), exist_ok=True)
    plt.tight_layout()
    plt.savefig(OUTPNG, dpi=180)
    print(f"Saved: {OUTPNG}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ndecks", type=int, default=8)
    parser.add_argument("--soft17hit", type=int, default=1)
    parser.add_argument("--length_session", type=int, default=1000)
    parser.add_argument("--n_session", type=int, default=200)  # 1000 can be slow
    parser.add_argument("--nb_hands", type=int, default=2)
    args = parser.parse_args()
    run_sessions(
        ndecks=args.ndecks,
        soft17hit=bool(args.soft17hit),
        length_session=args.length_session,
        n_session=args.n_session,
        nb_hands=args.nb_hands
    )


if __name__ == "__main__":
    main()
