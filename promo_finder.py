"""promo_finder.py

Command-line interface (CLI) for Kuku Microdrama Promo Finder.

Usage:
    python promo_finder.py --input ./data --out ./outputs
    python promo_finder.py --input ./data --out ./outputs --stability-check
"""

import argparse
import sys
from pathlib import Path

from pipeline import PromoFinderPipeline, run_pipeline
from llm_client import LLMClient


def parse_args():
    parser = argparse.ArgumentParser(
        description="Kuku Microdrama Promo Finder: Extract 20-60s promos with exact timestamps."
    )
    parser.add_argument(
        "--input",
        type=str,
        default="./data",
        help="Path to folder containing episode .txt screenplay files (default: ./data)"
    )
    parser.add_argument(
        "--out",
        type=str,
        default="./outputs",
        help="Path to directory for outputs (default: ./outputs)"
    )
    parser.add_argument(
        "--max-episodes",
        type=int,
        default=None,
        help="Optional limit on number of episodes to process (useful for rapid tests)"
    )
    parser.add_argument(
        "--stability-check",
        action="store_true",
        help="Run pipeline with dual temperatures (0.2 vs 0.7) to evaluate Top-10 ranking stability."
    )
    return parser.parse_args()


def run_stability_check(input_dir: str, out_dir: str, max_episodes: int = 10):
    print("\n" + "=" * 80)
    print("RUNNING STABILITY CHECK (Temperature 0.2 vs 0.7)")
    print("=" * 80)

    # Run 1: Temperature 0.2 (Baseline)
    print("\n--- RUN 1: Temperature 0.2 ---")
    pipe1 = PromoFinderPipeline(
        llm_client=LLMClient(),
        out_dir=f"{out_dir}/stability_t02",
        raw_dir=f"{out_dir}/stability_t02/raw"
    )
    pipe1.load_data(input_dir)
    pipe1.run_pass_1(max_episodes=max_episodes)
    pipe1.run_pass_2()
    pipe1.validate_and_deduplicate()
    pipe1.run_pass_3_judge()
    top_t02 = pipe1.rank_and_export()[:10]

    # Run 2: Temperature 0.7
    print("\n--- RUN 2: Temperature 0.7 ---")
    pipe2 = PromoFinderPipeline(
        llm_client=LLMClient(),
        out_dir=f"{out_dir}/stability_t07",
        raw_dir=f"{out_dir}/stability_t07/raw"
    )
    pipe2.load_data(input_dir)
    pipe2.run_pass_1(max_episodes=max_episodes)
    pipe2.run_pass_2()
    pipe2.validate_and_deduplicate()
    pipe2.run_pass_3_judge()
    top_t07 = pipe2.rank_and_export()[:10]

    # Compare overlap
    ids_02 = {p.promo_id for p in top_t02}
    ids_07 = {p.promo_id for p in top_t07}
    overlap = ids_02.intersection(ids_07)
    overlap_rate = len(overlap) / 10.0 * 100.0

    print("\n" + "=" * 80)
    print("STABILITY CHECK RESULTS")
    print("=" * 80)
    print(f"Top 10 (Temp 0.2): {[p.promo_id for p in top_t02]}")
    print(f"Top 10 (Temp 0.7): {[p.promo_id for p in top_t07]}")
    print(f"Shared in Top 10:  {len(overlap)} / 10 ({overlap_rate:.1f}% overlap)")
    print("=" * 80)


def main():
    args = parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input path '{args.input}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if args.stability_check:
        run_stability_check(args.input, args.out, max_episodes=args.max_episodes or 15)
        return

    print("=" * 80)
    print("KUKU MICRODRAMA PROMO FINDER PIPELINE")
    print("=" * 80)
    print(f"Input Directory:  {args.input}")
    print(f"Output Directory: {args.out}")

    ranked_promos = run_pipeline(
        input_dir=args.input,
        out_dir=args.out,
        max_episodes=args.max_episodes
    )

    print("\n" + "=" * 80)
    print(f"SUCCESS: Generated {len(ranked_promos)} ranked promo clips.")
    print(f"Deliverables exported:")
    print(f"  - {args.out}/raw/promos.json")
    print(f"  - {args.out}/raw/promos.csv")
    print(f"  - ranking.md")
    print(f"  - quality_report.md")
    print("=" * 80)


if __name__ == "__main__":
    main()
