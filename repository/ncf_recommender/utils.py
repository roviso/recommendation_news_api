import pandas as pd
import torch
import torch.nn as nn
from tqdm import tqdm
from repository.ncf_recommender.dataset_loader import Test_Rating_dataSet
from sharedcount import SharedCountApi
import ast
from itertools import islice
import operator

# Configer converts a dictionary to class:
class configer(object):
    def __init__(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])


def str_to_list(list_string):
  return ast.literal_eval(list_string)


def eval_sample_list(user_list,url_list,pre,model):
  user_df = pd.DataFrame({'user': user_list})
  article_df = pd.DataFrame({'article':url_list})
  test_ds = Test_Rating_dataSet(user_df,article_df, pre.user_index_mapping, pre.url_to_index_and_labels_dict)
  test_dl = torch.utils.data.DataLoader(test_ds, batch_size=1, shuffle=False,)
  url_to_rating = {}
  device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

  for _, (user_name,user,article_url,url_index,labels,Dominant_Topic) in tqdm(enumerate(test_dl)):
      user = user[0].unsqueeze(1)
      # print('keywords before: ',keywords)
      # keywords = torch.tensor([ str_to_list(key) for key in keywords])
      # print('keywords after: ',keywords,keywords.shape)
      user,url_index, label,Dominant_Topic = user.to(device),url_index.to(device),labels.to(device),Dominant_Topic.to(device)
      # print('user shape: ',user.shape,'keywords shape:',keywords.shape,'label shape:',label.shape)
      prediction, user_embed_MLP, article_embed_MLP = model( user, url_index,label,Dominant_Topic)
        
      for i,url in enumerate(article_url[0]):
          
          url_r= {url : float(prediction[i])}
          url_to_rating.update(url_r)

  return url_to_rating


def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))

    
def get_top_20(user_name,url_list,pre ,model):
    user_list = [user_name,]
    url_to_rating = eval_sample_list(user_list,url_list,pre,model)
    sorted_top_url = dict( sorted(url_to_rating.items(), key=operator.itemgetter(1),reverse=True))
#   top_20 = take(20, sorted_top_url.items()) # gives url with scores
    top_20 = take(20, sorted_top_url.keys()) # gives url only
    return top_20

def get_top_100(user_name,url_list,pre ,model):
    user_list = [user_name,]
    url_to_rating = eval_sample_list(user_list,url_list,pre,model)
    sorted_top_url = dict( sorted(url_to_rating.items(), key=operator.itemgetter(1),reverse=True))
#   top_20 = take(20, sorted_top_url.items()) # gives url with scores
    top_100 = take(100, sorted_top_url.keys()) # gives url only
    return top_100


def content_filter(content):
    new_content_list = []
    present_index = 0

    content = list(filter(None, content))
    while present_index < len(content)-2:
    #     print(present_index)
        if len(content[present_index]) > 350:
            new_content_list.append(content[present_index][:350])
            new_content_list.append(content[present_index][350:])
            present_index += 1 
        
        elif len(content[present_index]) + len(content[present_index + 1]) + len(content[present_index + 2])<= 350:
            new_content = content[present_index] + ' ' + content[present_index + 1] + ' ' + content[present_index + 2]
            new_content_list.append(new_content)
            present_index += 3
        
        elif len(content[present_index]) + len(content[present_index + 1]) <= 350:
            new_content = content[present_index] + ' ' + content[present_index + 1]
            new_content_list.append(new_content)
            present_index += 2
        else:
            new_content_list.append(content[present_index])
            present_index += 1
            
    while present_index >= len(content)-2 and present_index< len(content):
        if present_index == len(content)-1:
            new_content_list.append(content[present_index])
            present_index += 1
        elif len(content[present_index]) + len(content[present_index + 1]) <= 350:
            new_content = content[present_index] + ' ' + content[present_index + 1]
            new_content_list.append(new_content)
            present_index += 2
        else:
            new_content_list.append(content[present_index])
            present_index += 1
    
    return new_content_list

    
def get_shared_count(api_key, response_url):
    sharedCountApiInstance = SharedCountApi(api_key)
    urlGetResponse = sharedCountApiInstance.get(response_url)
    fb_info = urlGetResponse['Facebook']
    shares = fb_info['share_count']
    likes = fb_info['total_count']
    return likes,shares

def context_giver(top_20,pre):
    return_val = []
    for item in top_20:
        item_df = pre.df[pre.df.url == item].iloc[0]
        # try:
        #     api_key  = '997ee09718596404b3e6edca59da47cf7d391f20'
        #     likes,shares = get_shared_count(api_key, item_df.url)
        # except:
        #     try:
        #         api_key  = 'dbc159c8dcf39265dd0a5cde28cd603e0b62ced7'
        #         likes,shares = get_shared_count(api_key, item_df.url)
        #     except:
        #         try:
        #             api_key  = '42c47e38ba96c8eb6f283a09a0ace27d44639466'
        #             likes,shares = get_shared_count(api_key, item_df.url)
        #         except:
        #             try:
        #                 api_key  = '43238bc406280d3abc1351bf24257008924a2ca3'
        #                 likes,shares = get_shared_count(api_key, item_df.url)
        #             except:
        #                 try:
        #                     api_key  = '92c43723aa3d1ecf90a507861fcf8b227b121c38'
        #                     likes,shares = get_shared_count(api_key, item_df.url)
        #                 except:
        #                     try:
        #                         api_key  = '1bcfcf7c6de2e619003d9d106a7763c446b48c34'
        #                         likes,shares = get_shared_count(api_key, item_df.url)
        #                     except:
        likes = 0
        shares = 0

        item_val = {
            "url": item_df.url,
            "head_image": item_df.head_image,
            "heading": item_df.heading,
            "date": item_df.date.split()[0],
            "label": item_df.label,
            # "content": content_filter(ast.literal_eval(item_df.content)),
            "content": list(filter(None, ast.literal_eval(item_df.content))),
            "additional_img": ast.literal_eval(item_df.additional_images),
            "source": item_df.source,
            "author": item_df.author,
            "author_img": item_df.author_img,
            "likes": likes,
            "shares": shares,
        }
        return_val.append(item_val)
    return return_val