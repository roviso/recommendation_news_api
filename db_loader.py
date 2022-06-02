import psycopg2
import numpy as np
import psycopg2.extras as extras
import pandas as pd
import pickle
from preprocessor import preprocessor
from config import pathconfig
import ast
import secrets

def str_to_list(list_string):
    return ast.literal_eval(list_string)

def load_pkl(pkl_file):
    with open(pkl_file, 'rb') as inp:
        pickled_obj = pickle.load(inp)
    return pickled_obj

def execute_values(conn, df, table):
  
    tuples = [tuple(x) for x in df.to_numpy()]
  
    cols = ','.join(list(df.columns))
    # SQL query to execute
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    cursor = conn.cursor()
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("the dataframe is inserted")
    cursor.close()


def load_model_data():    
    # LOADING PRE PICKLE FILE
    if pathconfig.PRE_PKL_PATH.is_file():
        pre = load_pkl(pathconfig.PRE_PKL_PATH)
        print('Successfully Loaded Pickle file')
    else:
        print("NO PICKLE FILE FOUND SAD :(")

    # ESTABLISHING CONNECTION TO DATABASE
    hostname = 'localhost'
    username = 'postgres'
    password = 'techprixa1234' # your password
    database = 'news_recommendation_dev'

    connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)

    # LOADING AUTHOR INFORMATION
    print("============= LOADING AUTHOR ===============================")

    author_df = pre.df[['author','author_img','source']]

    author_df.drop_duplicates(subset=['author'], keep='last', inplace=True)

    author_id_dict = {author: secrets.token_urlsafe(32) for author in author_df.author.unique()}

    author_df['id'] = author_df.apply(lambda x: author_id_dict.get(x['author']), axis=1)

    author_df.rename(columns={"author": "author_name"}, inplace=True)


    execute_values(connection, author_df, 'author')

    # LOADING ARTICLE INFORMATION

    print("============= LOADING ARTICLE ===============================")
    article_df = pre.df[['article_id','url','head_image','heading','date','content','additional_images','source','label','author']]
    article_df['author_id'] = article_df.apply(lambda x: author_id_dict.get(x['author']), axis=1)
    article_df.drop('author', 1, inplace=True)

    views_df = article_df.pivot_table(columns=['article_id'], aggfunc='size')

    article_df['likes'] = 0
    article_df['shares'] = 0
    article_df['type'] = 'recommended'
    article_df['views'] = article_df.apply(lambda x: views_df.get(x['article_id']), axis=1)

    article_df['ignores'] = 0
    article_df['total_comments'] = 0
    article_df['bookmarks'] = 0

    article_df.drop_duplicates(subset=['article_id'], keep='last', inplace=True)

    article_df.rename(columns={"article_id": "id","additional_images": "additional_img"}, inplace=True)

    article_df['content'] = article_df['content'].apply(lambda x: str_to_list(x))

    article_df['additional_img'] = article_df['additional_img'].apply(lambda x: str_to_list(x))

    execute_values(connection, article_df, 'article')