from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Union
from unicodedata import category
import snowballstemmer
import numpy as np
from nltk.corpus import stopwords  # type: ignore
from scipy.sparse import spmatrix  # type: ignore
from sklearn.feature_extraction.text import CountVectorizer  # type: ignore
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import random

COUNT_VEC_KWARGS: Dict = {
    'decode_error': 'ignore',
    'lowercase': False,
    'ngram_range': (1, 1),
    'max_features': 20000,
    'stop_words': stopwords.words('nepali'),
    'tokenizer':
    # lambda text: [_strip_punctuations(word) for word in text.split()],
    lambda text: tokenizer(text)
}


TFIDF_VEC_KWARGS: Dict = {
    **COUNT_VEC_KWARGS,
    'min_df': 1,
}



STOP_WORD_LIST_PATH: Path = Path(
    Path(__file__).parent, 'non-potential-topic-word-list.txt').resolve()


stop_words = []
with open(STOP_WORD_LIST_PATH, 'r', encoding="utf8") as reader:
    for line in reader:
        line = line.strip('\n')
        stop_words.append(line)


stemmer = snowballstemmer.NepaliStemmer()
stopwords = set(stop_words)


def tokenizer(text): 
    tokenized_word = []
    

    stem_list = stemmer.stemWords(text.split())


    tokenized_word = list(filter(word_filter, stem_list))
    # final_tokenized_word = [word for word in tokenized_word if len(word)>3]

    return tokenized_word

def word_filter(stem_word):
    nepali_word = True
    # print('stem_word: ',stem_word)
    if len(stem_word) > 3:
        for letter in stem_word:
            if not 0x0090 <= ord(letter) <= 0x97F:
                nepali_word = False
            return nepali_word 
    else:
        return False 



def train_idfs(train_df) -> Dict[str, float]:
#         csv_filename: Union[str, PathLike]) -> Dict[str, float]:
    """
    Trains idf values from the supplied csv dataset.

    # Arguments
        csv_filename: str | PathLike, Path to the csv file.

    # Returns
        word_idf: dict[str, float], A dict containing the word-wise idf values.
    """

#     csv_file: Path = Path(csv_filename)
#     train_texts: pd.DataFrame = pd.read_csv(csv_file,
#                                             header=0,
#                                             names=['heading', 'content'])
#     train_texts['text'] = (train_texts['heading'] + ' ' +
#                            train_texts['content'])

    tfidf_vec = TfidfVectorizer(**TFIDF_VEC_KWARGS)
    tfidf_vec.fit(train_df['text'].tolist())

    return dict(zip(tfidf_vec.get_feature_names_out(), tfidf_vec.idf_))


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
                              float(word_idf[words[idx_y]]))

        # Add leftover keywords scores at the end and compute top indices
        
        try:
            temp_kwds = n_kwds
            final_keywords: np.ndarray = np.array([*keywords, temp_kwds])
            top_indices: np.ndarray = np.array([*tfidf_scores, scores],
                                           dtype=np.float64).argpartition(
                                               kth=-temp_kwds, axis=1)[:,
                                                                    -temp_kwds:]
            for i, indices in enumerate(top_indices):
                top_keywords.append(list(final_keywords[i, indices]))
        except:
            top_keywords.append(random.sample(list(corpus.split()),10))
    return top_keywords
