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

## Features
- **Blackjack rules** (configurable decks, soft 17 behavior, splits, doubles, blackjack payout).
- **Strategy evaluation** from a pre-computed optimal strategy (`strategy.pkl`).
- **Monte Carlo simulation** for realistic statistical results.
- **Session-based performance analysis** with quantile bands.
- **CSV output** of simulated games for further analysis.
- **Visualization** of:
  - Strategy decision matrices (hard hands, soft hands, splits).
  - Cumulative earnings with percentile bands.
- **Summary statistics**: win rate, draw rate, loss rate, EV per hand.
---

## Background

### Blackjack Rules
- Number cards (2–10) have face value.  
- Face cards (J, Q, K) are worth 10.  
- Ace (A) is worth 1 or 11.  
- Dealer must hit until 17+ (soft 17 rules configurable).  
- Blackjack pays 3:2 (1.5 units).  

### Monte Carlo Method
This simulation relies on **repeated random sampling** to approximate probabilities and outcomes.
---

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
## Installation
1. Clone the repository:
git clone https://github.com/yourusername/blackjack_simulation_python.git
cd blackjack_simulation_python
2. pip install -r requirements.txt
---
## Compiling
Run the below commands in order(CMD):
1. python -m src.simulate_games --ndecks 1 --max_rows 100000
2. python -m src.analyze
3. python -m src.test_strategy --ndecks 1 --length_session 1000 --n_session 200
---






