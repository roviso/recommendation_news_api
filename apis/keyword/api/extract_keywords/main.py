#!/usr/bin/env python

import json
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, Iterable, Mapping, Optional

from extract_keywords.extract import extract_keywords
from extract_keywords.train import train_idfs_from_csv

IDFS_JSON_PATH = Path(
    Path(__file__).parents[2], 'datasets', 'idfs',
    'trained_idfs.json').resolve()


def main(args: Optional[Iterable[str]] = None):
    if args is None:
        args = sys.argv[1:]

    arguments: Mapping = _parse_arguments(args)

    word_idfs: Mapping[str, float]

    if 'train_csv' in arguments:
        if not arguments['train_csv'].endswith('.csv'):
            raise ValueError(
                'extract_keywords: error: TRAIN_CSV must be a .csv file')

        word_idfs = train_idfs_from_csv(arguments['train_csv'])

        if not IDFS_JSON_PATH.parents[1].is_dir():
            IDFS_JSON_PATH.parents[1].mkdir()

        if not IDFS_JSON_PATH.parent.is_dir():
            IDFS_JSON_PATH.parent.mkdir()

        try:
            with open(IDFS_JSON_PATH, 'w', encoding='utf-8') as file:
                json.dump(word_idfs, file)
        except PermissionError as err:
            raise SystemExit('extract_keywords: error: could not write file',
                             IDFS_JSON_PATH, 'due to bad permissions') from err
        else:
            print('Successfully wrote trained idf values into', IDFS_JSON_PATH)
    elif 'idf_json' in arguments:
        if not arguments['idf_json'].endswith('.json'):
            raise ValueError(
                'extract_keywords: error: idf_json must be a .json file')

        if not arguments['text_txt'].endswith('.txt'):
            raise ValueError(
                'extract_keywords: error: texts_txt must be a .txt file')

        try:
            with open(arguments['idf_json'], 'r', encoding='utf-8') as file:
                word_idfs = json.load(file)
        except FileNotFoundError as err:
            raise SystemExit(
                'extract_keywords: error:'
                f'file {arguments["idf_json"]} not found') from err
        else:
            print('Successfully loaded idf values from',
                  Path(arguments['idf_json']).resolve())

        try:
            with open(arguments['text_txt'], 'r', encoding='utf-8') as file:
                corpus = [file.read()]
        except FileNotFoundError as err:
            raise SystemExit(
                'extract_keywords: error:'
                f'file {arguments["text_txt"]} not found') from err
        else:
            print(extract_keywords(corpus, word_idfs, arguments['k']))


def _parse_arguments(args: Iterable[str]) -> Dict:
    parser: ArgumentParser = ArgumentParser(
        prog='keywords',
        description='A program to extract keywords from a nepali text.')

    subparsers = parser.add_subparsers(help='available sub-commands')

    parser_extract: ArgumentParser = subparsers.add_parser(
        'extract', help='extract keywords from the provided texts')
    parser_extract.add_argument(
        'idf_json',
        type=str,
        help='.json file containing the pretrainied idf values')
    parser_extract.add_argument(
        'text_txt',
        type=str,
        help='.txt file containing the text to extract keywords from')
    parser_extract.add_argument('-k',
                                type=int,
                                default=20,
                                required=False,
                                help='number of keywords to extract')

    parser_train: ArgumentParser = subparsers.add_parser(
        'train', help='train the idf value from the provided dataset')
    parser_train.add_argument(
        'train_csv',
        type=str,
        help='.csv file containing the data for training the idf value')

    return vars(parser.parse_args(args))  # type: ignore


if __name__ == '__main__':
    main()
