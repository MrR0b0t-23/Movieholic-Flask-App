from flask import Flask
from flask import render_template, request, redirect, url_for
import pandas as pd 
from MovieRecEnginePredict import Predict
from tmdbAPI import tmdbAPI
from MovieRecommender import MovieRec
import datetime
pd.options.mode.chained_assignment = None 

app = Flask(__name__) 

usersData = pd.read_csv("./Movieholic-app/Dataset/updatedRatings.csv")
userIdList = usersData['userId'].unique()
tmdb_api = tmdbAPI(debug = False, API_KEY= '<YOUR TMDB API KEY>', language ='en-US')

@app.route('/', methods =[ 'POST', 'GET'])
def login_page():
    
    if request.method == 'POST':
       # getting input with name = fname in HTML form
       userId = request.form.get("userId")
       return redirect(url_for('landing_page', userId= userId))
    content = {
        'users': userIdList
    }
    return render_template('./LoginPageHTML.html', **content)

class LandingPage:

    def __init__(self, userId):
        self.userId = userId

    def filter_userData(self):
        self.dataset = usersData
        self.starting_date = pd.to_datetime(self.dataset['time'].max()) - datetime.timedelta(30)
        self.watched_movieData = self.dataset[self.dataset['userId'] == int(self.userId)]
        self.unwatched_movieData = self.dataset[~self.dataset['movieId'].isin(self.watched_movieData['movieId'].values)]
        self.top_movieData = self.dataset[pd.to_datetime(self.dataset['time']) > self.starting_date]
        self.top_movieData['popularity'] = self.top_movieData.groupby(['movieId'])['userId'].transform('count')
        self.top_movieData.sort_values(by = ['popularity'], inplace = True,  ascending= False)
        self.top_movieData.drop_duplicates(subset=['movieId'], inplace = True, keep = 'last')
        self.recentWatched_movieData = self.watched_movieData.sort_values(by=['time'], ascending =False).head(2)

        print("-------Filtering function passed-------")

    def predict_userRating(self):
        self.predicted_userRatingData = pd.DataFrame()
        self.predicted_userRatingData['movieId'] = self.unwatched_movieData['movieId']
        self.predicted_userRatingData['tmdbId'] = self.unwatched_movieData['tmdbId']
        self.predicted_userRatingData.drop_duplicates(subset=['movieId'], inplace = True)
        self.predicted_userRatingData['userId'] = self.userId
        self.predicted_userRatingData['rating'] = 0.0
        self.model = Predict(dataset = self.predicted_userRatingData )
        self.predicted_userRatingData['rating'] = self.model.predict()
        self.predicted_userRatingData.sort_values(by=['rating'], ascending=False, inplace = True)
        self.predicted_userRatingData = self.predicted_userRatingData.head(12)

        print("-------Rating Prediction passed-------")
    
    def get_top_movieData(self):
        self.top_movieData = self.top_movieData.head(6)
        self.top_movieDataJSON = []
        for tmdbId in self.top_movieData['tmdbId'].values:
            self.top_movieDataJSON.append(self.get_movieData(tmdbId))

        print("-------Top movie function passed-------")
        

    def get_watched_movieData(self):
        self.watched_movieData.sort_values(by=['time'], ascending=False, inplace = True)
        self.watched_movieData = self.watched_movieData.head(6)
        self.watched_movieDataJSON = []
        for tmp in self.watched_movieData['tmdbId'].values:
            self.watched_movieDataJSON.append(self.get_movieData(tmp))
    
        print("-------Watched movie function passed-------")
        
    def get_unwatched_movieData(self):
        self.predict_userRating()
        self.predicted_recMovieDataJSON = []
        for tmp in self.predicted_userRatingData['tmdbId'].values:
            self.predicted_recMovieDataJSON.append(
                self.get_movieData(tmp)
            )
        print("-------Unwatched movie function passed-------")
            
    def get_recentwatched_movieData(self):
        self.MovieRecModel = MovieRec(self.dataset)
        self.recentWatched_movie1SimilarData = self.MovieRecModel.predict(self.recentWatched_movieData['tmdbId'].values[0],
                                                                            self.recentWatched_movieData['rating'].values[0], 12 )
        self.recentWatched_movie2SimilarData = self.MovieRecModel.predict(self.recentWatched_movieData['tmdbId'].values[1],
                                                                   self.recentWatched_movieData['rating'].values[1], 12)
        for tmp in self.recentWatched_movie1SimilarData.index:
            if tmp  in self.watched_movieData['tmdbId'].values:
                self.recentWatched_movie1SimilarData.drop(labels = [tmp], inplace =True) 

        self.recentWatched_movie1SimilarDataJSON = []
        for tmp in self.recentWatched_movie1SimilarData.index[:6]:
            self.recentWatched_movie1SimilarDataJSON.append(
                self.get_movieData(tmp)
            )

        for tmp in self.recentWatched_movie2SimilarData.index:
            if tmp  in self.watched_movieData['tmdbId'].values:
                self.recentWatched_movie2SimilarData.drop(labels = [tmp], inplace =True) 

        self.recentWatched_movie2SimilarDataJSON = []
        for tmp in self.recentWatched_movie2SimilarData.index[:6]:
            self.recentWatched_movie2SimilarDataJSON.append(
                self.get_movieData(tmp)
            )

    def get_movieData(self, tmdbId):
        self.tmdb_api = tmdbAPI(debug = True, API_KEY= '<YOUR TMDB API KEY>', language ='en-US')
        return self.tmdb_api.get_info(tmdbId)

    def get_landindPageData(self):
        self.filter_userData()
        self.get_top_movieData()
        self.get_unwatched_movieData()
        self.get_watched_movieData()
        self.get_recentwatched_movieData()
        contents = {
            'top_movieData': self.top_movieDataJSON,
            'unwatched_movieData' : self.predicted_recMovieDataJSON,
            'watched_movieData': self.watched_movieDataJSON,
            'recentWatched_movie1': self.recentWatched_movieData['title'].values[0],
            'recentWatched_movie2': self.recentWatched_movieData['title'].values[1],
            'recentWatched_movie1SimilarData': self.recentWatched_movie1SimilarDataJSON,
            'recentWatched_movie2SimilarData': self.recentWatched_movie2SimilarDataJSON,
                }
        return contents

@app.route('/home/<userId>')
def landing_page(userId):  
    LandingPageModel = LandingPage(userId)  
    contents = LandingPageModel.get_landindPageData()
    return render_template('./LandingPageHTML.html', contents = contents)

@app.route('/credit/<tmdbId>/<creditId>')
def credit_page(tmdbId,creditId):
    contents = tmdb_api.get_info(tmdbId)
    for val in contents['movieCreditActorData']:
        if val['Id'] == int(creditId):
            contents = val
            return render_template('./CreditPageHTML.html', contents= contents)
    if contents['movieCreditDirectorData']['Id']== int(creditId): 
            contents = contents['movieCreditDirectorData']
            return render_template('./CreditPageHTML.html', contents= contents)

@app.route('/video/<tmdbId>')
def video_page(tmdbId):
    contents = tmdb_api.get_info(tmdbId)
    dataset = usersData
    print("-------Dataset Successfully loaded--------")
    MovieRecModel = MovieRec(dataset)
    similar = MovieRecModel.predict(float(tmdbId), 5, 12)
    print("--------Similar movies predicted--------")
    SimilarMovieDataJSON = []
    for tmp in similar.index:
        SimilarMovieDataJSON.append(
            tmdb_api.get_info(tmp))
    return render_template('./VideoPageHTML.html', contents= contents, similar = SimilarMovieDataJSON)

if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0")
