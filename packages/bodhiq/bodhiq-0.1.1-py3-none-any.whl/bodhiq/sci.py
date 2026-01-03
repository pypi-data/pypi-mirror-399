from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

memories = ["my name is aman", "buy milk", "go to gym"]
vectorizer = TfidfVectorizer().fit(memories)
vecs = vectorizer.transform(memories)

query_vec = vectorizer.transform([input()])
sims = cosine_similarity(query_vec, vecs).flatten()

best_idx = sims.argmax()
print(memories[best_idx])
# -> "my name is aman"

