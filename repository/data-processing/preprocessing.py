import pandas as pd 
import time
import nepali_datetime 
import snowballstemmer

class preprocesor():
    def __init__(self,path,df):
        start = time.time()

        #initializing dataframe
        if df.any():
            self.df = df
        else:
            self.df = pd.read_csv(path)
#         self.df = self.df[self.df['heading'].notna()]
#         self.df = self.df[self.df['content'].notna()]
        self.df.date =  self.df.date.apply(self.to_nepali_date)
        self.most_recent_date = self.df['date'].max()
        print('Most recent date: ',self.most_recent_date)
        end_year = self.most_recent_date.year
        end_month = self.most_recent_date.month
        end_day = self.most_recent_date.day
        print('Taking only 6 months of datasets')
        start_date = nepali_datetime.datetime(2077, 11, end_day, 5, 5, 5, 108108)
        end_date = nepali_datetime.datetime(end_year, 2, end_day, 5, 5, 5, 108108)
        self.filter_by_date(start_date,end_date)
       


        #initializing stop_words
        self.stop_words = [] 
        with open('non-potential-topic-word-list.txt', 'r', encoding="utf8") as reader:
            for line in reader:
                line = line.strip('\n')
                self.stop_words.append(line)


        #initializing nepali stemmer
        self.stemmer = snowballstemmer.NepaliStemmer()

        
        self.df.drop_duplicates(subset =['url', 'label'],keep = 'last', inplace = True)
        self.df['all_content'] = self.df['heading'] + ' ' + self.df['content']
        
        print('Numbers of rows are: ',len(self.df))
        mid_end = time.time()
        print('time taken to initilize:', mid_end- start)
        self.content_filter(self.df['all_content'])
        end = time.time()
        print('time taken to filter:', end-mid_end)
        print('total time taken:', end-start)

    def to_nepali_date(self,date):
        nepali_date = nepali_datetime.datetime.strptime(date.split()[0], '%Y-%m-%d')
        return nepali_date

    def filter_by_date(self, start_date, end_date):
        mask = (self.df['date'] > start_date) & (self.df['date'] <= end_date)
        self.df = self.df.loc[mask].reset_index(drop = True)



    def content_filter(self,df_all_content):
        self.df['content_list'] = df_all_content.apply(self.tokenizer)
        self.df['all_content'] =  self.df['content_list'].apply(lambda x: " ".join(x))


    def tokenizer(self,text): 
        tokenized_word = []
        stopwords = set(self.stop_words)

        stem_list = self.stemmer.stemWords(text.split())
        

        tokenized_word = list(filter(self.word_filter, stem_list))
        # final_tokenized_word = [word for word in tokenized_word if len(word)>3]

        return tokenized_word

    def word_filter(self,stem_word):
        nepali_word = True
        # print('stem_word: ',stem_word)
        if len(stem_word) > 3:
            for letter in stem_word:
                if not 0x0090 <= ord(letter) <= 0x97F:
                    nepali_word = False
                return nepali_word 
        else:
            return False    

    
        
    def get_corpus_documents(self,):
        start = time.time()
        corpus = self.df["all_content"].tolist()
        documents = self.df["content_list"].tolist()
        # documents = [ 
        #     [ 
        #         term for term in document.split()
        #     ] 
        #     for document in corpus
        # ]
        end = time.time()
        print('time taken to prepare corpus and document:', end-start)
        return corpus,documents