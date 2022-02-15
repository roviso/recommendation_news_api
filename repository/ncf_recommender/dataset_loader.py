import numpy as np
import pandas as pd
from torch.utils.data import Dataset


class Rating_dataSet(Dataset):
    def __init__(self, user_df,url_df, user_fields, url_fields, y):
        self.user_df = user_df
        self.url_df = url_df
        self.user_fields = user_fields
        self.url_fields = url_fields
        self.df = pd.concat([self.user_df , self.url_df], axis=1)
        

        self.y = y.values.astype(np.float32)
        self.user_values = [c.values for n,c in self.df[self.user_fields].items()]
        self.url_and_label_values = [c.values for n,c in self.df[self.url_fields].items()]

        self.url_values = self.url_and_label_values[0]
        self.label_value = self.url_and_label_values[1]
        self.Dominant_Topic_value = self.url_and_label_values[2]


        self.user_features = np.stack(self.user_values, 1).astype(np.int64)
        self.url_features = np.stack(self.url_values)
        self.label_features = np.stack(self.label_value)
        self.Dominant_Topic_features = np.stack(self.Dominant_Topic_value)

    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, idx):
        # print(idx)
        user = self.user_features[idx]
        url = self.url_features[idx]
        label = self.label_features[idx]
        Dominant_Topic = self.Dominant_Topic_features[idx]
        y = self.y[idx]
        # print(user,url,label,Dominant_Topic,y)
        return user,url,label,Dominant_Topic, y



class Test_Rating_dataSet(Dataset):
    def __init__(self, user_df,article_df, user_le_mapping, url_to_keyword_label):
        # user_df = user_df["user"].replace(user_le_mapping)
        # article_df = article_df["article"].replace(url_to_keyword)
        # self.user_df = user_df.replace({"user": user_le_mapping})
        # self.article_df = article_df.article.apply(lambda x: url_to_keyword[x])
        self.user_name_df = user_df
        self.url_df = article_df

        self.user_df = user_df.user.apply(lambda x: user_le_mapping[x])
        self.article_df = article_df.article.apply(lambda x: url_to_keyword_label[str(x)])

        self.r_user_df = pd.DataFrame(self.user_df.values.repeat(len(self.article_df), axis=0))
        self.r_article_df = pd.concat([self.article_df]*len(self.user_df), ignore_index=True)

        self.user_name_df = pd.DataFrame(self.user_name_df.values.repeat(len(self.article_df), axis=0))
        self.url_df = pd.concat([self.url_df]*len(self.user_df), ignore_index=True)

        
        self.user_name = self.user_name_df.values.tolist()
        self.user = self.r_user_df.values.tolist()
        self.artices = self.r_article_df.values.tolist()
        self.url = self.url_df.values.tolist()
        # print(self.artices)
        # print(self.artices[0])



    def __len__(self):
        return len(self.r_user_df)
    
    def __getitem__(self, idx):
        # print('self.artices[idx]: ',self.artices[idx])
        user_name = self.user_name[idx]
        user = self.user[idx]
        article_url = self.url[idx]
        url_index = self.artices[idx][0]
        labels = self.artices[idx][1]
        Dominant_Topic = self.artices[idx][2]
        
        return user_name,user,article_url,url_index,labels,Dominant_Topic

