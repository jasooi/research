# ---------------------------------------------------------------------------
# remember to activate venv  .researchvenv\Scripts\activate
# ---------------------------------------------------------------------------


import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

from prompt_generator import combined_prompt_df
from ollama_runner import ollama_runner
from openai_runner import openai_runner

load_dotenv()

regional_model = os.getenv("SEALION_MODEL")
regional_model_friendly_name = os.getenv("SEALION_MODEL_NAME")
frontier_model = os.getenv("OPENAI_MODEL")
frontier_model_friendly_name = frontier_model

output_path = os.getenv("OUTPUT_PATH")


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

    regional_responses = ollama_runner(combined_prompt_df, regional_model)
    results_df = merge_responses(results_df, regional_responses, f"{regional_model_friendly_name}_response")

    openai_client = OpenAI()
    gpt4o_responses = openai_runner(openai_client, combined_prompt_df, frontier_model, use_batch=False)
    results_df = merge_responses(results_df, gpt4o_responses, f"{frontier_model_friendly_name}_response")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    root, ext = os.path.splitext(output_path)
    timestamped_output_path = f"{root}_{timestamp}{ext}"

    results_df.to_csv(timestamped_output_path, index=False)
    print(f"Saved {len(results_df)} rows to {timestamped_output_path}")

    return results_df


if __name__ == "__main__":
    main()
