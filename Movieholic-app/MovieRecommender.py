import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

class MovieRec:
    
    def __init__(self, rating_df):
        
        self.rating_df = rating_df        
        self.movie_rel = pd.pivot_table(rating_df,values='rating',
                                index='userId',
                                columns='tmdbId')
        self.movie_rel.fillna(0, inplace=True)
        self.movie_rel = self.movie_rel.apply(lambda row: (row - row.mean()) / (row.max() - row.min()), raw= True, axis=1)
        self.movie_similarity = pd.DataFrame(cosine_similarity(self.movie_rel.T), 
                                    columns = self.movie_rel.columns,
                                    index= self.movie_rel.columns)
        
    def predict(self, tmdbId, user_rating, result_size):
        self.user_rating = int(user_rating)
        self.tmdbId = int(tmdbId)
        self.result_size = result_size
        self.similar_score = self.movie_similarity[self.tmdbId]*(self.user_rating - 2.5)
        self.similar_score.sort_values(ascending = False, inplace = True)        
        return self.similar_score.iloc[1:self.result_size+1]
