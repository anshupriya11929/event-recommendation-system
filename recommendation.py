import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nlp_utils import preprocess_text
# Load dataset
df = pd.read_csv("events.csv")

# Combine features
df["combined"] = (
    df["event_name"] + " " +
    df["category"] + " " +
    df["description"] + " " +
    df["tags"]
)
df["combined"] = df["combined"].apply(preprocess_text)

# Convert text to vectors
vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    max_features=5000
)
tfidf_matrix = vectorizer.fit_transform(df["combined"])

# Compute similarity
similarity = cosine_similarity(tfidf_matrix)


def recommend_events(user_interest):
    user_vec = vectorizer.transform([user_interest])
    scores = cosine_similarity(user_vec, tfidf_matrix).flatten()

    df["score"] = scores
    recommended = df.sort_values(by="score", ascending=False)

    return recommended.head(5).to_dict(orient="records")