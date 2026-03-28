import nltk
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# Download NLTK data
nltk.download('stopwords')
nltk.download('wordnet')


# Preprocessing functionality

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()


def preprocess_text(text):
    """Clean and normalize a document string."""
    if not text:
        return ""
    # 1. Lowercase
    text = text.lower()
    # 2. Remove punctuation (keep only letters, numbers, spaces)
    text = re.sub(r'[^\w\s]', ' ', text)
    # 3. Split into words and filter
    words = text.split()
    # 4. Remove stopwords and lemmatize
    processed = [
        lemmatizer.lemmatize(word)
        for word in words
        if word not in stop_words and len(word) > 1
    ]
    # 5. Return as space-separated string
    return " ".join(processed)


def preprocess_line(line):
    """
    Process a single line: lowercasing, punctuation removal,
    stopword removal, lemmatization.
    Returns a list of cleaned tokens.
    """
    if not line:
        return []
    # 1. Lowercase
    line = line.lower()
    # 2. Remove punctuation (keep letters, digits, spaces)
    line = re.sub(r'[^\w\s]', ' ', line)
    # 3. Split into words
    words = line.split()
    # 4. Remove stopwords and lemmatize
    tokens = []
    for w in words:
        if w not in stop_words and len(w) > 1:
            tokens.append(lemmatizer.lemmatize(w))

    # Return a list of tokens
    return tokens
