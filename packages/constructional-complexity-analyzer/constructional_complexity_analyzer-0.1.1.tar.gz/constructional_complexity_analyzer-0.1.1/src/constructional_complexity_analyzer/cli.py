import argparse
from .core import run_constructional_analysis

def main():
    parser = argparse.ArgumentParser(
        description="Run constructional complexity analysis on a directory of text files."
    )
    parser.add_argument(
        "input_text_dir",
        help="Path to the directory containing text files"
    )
    parser.add_argument(
        "--diversity_out", default="CSV_constructional_diversity_output.csv",
        help="Output path for constructional diversity CSV"
    )
    parser.add_argument(
        "--complexity_out", default="CSV_constructional_complexity.csv",
        help="Output path for constructional complexity CSV"
    )
    parser.add_argument(
        "--verbal_out", default="CSV_verbal_diversity_output.csv",
        help="Output path for verbal diversity CSV"
    )

    args = parser.parse_args()

    df_diversity, df_complexity, df_verbal = run_constructional_analysis(
        input_text_dir=args.input_text_dir,
        diversity_out=args.diversity_out,
        complexity_out=args.complexity_out,
        verbal_out=args.verbal_out,
    )

    print("Analysis complete!")
    print("Diversity results:", df_diversity.shape)
    print("Complexity results:", df_complexity.shape)
    print("Verbal results:", df_verbal.shape)
