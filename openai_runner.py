# remember to activate venv  .researchvenv\Scripts\activate
from tqdm import tqdm


def openai_runner(openai_client, prompt_df, model_str):
    """
    Runs every prompt in prompt_df through an OpenAI model.
    Returns a list of (prompt_id, response_text) tuples.
    Convert to a dataframe and merge with the main dataframe on prompt_id
    after running this.
    """
    prompt_list = prompt_df["combined_prompt"].tolist()
    prompt_id_list = prompt_df["prompt_id"].tolist()

    response_list = []

    for prompt_id, prompt in tqdm(zip(prompt_id_list, prompt_list), total=len(prompt_list), desc=f"Running {model_str} (OpenAI)"):
        try:
            response = openai_client.responses.create(
                model=model_str,
                input=prompt
            )

            response_list.append((prompt_id, response.output_text))
        except Exception as e:
            response_list.append((prompt_id, "Error"))
            print(f"An error occurred for {prompt_id}: {e}")

    return response_list

    # TODO: consider using batching

