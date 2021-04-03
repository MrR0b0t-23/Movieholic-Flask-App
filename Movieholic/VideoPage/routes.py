from flask import Blueprint, render_template, request,  redirect, url_for
from .tmdbAPI import tmdbAPI
import pandas as pd
from .MovieRecommender import MovieRec

video = Blueprint("video", __name__ ,  template_folder='Templates', static_folder= 'static')

@video.route('/video/<tmdbId>')
def video_page(tmdbId):
    tmdb_api = tmdbAPI(debug = True, API_KEY= '673da2e5ce4c2bad166f72d315081927', language ='en-US')
    contents = tmdb_api.get_info(tmdbId)
    dataset = pd.read_csv("Dataset/updatedRatings.csv")
    print("-------Dataset Successfully loaded-------- ")
    MovieRecModel = MovieRec(dataset)
    similar = MovieRecModel.predict(float(tmdbId), 5, 12)
    print("--------Similar movies predicted--------")
    SimilarMovieDataJSON = []
    for tmp in similar.index:
        SimilarMovieDataJSON.append(
            tmdb_api.get_info(tmp)
        )
    return render_template('VideoPageHTML.html', contents= contents, similar = SimilarMovieDataJSON)