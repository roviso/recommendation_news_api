import pandas as pd
from sklearn import preprocessing
import ast



class preprocessor():
    def __init__(self,data_path,keywords_limit):
        self.df = pd.read_csv(data_path,index_col=False)
        self.df['keywords'] = self.df['keywords'].apply(lambda x: ast.literal_eval(x)[:keywords_limit])

        self.keywords_list = self.df['keywords'].to_list()

        self.keywords_list = list(set([j for sub in self.keywords_list for j in sub]))
        self.keyword_enocder = dict(zip(range(len(self.keywords_list)),self.keywords_list))
        self.keyword_to_label_enocder = dict(zip(self.keywords_list,range(len(self.keywords_list))))
        self.user_index_mapping, self.url_index_mapping, self.label_index_mapping,self.index_user_mapping,self.index_url_mapping,self.index_label_mapping = self.label_ecoder()

        article_list = self.df[['keywords','label_index','Dominant_Topic']].values.tolist()
        url_index_label_list = self.df[['url_index','label_index','Dominant_Topic']].values.tolist()
        
        self.url_to_keyword_and_labels_dict = dict(zip(self.df.url,pd.Series(article_list)))
        self.url_to_index_and_labels_dict = dict(zip(self.df.url,pd.Series(url_index_label_list)))

        self.url_to_keyword_dict = dict(zip(self.df.url_index,self.df.keywords))
        self.keyword_to_url_dict = dict((str(v), k) for k, v in self.url_to_keyword_dict.items())

        self.user_df = self.df[['user_index']]
        self.url_and_label_df = self.df[['url_index','label_index','Dominant_Topic']]

        self.user_flds = [n for n in self.user_df.columns.values]
        self.url_flds = [n for n in self.url_and_label_df.columns.values]
        self.y = self.df[['final_rating']]

        self.user_embedding_cardinality = {n: len(c.astype('category').cat.categories)+1 for n,c in self.df[['user_index']].items()}
        self.url_embedding_cardinality = {'keywords': len(self.keywords_list)+1,'label': len(self.df.label_index.unique()),'Dominant_Topic': len(self.df.Dominant_Topic.unique()) }

        self.user_emb_sizes, self.url_emb_sizes = self.get_user_url_label_embedding()


    def get_keyword_label(self,keyword_list):
        keyword_to_label = []
        for keyword in keyword_list:
            keyword_to_label.append(self.keyword_to_label_enocder[keyword])
        return keyword_to_label

    def label_ecoder(self,):
        user_le = preprocessing.LabelEncoder()
        url_le = preprocessing.LabelEncoder()
        label_le = preprocessing.LabelEncoder()
        self.df['user_index'] = user_le.fit_transform(self.df['user'])
        self.df['url_index'] = url_le.fit_transform(self.df['url'])
        self.df['label_index'] = label_le.fit_transform(self.df['label'])
        user_le_mapping = dict(zip(user_le.classes_, user_le.transform(user_le.classes_)))
        url_le_mapping = dict(zip(url_le.classes_, url_le.transform(url_le.classes_)))
        label_le_mapping = dict(zip(label_le.classes_, label_le.transform(label_le.classes_)))

        le_user_mapping = dict(zip(user_le.transform(user_le.classes_),user_le.classes_))
        le_url_mapping = dict(zip(url_le.transform(url_le.classes_),url_le.classes_))
        label_le_mapping = dict(zip(label_le.transform(label_le.classes_), label_le.classes_))

        self.df['Dominant_Topic'] = self.df['Dominant_Topic'].apply(lambda x : int(x))
        self.df['keywords'] = self.df['keywords'].apply(lambda x: self.get_keyword_label(x))

        return user_le_mapping,url_le_mapping,label_le_mapping,le_user_mapping,le_url_mapping,label_le_mapping

    def get_user_url_label_embedding(self):
        user_emb_sizes = [(size, 108) for item, size in self.user_embedding_cardinality.items()]
        url_emb_sizes = []
        for item, size in self.url_embedding_cardinality.items():
            if item == 'keywords':
                temp_tuple = tuple([size,108])
            elif item == 'label':
                temp_tuple = tuple([size,int(size//2.71828)])
            elif item == 'Dominant_Topic':
                temp_tuple = tuple([size,int(size//2.71828)])
            url_emb_sizes.append(temp_tuple)
        return user_emb_sizes,url_emb_sizes