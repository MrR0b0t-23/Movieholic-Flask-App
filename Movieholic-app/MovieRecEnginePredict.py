import torch 
import torch.nn as nn
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn import model_selection
from sklearn import metrics
import pandas as pd
import tez
import tqdm
import pickle 

class MovieDataset:
    def __init__(self, users, movies, ratings):
        self.users = users
        self.movies = movies
        self.ratings = ratings

    def __len__(self):
        return len(self.users)

    def __getitem__(self, item):
        user = self.users[item]
        movie = self.movies[item]
        rating = self.ratings[item]

        return { "users": torch.tensor(user, dtype=torch.long),
          "movies": torch.tensor(movie, dtype=torch.long),
          "ratings": torch.tensor(rating, dtype=torch.float),
        }
            

class RecSysModel(tez.Model):
    def __init__(self, num_users, num_movies):
        super().__init__()
        self.user_embed = nn.Embedding(num_users, 32)
        self.movie_embed = nn.Embedding(num_movies, 32)
        self.out = nn.Sequential(nn.Linear(64,32), nn.Linear(32,1))

    def fetch_optimizer(self):
        opt = torch.optim.Adam(self.parameters(), lr=1e-2)
        return opt

    def fetch_scheduler(self):
        sch = torch.optim.lr_scheduler.StepLR(self.optimizer, 
            step_size=4 , gamma=0.6)
        return sch
        
    def monitor_metrics(self, output, rating):
        output = output.detach().cpu().numpy()
        rating = rating.detach().cpu().numpy()

        return {
        'rmse': np.sqrt(metrics.mean_squared_error(rating, output))
        }

    def forward(self, users, movies, ratings):
        user_embeds = self.user_embed(users)
        movie_embeds = self.movie_embed(movies)
        output = torch.cat([user_embeds, movie_embeds], dim=1)
        output = self.out(output)

        if len(ratings):
            loss = nn.MSELoss()(output, ratings.view(-1,1))
            calc_metrics = self.monitor_metrics(output, ratings.view(-1,1))
            return output, loss, calc_metrics

class Predict:
    
    def __init__ (self, dataset, device = None):
        self.dataset = dataset
        self.userPklPath = './Movieholic-app/checkpoint/user_encoder.pkl'
        self.moviePklPath= './Movieholic-app/checkpoint/movie_encoder.pkl'
        self.trainedModelPath = './Movieholic-app/checkpoint/trained_model.bin'
        self.device = device
        if self.device == None:
            self.device = 'cpu'

        pkl_file = open(self.userPklPath, 'rb')
        self.lbl_user = pickle.load(pkl_file) 
        pkl_file.close()
        pkl_file = open(self.moviePklPath, 'rb')
        self.lbl_movie = pickle.load(pkl_file) 
        pkl_file.close()
        
        dataset['userId'] = self.lbl_user.fit_transform(dataset['userId'].values)
        dataset['movieId'] = self.lbl_movie.fit_transform(dataset['movieId'].values)
        
        self.valid_dataset = MovieDataset(users = self.dataset.userId.values, 
            movies = self.dataset.movieId.values,
            ratings = self.dataset.rating.values )
        
        self.model = RecSysModel(num_users = 610, 
        num_movies = 9724 )
        
        self.model.load(self.trainedModelPath, device= self.device)
        self.model.eval()
    
    def predict(self):
        self.pred = self.model.predict(self.valid_dataset, batch_size= 24)
        self.pred_valid = []
        for p in self.pred:
            for val in p:
                self.pred_valid.append(val.item()) 
        return self.pred_valid
    
