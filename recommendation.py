import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from nlp_utils import preprocess_text


# ----------------------------------
# Load Dataset
# ----------------------------------
df = pd.read_csv("events.csv")


# ----------------------------------
# Combine Event Features
# ----------------------------------
df["combined"] = (
    df["event_name"].fillna("") + " " +
    df["category"].fillna("") + " " +
    df["description"].fillna("") + " " +
    df["tags"].fillna("")
)

df["combined"] = df["combined"].apply(
    preprocess_text
)


# ----------------------------------
# TF-IDF Vectorization
# ----------------------------------
vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    max_features=5000
)

tfidf_matrix = vectorizer.fit_transform(
    df["combined"]
)


# ----------------------------------
# Matching Keywords
# ----------------------------------
def get_matching_keywords(
    user_interest,
    event_tags
):

    user_words = set(
        preprocess_text(
            user_interest
        ).split()
    )

    event_words = set()

    for tag in str(event_tags).split(","):

        event_words.update(
            preprocess_text(tag).split()
        )

    matches = user_words.intersection(
        event_words
    )

    return ", ".join(matches)


# ----------------------------------
# Recommendation Function
# ----------------------------------
def recommend_events(
    user_interest,
    top_n=10
):

    if not user_interest:
        return []

    # Handle multiple interests
    user_interest = user_interest.replace(
        ",",
        " "
    )

    processed_interest = preprocess_text(
        user_interest
    )

    # User vector
    user_vec = vectorizer.transform(
        [processed_interest]
    )

    # Similarity scores
    scores = cosine_similarity(
        user_vec,
        tfidf_matrix
    ).flatten()

    results = df.copy()

    results["score"] = (
        scores * 100
    ).round(2)

    # Matching explanation
    results["matched_keywords"] = (
        results["tags"]
        .apply(
            lambda x:
            get_matching_keywords(
                user_interest,
                x
            )
        )
    )

    # Remove weak matches
    results = results[
        results["score"] > 5
    ]

    # Sort by relevance
    results = results.sort_values(
        by="score",
        ascending=False
    )

    return results.head(
        top_n
    ).to_dict(
        orient="records"
    )