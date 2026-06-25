# Generate full list of system prompts
# To run this file, you need wvs_questions.csv
# system_prompts.csv and combined_prompts.csv will be generated

from dataclasses import dataclass, asdict
import pandas as pd
# ---------------------------------------------------------------------------
# Layer 1: generate and edit value positionings
# first define nested dictionary of value positionings, there should be 9 positions
# no space between {emphasiser} and the next word to avoid double space when no emphasiser is used
# ---------------------------------------------------------------------------
VALUE_POSITIONING = {
    "default": {
        "trad": 0, 
        "rat": 0, 
        "surv": 0, 
        "self": 0,
        "variants": [
            {
                "template": "an average {responder_noun}",
                "tradrat_framing": None, 
                "survself_framing": None
            },
            {
                "template": "a typical {responder_noun}",
                "tradrat_framing": None, 
                "survself_framing": None
            },
        ],
    },
    "traditional values": {
        "trad": 1, 
        "rat": 0, 
        "surv": 0, 
        "self": 0,
        "variants": [
            {
                "template": "a {emphasiser}traditional {responder_noun}",
                "tradrat_framing": "identity", 
                "survself_framing": None
            },
            {
                "template": "a {responder_noun} who values tradition and faith",
                "tradrat_framing": "preference", 
                "survself_framing": None
            },
        ],
    },
    "secular-rational values": {
        "trad": 0, 
        "rat": 1, 
        "surv": 0, 
        "self": 0,
        "variants": [
            {
                "template": "a {emphasiser}modern and secular {responder_noun}",
                "tradrat_framing": "identity", 
                "survself_framing": None
            },
            {
                "template": "a {responder_noun} who values reason over tradition",
                "tradrat_framing": "preference", 
                "survself_framing": None
            },
        ],
    },

    "survival values": {
            "trad": 0, 
            "rat": 0, 
            "surv": 1, 
            "self": 0,
            "variants": [
                {
                    "template": "a {emphasiser}security-focused and cautious {responder_noun}",
                    "tradrat_framing": None, 
                    "survself_framing": "identity"
                },
                {
                    "template": "a {responder_noun} who values security and stability",
                    "tradrat_framing": None, 
                    "survself_framing": "preference"
                },
        ],
    },
    "self-expression values": {
            "trad": 0, 
            "rat": 0, 
            "surv": 0, 
            "self": 1,
            "variants": [
                {
                    "template": "a {emphasiser}self-expressive and open {responder_noun}",
                    "tradrat_framing": None, 
                    "survself_framing": "identity"
                },
                {
                    "template": "a {responder_noun} who values self-expression and individual freedom",
                    "tradrat_framing": None, 
                    "survself_framing": "preference"
                },
        ],
    },
    "traditional and survival values": {
            "trad": 1, 
            "rat": 0, 
            "surv": 1, 
            "self": 0,
            "variants": [
                {
                    "template": "a {emphasiser}traditional, security-focused and cautious {responder_noun}",
                    "tradrat_framing": "identity", 
                    "survself_framing": "identity"
                },
                {
                    "template": "a {responder_noun} who values tradition, faith, security and stability",
                    "tradrat_framing": "preference", 
                    "survself_framing": "preference"
                },
                {
                    "template": "a {emphasiser}traditional {responder_noun} who values security and stability",
                    "tradrat_framing": "identity", 
                    "survself_framing": "preference"
                },
                {
                    "template": "a {emphasiser}security-focused and cautious {responder_noun} who values tradition and faith",
                    "tradrat_framing": "preference", 
                    "survself_framing": "identity"
                },
        ],
    },
    "traditional and self-expression values": {
        "trad": 1, 
        "rat": 0, 
        "surv": 0, 
        "self": 1,
        "variants": [
            {
                "template": "a {emphasiser}traditional, open and self-expressive {responder_noun}",
                "tradrat_framing": "identity", 
                "survself_framing": "identity"
            },
            {
                "template": "a {responder_noun} who values tradition, faith, self-expression and individual freedom",
                "tradrat_framing": "preference", 
                "survself_framing": "preference"
            },
            {
                "template": "a {emphasiser}traditional {responder_noun} who values self-expression and individual freedom",
                "tradrat_framing": "identity", 
                "survself_framing": "preference"
            },
            {
                "template": "a {emphasiser}self-expressive and open {responder_noun} who values tradition and faith",
                "tradrat_framing": "preference", 
                "survself_framing": "identity"
            },
        ],
    },

    "secular-rational and survival values": {
        "trad": 0, 
        "rat": 1, 
        "surv": 1, 
        "self": 0,
        "variants": [
            {
                "template": "a {emphasiser}modern, secular, security-focused and cautious {responder_noun}",
                "tradrat_framing": "identity", 
                "survself_framing": "identity"
            },
            {
                "template": "a {responder_noun} who values reason over tradition, security and stability",
                "tradrat_framing": "preference", 
                "survself_framing": "preference"
            },
            {
                "template": "a {emphasiser}modern and secular {responder_noun} who values security and stability",
                "tradrat_framing": "identity", 
                "survself_framing": "preference"
            },
            {
                "template": "a {emphasiser}security-focused and cautious {responder_noun} who values reason over tradition",
                "tradrat_framing": "preference", 
                "survself_framing": "identity"
            },
        ],
    },
    "secular-rational and self-expression values": {
        "trad": 0, 
        "rat": 1, 
        "surv": 0, 
        "self": 1,
        "variants": [
            {
                "template": "a {emphasiser}modern, secular, open and self-expressive {responder_noun}",
                "tradrat_framing": "identity", 
                "survself_framing": "identity"
            },
            {
                "template": "a {responder_noun} who values reason, self-expression and individual freedom over tradition",
                "tradrat_framing": "preference", 
                "survself_framing": "preference"
            },
            {
                "template": "a {emphasiser}modern and secular {responder_noun} who values self-expression and individual freedom",
                "tradrat_framing": "identity", 
                "survself_framing": "preference"
            },
            {
                "template": "a {emphasiser}self-expressive and open {responder_noun} who values reason over tradition",
                "tradrat_framing": "preference", 
                "survself_framing": "identity"
            },
    ],
    },
}

EMPHASISERS = ["deeply", "strongly", "very", "greatly"]  
RESPONDER_NOUNS = ["person", "individual"]


# ---------------------------------------------------------------------------
# Layer 2: one prompt = one row. Store the prompt characteristics in dataclass
# ---------------------------------------------------------------------------
@dataclass
class SystemPrompt:
    prompt_id: str
    position: str
    responder_noun: str
    tradrat_framing: str | None
    survself_framing: str | None
    emphasiser: str | None
    value_trad: int
    value_rat: int
    value_surv: int
    value_self: int
    value_string: str
    full_system_prompt: str


# ---------------------------------------------------------------------------
# Layer 3: generate the full set of system prompt variants
# ---------------------------------------------------------------------------
def build_prompt_set(positions, emphasisers, responder_nouns, vocab=VALUE_POSITIONING):
    rows = []
    for position in positions:
        entry = vocab[position]
        for v_idx, variant in enumerate(entry["variants"]):
            template = variant["template"]
            has_emph_slot = "{emphasiser} " in template

            # emphasiser only applies where the template grammatically allows it
            emph_options = ([None] + emphasisers) if has_emph_slot else [None]
            for noun in responder_nouns:
                for emph in emph_options:
                    value_string = template.format(
                        responder_noun=noun,
                        emphasiser=(f"{emph}" if emph else ""),
                    )
                    full_system_prompt = f"You are {value_string} responding to the following survey question."
                    prompt_id = f"{position}_v{v_idx}_{noun}_{emph or 'none'}"
                    rows.append(SystemPrompt(
                        prompt_id=prompt_id,
                        position=position, responder_noun=noun,
                        tradrat_framing=variant["tradrat_framing"],
                        survself_framing=variant["survself_framing"],
                        emphasiser=emph,
                        value_trad=entry["trad"], value_rat=entry["rat"],
                        value_surv=entry["surv"], value_self=entry["self"],
                        value_string=value_string,
                        full_system_prompt=full_system_prompt
                    ))
    return rows


# ---------------------------------------------------------------------------
# Build system prompt set. Export to csv for eye-ball check
# ---------------------------------------------------------------------------
system_prompts = build_prompt_set(
    positions=list(VALUE_POSITIONING.keys()),
    emphasisers=EMPHASISERS,
    responder_nouns=RESPONDER_NOUNS,
)

system_prompt_df = pd.DataFrame(asdict(p) for p in system_prompts)
# system_prompt_df.to_csv("system_prompts.csv", index=False)




# ---------------------------------------------------------------------------
# Now generate the full prompt set
# ---------------------------------------------------------------------------

question_prompt_df = pd.read_csv("csv_files/wvs_questions.csv", sep=',')

combined_prompt_df = system_prompt_df.merge(question_prompt_df, how="cross")
combined_prompt_df["combined_prompt"] = [sp + '\n' + qp for sp, qp in zip(combined_prompt_df['full_system_prompt'], combined_prompt_df['question_prompt'])]
combined_prompt_df["prompt_id"] = combined_prompt_df["prompt_id"] + "_" + combined_prompt_df["wvs_qn_id"]
combined_prompt_df.to_csv("csv_files/combined_prompts.csv", index=False)


