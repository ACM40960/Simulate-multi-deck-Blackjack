import os
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

DATA_CSV = os.path.join("data", "blackjack_games.csv")
STRAT_PKL = os.path.join("data", "strategy.pkl")
OUTDIR = "outputs"
os.makedirs(OUTDIR, exist_ok=True)


def load_and_prepare():
    games = pd.read_csv(DATA_CSV)

    # bust flags
    games["bust_dealer"] = games["score_fin_dealer"] > 21
   
    games["bust"] = games["score_if_hit"].isna() | (games["score_if_hit"] > 21)

    # win/draw at current level (stand now)
    games["win"] = (games["score"] > games["score_fin_dealer"]) | games["bust_dealer"]
    games["draw"] = (games["score"] == games["score_fin_dealer"])

    # outcomes if hit once
    win_if_hit = ( (games["score_if_hit"] > games["score_fin_dealer"]) | games["bust_dealer"] ) & (~games["bust"])
    draw_if_hit = (games["score_if_hit"] == games["score_fin_dealer"]) & (~games["bust"])
    games["win_if_hit"] = win_if_hit.fillna(False)
    games["draw_if_hit"] = draw_if_hit.fillna(False)

    
    games["hard_if_hit"] = games["hard_if_hit"].astype("boolean").fillna(True)

    
    games["stand"] = np.where(games["win"], 1, np.where(games["draw"], 0, -1))
    games["double"] = 2 * np.where(games["win_if_hit"], 1, np.where(games["draw_if_hit"], 0, -1))
    games["hit"] = np.where(games["win_if_hit"], 1, np.where(games["draw_if_hit"], 0, -1))

   
    keep = [
        "score","score_dealer","hard","score_if_hit","score_fin_dealer","game_id",
        "hit","stand","double","hard_if_hit"
    ]
    # if 'score_dealer' came as float (csv), ensure int
    games["score_dealer"] = games["score_dealer"].astype(int)
    games = games[keep]
    return games


def best_possible(games):
    g = games.groupby("game_id").agg(
        hit_max=("hit","max"),
        stand_max=("stand","max"),
        double_first=("double","first")   # -2/0/2
    ).reset_index()

    # EV upper bound 
    g["ev_best"] = g[["hit_max","stand_max","double_first"]].max(axis=1)
    print(f"Best possible EV (perfect hindsight): {g['ev_best'].mean():.3f} units/hand")

    # True win rate upper bound 

    g["win_any"] = (g["hit_max"] > 0) | (g["stand_max"] > 0) | (g["double_first"] > 0)
    print(f"Best possible win rate (upper bound): {g['win_any'].mean()*100:.2f}%")

    return g



def simple_threshold_strategy(games: pd.DataFrame):
    # emulate earns(i): stand at threshold i or above; otherwise hit
    rows = []
    for i in range(2, 22):
      
        def choose_row(group):
            g = group.sort_values("score")
            below = g[g["score"] < i]
            if len(below) > 0:
                
                r = below.iloc[-1]
                outcome = r["hit"]
            else:
                
                above = g[g["score"] >= i]
                r = above.iloc[0]
                outcome = r["stand"]
            return pd.Series({
                "outcome": outcome
            })

        b = games.groupby("game_id", group_keys=False).apply(choose_row).reset_index(drop=True)
        exp = b["outcome"].mean()
        rows.append({"threshold": i, "exp": exp,
                     "draw": (b["outcome"] == 0).mean(),
                     "lose": (b["outcome"] < 0).mean(),
                     "win": (b["outcome"] > 0).mean()})
    df = pd.DataFrame(rows)
    # plot
    plt.figure()
    plt.bar(df["threshold"], df["win"], alpha=0.5, label="win")
    plt.bar(df["threshold"], df["draw"], bottom=df["win"], alpha=0.5, label="draw")
    plt.bar(df["threshold"], df["lose"], bottom=df["win"]+df["draw"], alpha=0.5, label="lose")
    # overlay normalized expected value curve
    M, m = df["exp"].max(), df["exp"].min()
    norm = (df["exp"] - m) / (M - m + 1e-12)
    plt.plot(df["threshold"], norm, linewidth=2)
    plt.xlabel("Hit threshold")
    plt.ylabel("Expected earning (stacked bars rescaled)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "simple_strat.png"), dpi=180)
    print(f"Best threshold: {df.loc[df['exp'].idxmax(),'threshold']}")
    return df


def recursive_strategy(games: pd.DataFrame):
    """
    Reproduce the R recursive DP over (score, score_dealer, hard) states,
    using the empirical transition rows in games to compute:
      a_stand = mean(stand)
      a_double = mean(double)
      a_hit = weighted mean of next state's 'earn' (if known) else mean(hit)
    """
    # aggregate immediate outcomes by (state, next_state)
    g = (games
         .groupby(["score","score_dealer","hard","score_if_hit","hard_if_hit"])
         .agg(N=("hit","size"),
              hit=("hit","mean"),
              double=("double","mean"),
              stand=("stand","mean"))
         .reset_index())

  
    states = (games[["score","score_dealer","hard"]]
              .drop_duplicates()
              .sort_values(by=["hard","score","score_dealer"], ascending=[True, False, False]))
    states["decision"] = None
    states["earn"] = np.nan
    states["earn_if_stand"] = np.nan
    states["earn_if_double"] = np.nan
    states["earn_if_hit"] = np.nan

    # helper to fetch transitions for a given state
    g_key = g.set_index(["score","score_dealer","hard"])

    for i, row in tqdm(states.iterrows(), total=len(states), desc="Solving DP"):
        sc = int(row["score"])
        scd = int(row["score_dealer"])
        hd = bool(row["hard"])

        # all next possibilities from hitting in this state
        try:
            h = g_key.loc[(sc, scd, hd)].reset_index()
        except KeyError:
            
            states.loc[i, ["decision","earn","earn_if_stand","earn_if_double","earn_if_hit"]] = ["stand", 0.0, 0.0, 0.0, 0.0]
            continue

       
        future = states.set_index(["score","score_dealer","hard"])["earn"]
        # build key for lookup
        keys = list(zip(h["score_if_hit"].astype(int), [scd]*len(h), h["hard_if_hit"].astype(bool)))
        earn_next = []
        for k in keys:
            earn_next.append(future.get(k, np.nan))
        earn_next = np.array(earn_next, dtype=float)

        # compute action values
        a_stand = np.average(h["stand"], weights=h["N"])
        a_double = np.average(h["double"], weights=h["N"])

        
        if np.isnan(earn_next).all():
            a_hit = np.average(h["hit"], weights=h["N"])
        else:
            # when some next states unknown, backfill with immediate hit value
            fallback = h["hit"].to_numpy()
            mixed = np.where(np.isnan(earn_next), fallback, earn_next)
            a_hit = np.average(mixed, weights=h["N"])

        # choose best
        vals = np.array([a_double, a_hit, a_stand])
        acts = np.array(["double","hit","stand"])
        best_idx = int(np.argmax(vals))
        states.loc[i, "decision"] = acts[best_idx]
        states.loc[i, "earn"] = vals[best_idx]
        states.loc[i, "earn_if_stand"] = a_stand
        states.loc[i, "earn_if_double"] = a_double
        states.loc[i, "earn_if_hit"] = a_hit

    # soft / hard heatmaps
    def heatmap(df, title, fname):
        pivot = df.pivot_table(index="score", columns="score_dealer", values="decision", aggfunc="first")
        # simple text heatmap
        plt.figure(figsize=(10,6))
        plt.imshow(pivot.notna(), aspect="auto")
        plt.title(title)
        plt.xlabel("Dealer upcard (2=2 ... 11=Ace)")
        plt.ylabel("Player score")
        plt.tight_layout()
        plt.savefig(os.path.join(OUTDIR, fname), dpi=180)

    heatmap(states[states["hard"] == True], "Hard hands – decision (mask)", "hard_strat.png")
    heatmap(states[(states["hard"] == False) & (states["score"] != 21)], "Soft hands – decision (mask)", "soft_strat.png")

    
    st = states.copy()
    st["should_split"] = np.nan
    for i, r in st.iterrows():
        sc = int(r["score"])
        if sc % 2 == 0:
            key_half = (sc//2, int(r["score_dealer"]), bool(r["hard"]))
            earn_half = states.set_index(["score","score_dealer","hard"])["earn"].get(key_half, np.nan)
            if not np.isnan(earn_half) and not np.isnan(r["earn"]):
                st.loc[i, "should_split"] = (r["earn"] < 2 * earn_half)
   
    st.loc[(st["score"] == 12) & (st["hard"] == False), "should_split"] = True

    with open(STRAT_PKL, "wb") as f:
        pickle.dump(st, f)

    print(f"Saved strategy to {STRAT_PKL}")
    return states, st


def main():
    games = load_and_prepare()
    _ = best_possible(games)
    simple_threshold_strategy(games)
    recursive_strategy(games)


if __name__ == "__main__":
    main()

