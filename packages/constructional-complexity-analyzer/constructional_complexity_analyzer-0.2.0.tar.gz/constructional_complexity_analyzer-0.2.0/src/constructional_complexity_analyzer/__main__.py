import sys
from constructional_complexity_analyzer.core import run_constructional_analysis

def main():
    if len(sys.argv) < 2:
        print("Usage: constructional-analysis <input_text_dir>")
        sys.exit(1)

    input_text_dir = sys.argv[1]
    df_diversity, df_elaboration, df_verb = run_constructional_analysis(input_text_dir)
    print(df_diversity.head())
    print(df_elaboration.head())
    print(df_verb.head())
