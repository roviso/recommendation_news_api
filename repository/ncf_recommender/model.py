import torch
import torch.nn as nn

class NMF(nn.Module):
    def __init__(self, user_emb_sizes, url_emb_sizes,url_to_keyword_dict,nlayer, dropout,device):
        super(NMF, self).__init__()
        self.dropout = dropout
        self.device = device
        self.url_to_keyword_dict = url_to_keyword_dict
        self.total_keyword_len = len(url_to_keyword_dict[0])
        self.user_GMF_embedding, self.url_GMF_embedding = self.get_GMF_embeddings(user_emb_sizes,url_emb_sizes)

        self.user_MLP_embedding, self.url_MLP_embedding = self.get_MLP_embeddings(user_emb_sizes,url_emb_sizes,nlayer)

        self.final_url_GMF_size = self.total_keyword_len * url_emb_sizes[0][1] + url_emb_sizes[1][1] + url_emb_sizes[2][1]

        self.user_MLP_size = [(car, siz*(2**(nlayer-1))) for car,siz in user_emb_sizes][0][1] 
        MLP_url_emb_sizes = [(car, siz*(2**(nlayer-1))) for car,siz in url_emb_sizes]
        self.final_url_MLP_size = (self.total_keyword_len * MLP_url_emb_sizes[0][1]) + MLP_url_emb_sizes[1][1] + MLP_url_emb_sizes[2][1]
        self.final_MLP_input_size = self.user_MLP_size +self.final_url_MLP_size



        MLP_modules = []
        MLP_modules.append(nn.Linear(self.final_MLP_input_size, self.final_MLP_input_size//2))
        MLP_modules.append(nn.Dropout(p=self.dropout))
        MLP_modules.append(nn.Linear(self.final_MLP_input_size//2, self.final_MLP_input_size//4))
        MLP_modules.append(nn.ReLU())
        MLP_modules.append(nn.Dropout(p=self.dropout))
        MLP_modules.append(nn.Linear(self.final_MLP_input_size//4, self.final_MLP_input_size//8))
        MLP_modules.append(nn.ReLU())
        MLP_modules.append(nn.Dropout(p=self.dropout))
        MLP_modules.append(nn.Linear(self.final_MLP_input_size//8, self.final_MLP_input_size//16))
        MLP_modules.append(nn.ReLU())
        MLP_modules.append(nn.Dropout(p=self.dropout))

        self.MLP_layers = nn.Sequential(*MLP_modules)
        print('self.MLP_layers ',self.MLP_layers)

        self.predict_size = self.final_MLP_input_size//16
        self.predict_layer = nn.Linear(self.final_MLP_input_size//16,1)
        # print('self.predict_layer ',self.predict_layer)

    def get_GMF_embeddings(self,user_emb_sizes,url_emb_sizes):
        user_embeddings = nn.ModuleList([nn.Embedding(car, siz) for car,siz in user_emb_sizes])
        url_embeddings = nn.ModuleList([nn.Embedding(car, siz) for car,siz in url_emb_sizes])
        for emb in user_embeddings:
            emb.weight.data.uniform_(-1.00,1.00)
        for emb in url_embeddings:
            emb.weight.data.uniform_(-1.00,1.00)
        return user_embeddings,url_embeddings


    def get_MLP_embeddings(self,user_emb_sizes,url_emb_sizes,nlayer):
        user_embeddings = nn.ModuleList([nn.Embedding(car, siz*(2**(nlayer-1))) for car,siz in user_emb_sizes])
        url_embeddings = nn.ModuleList([nn.Embedding(car, siz*(2**(nlayer-1))) for car,siz in url_emb_sizes])
        for emb in user_embeddings:
            emb.weight.data.uniform_(-1.00,1.00)
        for emb in url_embeddings:
            emb.weight.data.uniform_(-1.00,1.00)
        return user_embeddings,url_embeddings

    
    def get_article_embed_GMF(self,url,label,Dominant_Topic):
        cuda = self.device
        for i,e in enumerate(self.url_GMF_embedding):
            if i ==0 :
                keywords_embedding = e(torch.tensor([self.url_to_keyword_dict[u] for u in [int(i) for i in url]]).to(device=cuda))
            if i ==1 :
                label_embedding = e(label.to(device=cuda))
            if i ==2 :
                Dominant_Topic_embedding = e(Dominant_Topic.to(device=cuda))
        article_embed_GMF = [keywords_embedding,label_embedding,Dominant_Topic_embedding]
        return article_embed_GMF

    def get_article_embed_MLP(self,url,label,Dominant_Topic):
        cuda = self.device
        for i,e in enumerate(self.url_MLP_embedding):
            if i ==0 :
                keywords_embedding = e(torch.tensor([self.url_to_keyword_dict[u] for u in [int(i) for i in url]]).to(device=cuda))
            if i ==1 :
                label_embedding = e(label.to(device=cuda))
            if i ==2 :
                Dominant_Topic_embedding = e(Dominant_Topic.to(device=cuda))
        article_embed_MLP = [keywords_embedding,label_embedding,Dominant_Topic_embedding]
        return article_embed_MLP


    def forward(self, user, item,label,Dominant_Topic):
        user_embed_GMF = [e(user) for i,e in enumerate(self.user_GMF_embedding)]
        article_embed_GMF = self.get_article_embed_GMF(item,label,Dominant_Topic)
        batch_size = user_embed_GMF[0].shape[0]
        user_embed_GMF = user_embed_GMF[0].reshape(batch_size,-1)
        final_article_embed_GMF = torch.cat((article_embed_GMF[2].reshape(batch_size,-1),article_embed_GMF[1].reshape(batch_size,-1),article_embed_GMF[0].reshape(batch_size,-1)),1)


        user_embed_MLP = [e(user) for i,e in enumerate(self.user_MLP_embedding)]
        article_embed_MLP = self.get_article_embed_MLP(item,label,Dominant_Topic)
        user_embed_MLP = user_embed_MLP[0].reshape(batch_size,-1)
        final_article_embed_MLP = torch.cat((article_embed_MLP[2].reshape(batch_size,-1),article_embed_MLP[1].reshape(batch_size,-1),article_embed_MLP[0].reshape(batch_size,-1)),1)

        final_article_embed_GMF[:,:final_article_embed_MLP.shape[1]]
        
        output_GMF = user_embed_GMF * final_article_embed_GMF[:,:user_embed_GMF.shape[1]]
        interaction = torch.cat((user_embed_MLP, final_article_embed_MLP), -1)

        output_MLP = self.MLP_layers(interaction)
        concat = torch.cat((output_GMF, output_MLP), -1)

        prediction = self.predict_layer(concat[:,:self.predict_size])

        return prediction, user_embed_MLP, article_embed_MLP
