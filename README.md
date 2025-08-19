<p align="center">
  <img src="https://github.com/ACM40960/Simulate-single-deck-Blackjack/blob/main/Blackjack.png" alt="Blackjack Logo" width="200"/>
</p>

<h1 align="center">🎲  Blackjack Strategy Simulator (Monte Carlo)</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" />
  <img src="https://img.shields.io/badge/NumPy-Latest-orange" />
  <img src="https://img.shields.io/badge/Matplotlib-Latest-green" />
  <img src="https://img.shields.io/badge/Pandas-Latest-yellow" />
  <img src="https://img.shields.io/badge/License-MIT-brightgreen.svg" />
  <img src="https://img.shields.io/github/stars/ACM40960/Simulate-single-deck-Blackjack?style=social" />
</p>

This project simulates and analyzes the game of Blackjack (21) using **Monte Carlo methods**.  
It evaluates different strategies by simulating large numbers of games, computing expected values (EV), win/draw/loss rates, and visualizing performance.

---
## 📖 Table of Contents
1. [Overview](#overview)  
2. [Features](#features)  
3. [Project Structure](#project-structure)  
4. [Installation](#installation)  
5. [Simulation Pipeline](#simulation-pipeline)   
6. [Outputs & Analysis](#outputs--analysis)  
7. [Future Work](#future-work)  
8. [Contributing](#contributing)  
9. [Contact](#contact)

---

## 🔍 Overview
Blackjack is modeled as a **finite-horizon stochastic control problem**.  
Each state includes:  
- Player total  
- Soft/hard flag  
- Dealer upcard  
- Split count  
- Double availability  

Actions = {Hit, Stand, Double, Split}.  
We simulate many rounds to estimate EV with **95% confidence intervals**, enabling fair comparisons of strategies and rules.

---

## ✨ Features
- Flexible **house rules**:  
  - Decks: single or multi-deck  
  - Dealer S17/H17  
  - Payout: 3:2 vs 6:5  
  - Double-after-split, re-splitting, etc.  
- Two policies: **Basic Strategy** vs **Naive**.  
- Supports **dataset generation** (EV lookups, action heatmaps) and **finite-shoe simulation**.  
- Outputs **EV curves, win/loss/push rates, quantile bands**.  
- All results export to CSV + plots for reproducibility.  

---

## 📂 Project Structure
```
simulate-blackjack/
├── blackjack_pipeline.py # Main pipeline
├── strategies/
│ ├── basic_strategy.py # Basic strategy lookup
│ └── simple_strategy.py # Naive (hit threshold) strategy
├── data/
│ └── strategy.pkl # Pre-computed strategy table
├── outputs/ # Simulation results (CSVs + plots)
├── docs/images/ # Figures used in README & poster
├── requirements.txt
└── README.md
```
---

## ⚙️ Installation

### Prerequisites
- Python **3.10+**
- pip

### Setup

git clone https://github.com/yourusername/blackjack_simulation_python.git
cd blackjack_simulation_python
pip install -r requirements.txt

## Methodology

1. **Game Modelling**
   - **Deck Model:** Supports single or multiple decks with shuffling.  
   - **Ace Handling:** Aces initially count as 11, adjusted to 1 if necessary to prevent busting.  
   - **Dealer Rules:** Dealer hits until reaching at least 17 (soft 17 behavior configurable).  

2. **Strategies Tested**
   - **Simple Strategy:** Always hit if hand value < 17, otherwise stand.  
   - **Basic Strategy (generated):** Decision table derived from simulated outcomes (`strategy.pkl`), includes hit/stand/double/split logic.  

3. **Simulation Process**
   - Deal two cards to player and dealer.  
   - Apply chosen strategy to player until they stand, bust, or take a double/split action.  
   - Dealer plays according to rules.  
   - Compare outcomes to determine win/draw/loss and calculate payoff.  
   - Repeat for thousands or millions of games to achieve stable statistics.  

4. **Performance Metrics**
   - **Win Rate** – Percentage of units won.  
   - **Draw Rate** – Percentage of units pushed.  
   - **Loss Rate** – Percentage of units lost.  
   - **Average EV per Hand** – Expected value in units over all hands.  
   - **Cumulative Earnings Graph** – Visualizes performance over time with percentile bands.

---

## Compiling
Run the below commands in order(CMD):
1. python -m src.simulate_games --ndecks 1 --max_rows 100000
2. python -m src.analyze
3. python -m src.test_strategy --ndecks 1 --length_session 1000 --n_session 200
---

## 📊 Outputs

Simulation produces:

CSV files: win/push/loss %, EV, CI

Plots: session EV convergence & quantile bands

Example EV Quantile Plot
<p align="center"> <img src="docs/images/ev_quantile_bands.png" width="600"/> </p>
Example Heatmap of Decisions
<p align="center"> <img src="docs/images/heatmap_basic.png" width="600"/> </p>

## 📈 Results & Discussion

Basic vs Naive: Basic improves win rate by +2.25pp, reduces loss by −1.3pp.

Deck count: EV worsens slightly with more decks (1–2 ≈ break-even, 4–6 negative).

Rules matter more than deck count:

S17 improves EV by ≈ +0.2pp

6:5 payout reduces EV by −1.3–1.5pp

Takeaway: Always play Basic Strategy at 3:2, S17, DAS tables; avoid 6:5 games.

## Contact

In case of any clarifications or queries, do reach out to the author :-

**Krishna Ramachandra** krishna.ramachandra@ucdconnect.ie

**zhixuan zhou** zhixuan.zhou@ucdconnect.ie

**DISCLAIMER** : This project is intended purely for educational and academic purpose and does not endorse betting or gambling in any form.




