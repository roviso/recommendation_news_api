import psycopg2
import numpy as np
import psycopg2.extras as extras
import pandas as pd
import pickle
from preprocessor import preprocessor
from config import pathconfig
import ast

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
    if pathconfig.PRE_PKL_PATH.is_file():
        pre = load_pkl(pathconfig.PRE_PKL_PATH)
        print('Successfully Loaded Pickle file')
    else:
        print("NO PICKLE FILE FOUND SAD :(")


    hostname = 'localhost'
    username = 'ravi'
    password = 'techprixa1234' # your password
    database = 'news_recommendation_dev'

    connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)

    article_df = pre.df[['article_id','url','head_image','heading','date','content','additional_images','source','label']]

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