import argparse
from src import run_simulation, analysis, test_strategy

def main():
    parser = argparse.ArgumentParser(description="Blackjack Monte Carlo Simulation")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---- SIMULATE ----
    simulate_parser = subparsers.add_parser("simulate", help="Run Monte Carlo simulation of Blackjack")
    simulate_parser.add_argument("--ndecks", type=int, default=8, help="Number of decks to use")
    simulate_parser.add_argument("--soft17hit", type=bool, default=True, help="Dealer hits on soft 17?")
    simulate_parser.add_argument("--max_rows", type=int, default=1000000, help="Number of rows to simulate")
    simulate_parser.add_argument("--nb_hands", type=int, default=3, help="Number of player hands per game")
    simulate_parser.add_argument("--chunk_write", type=int, default=10000, help="Write CSV every X rows")
    simulate_parser.add_argument("--out_csv", type=str, default="blackjack_games.csv", help="Output CSV file")

    # ---- ANALYZE ----
    analyze_parser = subparsers.add_parser("analyze", help="Analyze simulation results and build strategy")
    analyze_parser.add_argument("--csv", type=str, default="blackjack_games.csv", help="CSV file to analyze")

    # ---- TEST ----
    test_parser = subparsers.add_parser("test", help="Test a strategy over multiple sessions")
    test_parser.add_argument("--n_session", type=int, default=1000, help="Number of sessions")
    test_parser.add_argument("--length_session", type=int, default=1000, help="Hands per session")
    test_parser.add_argument("--nb_hands", type=int, default=2, help="Number of player hands per game")
    test_parser.add_argument("--strategy_file", type=str, default="strategy.pkl", help="Saved strategy file")

    args = parser.parse_args()

    if args.command == "simulate":
        run_simulation.run(
            ndecks=args.ndecks,
            soft17hit=args.soft17hit,
            max_rows=args.max_rows,
            nb_hands=args.nb_hands,
            chunk_write=args.chunk_write,
            out_csv=args.out_csv
        )

    elif args.command == "analyze":
        analysis.run_analysis(csv_file=args.csv)

    elif args.command == "test":
        test_strategy.run_test(
            n_session=args.n_session,
            length_session=args.length_session,
            nb_hands=args.nb_hands,
            strategy_file=args.strategy_file
        )

if __name__ == "__main__":
    main()
