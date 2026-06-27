import json
import time
from pathlib import Path

from tqdm import tqdm

BATCH_INPUT_PATH = "csv_files/batch_input.jsonl"
BATCH_POLL_INTERVAL_SECONDS = 30
BATCH_TERMINAL_STATUSES = {"completed", "failed", "expired", "cancelled"}


def openai_runner(openai_client, prompt_df, model_str, use_batch=False):
    """
    Runs every prompt in prompt_df through an OpenAI model.
    Returns a list of (prompt_id, response_text) tuples.
    Convert to a dataframe and merge with the main dataframe on prompt_id
    after running this.

    use_batch=False (default): one synchronous request per prompt.
    use_batch=True: submits all prompts as a single Batch API job. Cheaper
    (50% discount) and avoids per-request rate limits, but is asynchronous
    -- it can take anywhere from minutes to ~24h to complete, and this
    function blocks, polling until it's done.
    """
    if use_batch:
        return _openai_batch_runner(openai_client, prompt_df, model_str)
    return _openai_sync_runner(openai_client, prompt_df, model_str)


def _openai_sync_runner(openai_client, prompt_df, model_str):
    prompt_list = prompt_df["combined_prompt"].tolist()
    prompt_id_list = prompt_df["prompt_id"].tolist()

    response_list = []

    for prompt_id, prompt in tqdm(zip(prompt_id_list, prompt_list), total=len(prompt_list), desc=f"Running {model_str} (OpenAI, sync)"):
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


def _openai_batch_runner(openai_client, prompt_df, model_str):
    prompt_list = prompt_df["combined_prompt"].tolist()
    prompt_id_list = prompt_df["prompt_id"].tolist()

    batch_input_path = Path(BATCH_INPUT_PATH)
    batch_input_path.parent.mkdir(parents=True, exist_ok=True)
    with batch_input_path.open("w", encoding="utf-8") as f:
        for prompt_id, prompt in zip(prompt_id_list, prompt_list):
            request = {
                "custom_id": prompt_id,
                "method": "POST",
                "url": "/v1/responses",
                "body": {"model": model_str, "input": prompt},
            }
            f.write(json.dumps(request) + "\n")

    with batch_input_path.open("rb") as f:
        batch_file = openai_client.files.create(file=f, purpose="batch")

    batch = openai_client.batches.create(
        input_file_id=batch_file.id,
        endpoint="/v1/responses",
        completion_window="24h",
    )

    print(f"Submitted batch {batch.id} ({len(prompt_id_list)} prompts). Polling every {BATCH_POLL_INTERVAL_SECONDS}s...")
    while batch.status not in BATCH_TERMINAL_STATUSES:
        time.sleep(BATCH_POLL_INTERVAL_SECONDS)
        batch = openai_client.batches.retrieve(batch.id)
        print(f"Batch {batch.id} status: {batch.status}")

    if batch.status != "completed":
        raise RuntimeError(f"Batch {batch.id} ended with status '{batch.status}' instead of 'completed'")

    output_content = openai_client.files.content(batch.output_file_id).text
    results_by_id = {}
    for line in output_content.splitlines():
        if not line.strip():
            continue
        result = json.loads(line)
        prompt_id = result["custom_id"]
        if result.get("error"):
            results_by_id[prompt_id] = "Error"
            print(f"An error occurred for {prompt_id}: {result['error']}")
            continue
        results_by_id[prompt_id] = _extract_output_text(result["response"]["body"])

    # preserve original prompt order; mark any missing/failed rows as "Error"
    return [(prompt_id, results_by_id.get(prompt_id, "Error")) for prompt_id in prompt_id_list]


def _extract_output_text(response_body):
    """Mirrors the SDK's Response.output_text helper, for raw batch-output JSON."""
    chunks = []
    for item in response_body.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                chunks.append(content.get("text", ""))
    return "".join(chunks)
