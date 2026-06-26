# Cultural Value Alignment in Regional vs. Global LLMs

Code for an experiment assessing whether regional LLMs (e.g. SEA-LION, a model
tuned for Southeast Asia) exhibit cultural values that align with the target
populations they aim to serve, compared against a general-purpose global model
(GPT-4o). Alignment is probed by asking each model World Values Survey (WVS)
questions under different value-positioned personas.

## Methodology

1. **Persona generation** — system prompts are generated that position the
   responder along the four WVS cultural value dimensions (traditional,
   secular-rational, survival, self-expression), individually and in
   combination, with variation in:
   - framing (identity, e.g. *"a traditional person"*, vs. preference, e.g.
     *"a person who values tradition and faith"*)
   - emphasiser strength (`deeply`, `strongly`, `very`, `greatly`, or none)
   - responder noun (`person`, `individual`)
2. **Prompt assembly** — every persona is crossed with every WVS survey
   question to produce the full prompt set.
3. **Model comparison** — the same prompt set is run against:
   - **GPT-4o** (OpenAI API) — general-purpose, global model
   - **SEA-LION v3.5 Llama3.1 8B** (`aisingapore/Llama-SEA-LION-v3.5-8B-R`, via
     Ollama) — Southeast-Asia-focused regional model
4. Responses are compared across personas and models to assess whether
   SEA-LION's answers track the cultural values it's meant to represent more
   closely than GPT-4o's do.

## Repo structure

```
main.py                      Entry point: runs both models and persists results
prompt_generator.py          Builds the persona x WVS-question prompt set
ollama_runner.py             Runner function for SEA-LION v3.5 (via local Ollama)
openai_runner.py             Runner function for GPT-4o (via OpenAI API)
csv_files/
  wvs_questions.csv                      Input: WVS question id, theme, and question text
  combined_prompts.csv                   Output of prompt_generator.py: full prompt set
  combined_prompts_with_responses.csv    Output of main.py: prompt set + both models' responses
requirements.txt
```

## Setup

1. Create and activate a virtual environment:
   ```
   python -m venv .researchvenv
   .researchvenv\Scripts\activate   # Windows
   source .researchvenv/bin/activate  # macOS/Linux
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. **SEA-LION (Ollama):** install [Ollama](https://ollama.com), then pull the
   model:
   ```
   ollama pull aisingapore/Llama-SEA-LION-v3.5-8B-R
   ```
4. **GPT-4o (OpenAI):** add your API key to a `.env` file in the repo root
   (gitignored):
   ```
   OPENAI_API_KEY=sk-...
   ```

## Usage

### 1. Generate the prompt set

```
python prompt_generator.py
```

Reads `csv_files/wvs_questions.csv` and writes the full persona x question
prompt set to `csv_files/combined_prompts.csv` (one row per `prompt_id`, with
the assembled `combined_prompt` text).

### 2. Run both models and persist results

```
python main.py
```

This runs every prompt in `combined_prompt_df` through SEA-LION (via Ollama)
and then GPT-4o (via the OpenAI API). Each runner function
(`ollama_runner()`, `openai_runner()`) returns a list of `(prompt_id,
response_text)` tuples; `main.py` merges each list back onto
`combined_prompt_df` as a new column (`sealion_response`,
`gpt4o_response`), matching on `prompt_id` so a skipped or out-of-order
generation can't silently misalign with the wrong row. The enriched
dataframe is saved to `csv_files/combined_prompts_with_responses.csv`.

## Status / next steps

- [ ] Consider batching for the OpenAI runner (see TODO in `openai_runner.py`)
- [ ] Add response post-processing/scoring against the WVS value dimensions
