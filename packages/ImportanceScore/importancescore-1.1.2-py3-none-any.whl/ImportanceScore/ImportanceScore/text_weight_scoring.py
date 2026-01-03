# text_weight_scoring.py

from pathlib import Path
import re
import string
import sys
from typing import Dict, List, Tuple
import unicodedata

from flashtext import KeywordProcessor
import pandas as pd

from ImportanceScore.manifest import Manifest

def normalize_text(text: str) -> str:
    """
    Performs robust Unicode normalization and lowercasing on a string.
    """
    if not isinstance(text, str):
        return ''
    return unicodedata.normalize('NFKC', text).lower()

class _TextScorer:
    """
    A high-performance text scorer for 'contains' substring matching.
    """
    def __init__(self, phrases_with_scores: Dict[str, int]):
        """
        Initializes the scorer. Note: Punctuation exceptions are no longer
        needed here because pure punctuation is handled via Regex before this.
        """
        self.keyword_processor = KeywordProcessor(case_sensitive=True)

        # Standard non-word chars are fine now
        self.keyword_processor.non_word_characters = set(string.punctuation)

        for phrase, score in phrases_with_scores.items():
            self.keyword_processor.add_keyword(phrase, score)

    def __call__(self, text: str) -> int:
        if not text:
            return 0
        found_keywords = self.keyword_processor.extract_keywords(text, span_info=True)
        if not found_keywords:
            return 0
        # Longest match logic
        best_match = max(found_keywords, key=lambda item: (item[2] - item[1]))
        return best_match[0]


def apply_text_weights(
        df: pd.DataFrame, text_weight_columns: List[str], category: str,
        config_dir: str = "config", verbose: bool = True
) -> None:
    """
    Applies text-based weight scores using a hybrid Regex + FlashText approach.
    """
    for col in text_weight_columns:
        config_path = Path(config_dir) / f"{category}_{col}_weights.yml"
        log_msg(verbose, f" ➡️ Applying text weights from: {config_path}")

        try:
            contains_phrases, match_phrases = read_text_weights_config(config_path)
        except (FileNotFoundError, ValueError) as e:
            log_msg(True, f"\n   ❌ FATAL ERROR: {e}\n")
            sys.exit(1)

        score_col = f"{col}_score"

        if col not in df.columns:
            df[score_col] = 0
            log_msg(True, f"   Column '{col}' not found. Creating empty score column '{score_col}'.")
            continue

        df[score_col] = 0

        # Normalize once
        normalized_text_series = df[col].fillna('').apply(normalize_text)

        # --- STAGE 0: Punctuation / Non-Alphanumeric (Regex) ---
        # Identify "contains" rules that have NO alphanumeric characters (e.g. "(" or "-")
        # FlashText is bad at these, so we use Pandas str.contains
        punct_phrases = {p: w for p, w in contains_phrases.items() if not any(c.isalnum() for c in p)}

        if punct_phrases:
            for symbol, weight in punct_phrases.items():
                # We search on the NORMALIZED text to match the config keys
                mask = normalized_text_series.str.contains(re.escape(symbol), regex=True)
                df.loc[mask, score_col] += weight
                log_msg(verbose, f"   - Regex matched '{symbol}' in {mask.sum()} rows.")

            # Remove them from FlashText dict to prevent double processing/errors
            for symbol in punct_phrases:
                del contains_phrases[symbol]

        # --- STAGE 1: Exact Match (Highest Precedence) ---
        if match_phrases:
            normalized_match = {normalize_text(p): w for p, w in match_phrases.items()}
            for phrase, weight in normalized_match.items():
                # Note: This overwrites previous scores (like regex) if an exact match is found.
                # This logic assumes Exact Match is the final authority.
                mask = (normalized_text_series == phrase)
                df.loc[mask, score_col] = weight

        # --- STAGE 2: Contains (FlashText) ---
        if contains_phrases:
            normalized_contains = {normalize_text(p): w for p, w in contains_phrases.items()}

            # Only process rows that haven't been finalized by Exact Match
            # (We DO add to rows that only had Regex hits, unless Exact matched them too)
            # Logic: If current score is 0 OR it came from Stage 0, we can add FlashText score?
            # Current logic: If Exact Match hit, we are done. If not, we add FlashText.
            # But wait: FlashText replaces 0. It doesn't ADD to Stage 0.

            # FIX: We want FlashText to ADD to whatever is there (e.g. Regex score)
            # UNLESS Exact Match already set a score.
            # Actually, standard behavior is usually additive for "contains".

            scorer = _TextScorer(normalized_contains)
            contains_scores = normalized_text_series.apply(scorer)

            # Add FlashText scores to existing scores (which might include Stage 0 regex results)
            df[score_col] += contains_scores

        matches = (df[score_col] != 0).sum()
        log_msg(verbose, f"  ✅ Assigned text weights to '{score_col}' for {matches} rows.")

# ... (read_text_weights_config, log_msg, and schema remain unchanged) ...
def read_text_weights_config(path: Path) -> Tuple[Dict[str, int], Dict[str, int]]:
    """
    Reads a text weights YAML config file with 'contains' and 'match' keys.

    Args:
        path (Path): The path to the YAML configuration file.

    Returns:
        A tuple containing two dictionaries:
        - (contains_phrases: {phrase: weight})
        - (match_phrases: {phrase: weight})

    Raises:
        FileNotFoundError: If the specified configuration file does not exist.
        ValueError: If the configuration file is empty or malformed.
    """
    try:
        manifest = Manifest()
        config = manifest.load_config(
            path, text_weights_schema, root_node="text_weights", block_descriptor="description"
        )
    except FileNotFoundError:
        # Re-raise the exception to be caught by the calling function.
        # This makes the error fatal.
        raise FileNotFoundError(f"Text weight config not found at '{path}'")
    except Exception as e:
        # Wrap other potential parsing errors in a ValueError for clarity.
        raise ValueError(f"Could not read or parse config '{path}':\n  {e}")

    contains_phrases: Dict[str, int] = {}
    match_phrases: Dict[str, int] = {}

    for tier in config.get("text_weights", []):
        weight = tier.get("weight")
        if weight is None:
            continue

        for phrase in tier.get("contains", []):
            if phrase:
                contains_phrases[phrase] = weight

        for phrase in tier.get("match", []):
            if phrase:
                match_phrases[phrase] = weight

    if not contains_phrases and not match_phrases:
        # This should also be a fatal error, as an empty config is a mistake.
        raise ValueError(f"No phrases defined in 'contains' or 'match' blocks in {path}")

    return contains_phrases, match_phrases

def log_msg(verbose: bool, msg: str) -> None:
    if verbose:
        print(msg)


# The schema defining the structure of the YAML configuration file.
text_weights_schema = {
    "text_weights": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "weight": {"type": "integer", "required": True},
                "description": {"type": "string", "required": True, "empty": False},
                "contains": {
                    "type": "list", "required": False,
                    "schema": {"type": "string", "empty": False}
                },
                "match": {
                    "type": "list", "required": False,
                    "schema": {"type": "string", "empty": False}
                },
            },
        },
    }
}