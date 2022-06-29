import sys
from os import PathLike
from pathlib import Path
from typing import Dict, Union

import pandas as pd  # type: ignore
from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore

from apis.keyword.api.extract_keywords.extract import COUNT_VEC_KWARGS
# from api.extract_keywords.extract import COUNT_VEC_KWARGS

TFIDF_VEC_KWARGS: Dict = {
    **COUNT_VEC_KWARGS,
    'min_df': 2,
}


def train_idfs_from_csv(
        csv_filename: Union[str, PathLike]) -> Dict[str, float]:
    """
    Trains idf values from the supplied csv dataset.

    # Arguments
        csv_filename: str | PathLike, Path to the csv file.

    # Returns
        word_idf: dict[str, float], A dict containing the word-wise idf values.
    """

    csv_file: Path = Path(csv_filename)
    train_texts: pd.DataFrame = pd.read_csv(csv_file,
                                            header=0,
                                            names=['heading', 'content'])
    train_texts['text'] = (train_texts['heading'] + ' ' +
                           train_texts['content'])

    tfidf_vec = TfidfVectorizer(**TFIDF_VEC_KWARGS)
    tfidf_vec.fit(train_texts['text'].tolist())

    return dict(zip(tfidf_vec.get_feature_names_out(), tfidf_vec.idf_))


