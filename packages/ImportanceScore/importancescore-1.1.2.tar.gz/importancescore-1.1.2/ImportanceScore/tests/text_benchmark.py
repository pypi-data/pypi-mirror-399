import random
import time
from typing import List, Dict, Tuple

from flashtext import KeywordProcessor
from sklearn.feature_extraction.text import CountVectorizer


# --- Data Generation ---

def generate_test_data(num_rows: int, num_phrases: int) -> Tuple[Dict[str, int], List[str]]:
    """Generates a set of phrases with scores and a list of text rows for testing."""

    # Generate phrases and scores
    base_phrases = ["national park", "state park", "town park", "regional park", "forest",
                    "preserve", "monument", "seashore", "lake", "river", "mountain", "peak",
                    "restaurant", "cafe", "pub", "deli", "fast food", "nature reserve",
                    "protected area"]

    phrases = {f"{random.choice(base_phrases)} {i}" for i in range(num_phrases)}
    # Ensure our key test phrases are present for cumulative scoring demo
    phrases.add("national park")
    phrases.add("park")

    phrases_with_scores = {phrase: random.randint(5, 100) for phrase in phrases}
    phrases_with_scores["national park"] = 100
    phrases_with_scores["park"] = 20

    # Generate text rows
    sentences = ["Welcome to the beautiful {p}.", "This is the famous {p} area.",
                 "The sign says {p}, a local treasure.", "Let's go hiking in the {p} tomorrow.",
                 "There is no parking in the red zone.", "I am just parking my car here.",
                 "The grand yellowstone national park is a must-see.",
                 "This is a test sentence with no keywords.", ]

    rows = [random.choice(sentences).format(p=random.choice(list(phrases_with_scores.keys()))) for _
            in range(num_rows)]
    # Ensure at least one complex case
    rows.append("the yellowstone national park is a large park.")

    print(
        f"Generated {len(rows)} rows and {len(phrases_with_scores)} unique phrases for benchmark."
    )
    return phrases_with_scores, rows


# --- Scoring Implementation: FlashText ---

def score_with_flashtext(phrases_with_scores: Dict[str, int], rows: List[str], strategy: str) -> \
        Tuple[int, int, List]:
    """Scores rows using the FlashText library."""
    keyword_processor = KeywordProcessor(case_sensitive=False)

    # For FlashText, we can associate the weight directly with the keyword
    for phrase, score in phrases_with_scores.items():
        keyword_processor.add_keyword(phrase, (phrase, score))

    total_score = 0
    matched_rows_count = 0
    all_matches = []

    for row in rows:
        found_keywords = keyword_processor.extract_keywords(row)
        row_score = 0

        if found_keywords:
            matched_rows_count += 1

            # found_keywords is a list of tuples: [('phrase', score), ...]
            if strategy == 'CUMULATIVE':
                row_score = sum(score for _, score in found_keywords)

            elif strategy == 'HIGHEST_WEIGHT':
                row_score = max(score for _, score in found_keywords)

            elif strategy == 'LONGEST_MATCH':
                # Get the tuple ('phrase', score) corresponding to the longest phrase
                longest_match = max(found_keywords, key=lambda item: len(item[0]))
                row_score = longest_match[1]  # The score is the 2nd element

        total_score += row_score
        all_matches.append(found_keywords if found_keywords else [])

    return total_score, matched_rows_count, all_matches


# --- Scoring Implementation: scikit-learn ---

def score_with_sklearn(phrases_with_scores: Dict[str, int], rows: List[str], strategy: str) -> \
        Tuple[int, int, List]:
    """Scores rows using scikit-learn's CountVectorizer."""

    phrases = list(phrases_with_scores.keys())
    if not phrases:
        return 0, 0, [[] for _ in rows]

    # To simulate substring matching, we must use a character-based analyzer.
    # 'char_wb' creates n-grams only from text inside word boundaries.
    min_len = min(map(len, phrases))
    max_len = max(map(len, phrases))

    vectorizer = CountVectorizer(
        vocabulary=phrases, lowercase=True, analyzer='char_wb',
        # This is key for substring-like matching
        ngram_range=(min_len, max_len)
    )

    X = vectorizer.fit_transform(rows)
    feature_names = vectorizer.get_feature_names_out()

    # Create a mapping of feature name to its score for quick lookup
    weights_map = {name: phrases_with_scores.get(name, 0) for name in feature_names}

    total_score = 0
    matched_rows_count = 0
    all_matches = []

    # Iterate through the sparse matrix to calculate scores row by row
    for i in range(X.shape[0]):
        row_vector = X.getrow(i)
        row_score = 0
        found_keywords = []

        if row_vector.nnz > 0:  # If there are any matches in this row
            matched_rows_count += 1

            # Get the actual phrases and their scores that were found
            found_indices = row_vector.indices
            found_phrases = [feature_names[j] for j in found_indices]
            found_keywords = [(phrase, weights_map[phrase]) for phrase in found_phrases]

            if strategy == 'CUMULATIVE':
                row_score = sum(score for _, score in found_keywords)

            elif strategy == 'HIGHEST_WEIGHT':
                row_score = max(score for _, score in found_keywords)

            elif strategy == 'LONGEST_MATCH':
                longest_match = max(found_keywords, key=lambda item: len(item[0]))
                row_score = longest_match[1]

        total_score += row_score
        all_matches.append(found_keywords)

    return total_score, matched_rows_count, all_matches


# --- Main Benchmark Runner ---

def run_benchmark(
        name: str, scoring_func, phrases_with_scores: Dict[str, int], rows: List[str],
        strategy: str, print_matches: bool = False
):
    """Generic function to run and time a scoring implementation."""
    print(f"\n--- Benchmarking: {name} (Strategy: {strategy}) ---")

    start_time = time.perf_counter()
    total_score, matched_rows, all_matches = scoring_func(phrases_with_scores, rows, strategy)
    end_time = time.perf_counter()

    duration = end_time - start_time

    print(f"    Time to finish: {duration:.6f} seconds")
    print(f"  # of Rows Matched: {matched_rows}")
    print(f"        Total Score: {total_score}")

    if print_matches:
        print("\n    Sample Matches (first 5 and last 5):")
        # Find some rows that actually had matches to show
        matched_examples = [(i, m) for i, m in enumerate(all_matches) if m]

        for i, matches in matched_examples[:5]:
            print(f"      Row {i}: '{rows[i][:70]}...' -> {matches}")
        if len(matched_examples) > 10:
            print("      ...")
        for i, matches in matched_examples[-5:]:
            print(f"      Row {i}: '{rows[i][:70]}...' -> {matches}")


if __name__ == "__main__":
    # --- Configuration ---
    NUM_ROWS = 100_000
    NUM_PHRASES = 500
    PRINT_MATCHES_FOR_VERIFICATION = True

    phrases_with_scores, rows = generate_test_data(NUM_ROWS, NUM_PHRASES)

    scoring_strategies = ['CUMULATIVE', 'HIGHEST_WEIGHT', 'LONGEST_MATCH']

    for strategy in scoring_strategies:
        run_benchmark(
            name="FlashText", scoring_func=score_with_flashtext,
            phrases_with_scores=phrases_with_scores, rows=rows, strategy=strategy,
            print_matches=PRINT_MATCHES_FOR_VERIFICATION
        )

        run_benchmark(
            name="scikit-learn (CountVectorizer)", scoring_func=score_with_sklearn,
            phrases_with_scores=phrases_with_scores, rows=rows, strategy=strategy,
            print_matches=PRINT_MATCHES_FOR_VERIFICATION
        )
        print("\n" + "=" * 80)
