import json
from os import PathLike
from pathlib import Path
from typing import List, Mapping

from fastapi import Body, FastAPI, Query

# from api.extract_keywords.extract import extract_keywords
# from api.extract_keywords.train import train_idfs_from_csv

from apis.keyword.api.extract_keywords.extract import extract_keywords
from apis.keyword.api.extract_keywords.train import train_idfs_from_csv

DATASET_CSV_PATH: Path = Path(
    Path(__file__).parent, 'datasets', 'news', 'filtered_all.csv').resolve()
TRAINED_IDFS_JSON_PATH: Path = Path(
    Path(__file__).parent, 'datasets', 'idfs', 'trained_idfs.json').resolve()

keywordApi = FastAPI()


@keywordApi.get('/')
async def root():
    return {'message': 'Keyword extraction from text'}


@keywordApi.post('/')
async def extract_keywords_from(texts: List[str] = Body(...),
                                k: int = Query(20)):
    word_idfs: Mapping[str, float]

    if not TRAINED_IDFS_JSON_PATH.is_file():
        print(f"Trained IDF: {TRAINED_IDFS_JSON_PATH} NOT FOUND")
        print("Training From {DATASET_CSV_PATH}")
        word_idfs = train_idfs_from_csv(DATASET_CSV_PATH)
        print(word_idfs, 666666666666666666666666666666666)
    else:
        print(f"USING Trained IDF: {TRAINED_IDFS_JSON_PATH}")
        with open(TRAINED_IDFS_JSON_PATH, 'r', encoding='utf-8') as json_file:
            word_idfs = json.load(json_file)

    return {
        'message': 'Extracted keywords',
        'keywords': extract_keywords(texts, word_idfs, k)
    }
