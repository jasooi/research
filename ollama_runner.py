from prompt_generator import combined_prompt_df
import ollama
import pandas as pd

# ---------------------------------------------------------------------------
# Prerequisite: run ollama pull MODEL in terminal beforehand
# will use SEA-LION v3.5 Llama3.1 8b for pilot
# ---------------------------------------------------------------------------
model_str = 'aisingapore/Llama-SEA-LION-v3.5-8B-R'

# test single response first
test_prompt = combined_prompt_df["combined_prompt"][0]
test_prompt_id = combined_prompt_df["prompt_id"][0]

test_response = ollama.generate(
                model=model_str,
                prompt=test_prompt
            )

response_text = test_response.response

with open("output.txt", "w", encoding="utf-8") as file:
    file.write(response_text)

#print(f"prompt {test_prompt_id}: {test_response}")



# def ollama_runner(prompt_df, model_str):
#     """
#     This returns a list of tuples containing prompt id and model response.
#     Convert to a dataframe and merge with main dataframe after running this
#     """
#     prompt_list = prompt_df["combined_prompt"]
#     prompt_id_list = prompt_df["prompt_id"]

#     response_list = []

#     for i in range(len(prompt_list)):
#         try:
#             response = ollama.generate(
#                 model=model_str,
#                 prompt=prompt_list[i]
#             )
#             response_list.append((prompt_id_list[i], response))
#         except Exception as e:
#             response_list.append((prompt_id_list[i], "Error"))
#             print(f"An error occurred: {e}")

#     return response_list