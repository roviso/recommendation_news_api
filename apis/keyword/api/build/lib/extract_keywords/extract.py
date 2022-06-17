from pathlib import Path
from typing import Dict, Iterable, List, Mapping
from unicodedata import category

import numpy as np
from nltk.corpus import stopwords  # type: ignore
from scipy.sparse import spmatrix  # type: ignore
from sklearn.feature_extraction.text import CountVectorizer  # type: ignore

COUNT_VEC_KWARGS: Dict = {
    'decode_error': 'ignore',
    'lowercase': False,
    'ngram_range': (1, 1),
    'max_features': 20000,
    'stop_words': stopwords.words('nepali'),
    'tokenizer':
    lambda text: [_strip_punctuations(word) for word in text.split()],
}


def extract_keywords(corpus: Iterable[str], word_idf: Mapping[str, float],
                     n_kwds: int) -> List[List[str]]:
    """
    Extracts keywords from the given corpus using pretrained idf values.

    # Arguments
        corpus: Iterable[str], A list-like containing documents as raw strings.
        word_idf: Mapping[str, float], A dict-like containing word-wise
                  idf values.
        n_kwds: int, The number of keywords to extract from each document.

    # Returns
        keywords: list[list[str]], A list containing lists of keywords
                  per document.
    """
    top_keywords: List[List[str]] = []

    for document in corpus:
        count_vec: CountVectorizer = CountVectorizer(**COUNT_VEC_KWARGS)
        word_counts: spmatrix = count_vec.fit_transform([document])
        total_words: int = np.sum(word_counts)

        words: np.ndarray = count_vec.get_feature_names_out()

        keywords: List[List[str]] = []
        tfidf_scores: List[List[float]] = []
        prev_x: int = 0
        kwds: List[str] = []
        scores: List[float] = []

        for idx_x, idx_y in zip(*word_counts.nonzero()):
            if words[idx_y] not in word_idf:
                continue

            if prev_x != idx_x:
                keywords.append(kwds)
                tfidf_scores.append(scores)
                kwds = []
                scores = []
                prev_x = idx_x
            else:
                kwds.append(words[idx_y])
                scores.append((word_counts[idx_x, idx_y] / total_words) *
                              word_idf[words[idx_y]])

        # Add leftover keywords scores at the end and compute top indices
        final_keywords: np.ndarray = np.array([*keywords, kwds])
        top_indices: np.ndarray = np.array([*tfidf_scores, scores],
                                           dtype=np.float64).argpartition(
                                               kth=-n_kwds, axis=1)[:,
                                                                    -n_kwds:]

        for i, indices in enumerate(top_indices):
            top_keywords.append(list(final_keywords[i, indices]))

    return top_keywords


def _strip_punctuations(word):
    return ''.join(ch for ch in word if not category(ch).startswith('P'))
