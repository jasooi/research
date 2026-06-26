# ---------------------------------------------------------------------------
# remember to activate venv  .researchvenv\Scripts\activate
# ---------------------------------------------------------------------------


import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

from prompt_generator import combined_prompt_df
from ollama_runner import ollama_runner
from openai_runner import openai_runner

load_dotenv()

SEALION_MODEL = "aisingapore/Llama-SEA-LION-v3.5-8B-R"
OPENAI_MODEL = "gpt-4o"

RESULTS_CSV_PATH = "csv_files/combined_prompts_with_responses.csv"


def merge_responses(df, response_list, column_name):
    """
    Merges a list of (prompt_id, response_text) tuples into df as a new
    column, matched on prompt_id so any skipped/missing rows don't
    silently misalign with the wrong prompt.
    """
    response_df = pd.DataFrame(response_list, columns=["prompt_id", column_name])
    return df.merge(response_df, on="prompt_id", how="left")


def main():
    results_df = combined_prompt_df.copy()

    sealion_responses = ollama_runner(combined_prompt_df, SEALION_MODEL)
    results_df = merge_responses(results_df, sealion_responses, "sealion_response")

    openai_client = OpenAI()
    gpt4o_responses = openai_runner(openai_client, combined_prompt_df, OPENAI_MODEL)
    results_df = merge_responses(results_df, gpt4o_responses, "gpt4o_response")

    results_df.to_csv(RESULTS_CSV_PATH, index=False)
    print(f"Saved {len(results_df)} rows to {RESULTS_CSV_PATH}")

    return results_df


if __name__ == "__main__":
    main()
