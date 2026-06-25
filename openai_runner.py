# remember to activate venv  .researchvenv\Scripts\activate
from prompt_generator import combined_prompt_df
from openai import OpenAI

# this function will output list of results
def openai_runner(openai_client, prompt_df, model_str):
    """
    This returns a list of tuples containing prompt id and model response.
    Convert to a dataframe and merge with main dataframe after running this
    """
    prompt_list = prompt_df["combined_prompt"]
    prompt_id_list = prompt_df["prompt_id"]

    response_list = []

    for i in range(len(prompt_list)):
        try:
            response = openai_client.responses.create(
                model=model_str,
                input=prompt_list[i]
            )
            
            response_list.append((prompt_id_list[i], response))
        except Exception as e:
            response_list.append((prompt_id_list[i], "Error"))
            print(f"An error occurred: {e}")

    return response_list

