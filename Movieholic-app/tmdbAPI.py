import requests

class tmdbAPI:

    def __init__(self, API_KEY, language, debug):
        self.API_KEY = str(API_KEY)
        self.language = language
        self.debug = debug 
        self.imagePath = 'https://image.tmdb.org/t/p/w500'
        self.youtubePath = 'https://www.youtube.com/embed/'
    
    
    def get_movieId(self):
        self.tmbdId_response = requests.get('https://api.themoviedb.org/3/movie/' + self.tmdbId + '/external_ids?api_key=' + self.API_KEY)
        self.tmbdId_response = self.tmbdId_response.json()
        if 'status_code' not in self.tmbdId_response:
            self.movieImdbId = str(self.tmbdId_response['imdb_id'])
        else: 
            self.movieImdbId = None

    def get_movieDetails(self):
        self.movieDetail_response = requests.get('https://api.themoviedb.org/3/movie/'+ self.movieImdbId + '?api_key=' + self.API_KEY +'&language=' + self.language)
        self.movieDetail_response = self.movieDetail_response.json()

        self.movieTitle = self.movieDetail_response['original_title']
        self.movieRuntime = self.movieDetail_response['runtime']
        self.movieReleaseDate = self.movieDetail_response['release_date']
        self.movieAdult = self.movieDetail_response['adult']
        self.movieOverview = self.movieDetail_response['overview']
        self.movieGenres_json = self.movieDetail_response['genres']
        self.movieVoteAverage = self.movieDetail_response['vote_average']
        self.movieGenres = []
        for i in self.movieGenres_json:
            self.movieGenres.append(i['name'])
        self.movieLanguage = self.movieDetail_response['original_language']
        
    def get_moviePoster(self):
        self.movieBgDropPath = self.imagePath + str(self.movieDetail_response['backdrop_path'])
        self.moviePosterPath = self.imagePath + str(self.movieDetail_response['poster_path'])
        #print(self.moviePosterPath)
        #print(self.movieBgDropPath)
        
    def get_movieCredits(self):
        self.movieCredit_response = requests.get('https://api.themoviedb.org/3/movie/' + self.movieImdbId + '/credits?api_key=' + self.API_KEY + '&language=' + self.language)
        self.movieCredit_response = self.movieCredit_response.json()
        self.movieCreditActor_response = self.movieCredit_response['cast']
        
        self.movieCreditActorData = []
        for i in self.movieCreditActor_response[0:5]:

            tmpActor_response = requests.get('https://api.themoviedb.org/3/person/'+ str(i['id'])  +'?api_key='+ self.API_KEY +'&language='+ self.language)
            tmpActor_response = tmpActor_response.json()
            self.movieCreditActorData.append( {'Id': i['id'],
                                            'originalName' : tmpActor_response['name'],
                                            'characterName': i['character'],
                                            'department' : tmpActor_response['known_for_department'],
                                            'profilePath': self.imagePath + str(tmpActor_response['profile_path']),
                                            'bDay': tmpActor_response['birthday'],
                                            'bPlace': tmpActor_response['place_of_birth'],
                                            'overview': tmpActor_response['biography']} )
        
        self.movieCreditDirector_response = self.movieCredit_response['crew']
        for i in self.movieCreditDirector_response:
            if i['job'] == 'Director':
                tmpDirector_response = requests.get('https://api.themoviedb.org/3/person/'+ str(i['id']) +'?api_key='+ self.API_KEY +'&language='+ self.language)
                tmpDirector_response = tmpDirector_response.json()
                
                self.movieCreditDirectorData = {
                    'Id': i['id'],
                    'originalName' : tmpDirector_response['name'],
                    'department' : tmpDirector_response['known_for_department'],
                    'profilePath' : self.imagePath + str(tmpDirector_response['profile_path']),
                    'bDay': tmpDirector_response['birthday'],
                    'bPlace': tmpDirector_response['place_of_birth'],
                    'overview': tmpDirector_response['biography']
                }
            

        #print(self.movieCreditDirectorData)

    def get_movieVideo(self):
        self.movieVideo_response = requests.get('https://api.themoviedb.org/3/movie/'+ self.movieImdbId +'/videos?api_key='+ self.API_KEY + '&language=' + self.language)
        self.movieVideo_response = self.movieVideo_response.json()

        self.movieTrailerPath = '/'
        self.movieTeaserPath = '/'
        self.movieClipPath = '/'
        for i in self.movieVideo_response['results']:
            if i['site'] == 'YouTube' and i['type'] == 'Trailer':
                self.movieTrailerPath = self.youtubePath + str(i['key'])
            if i['site'] == 'YouTube' and i['type'] == 'Teaser':
                self.movieTeaserPath = self.youtubePath + str(i['key'])
            if i['site'] == 'YouTube' and i['type'] == 'Clip':
                self.movieClipPath = self.youtubePath + str(i['key'])
        #print(self.movieTrailerPath)
        
    def get_info(self, tmdbId):
        self.tmdbId = str(tmdbId)
        self.get_movieId()
        if self.movieImdbId:
            self.get_movieDetails()
            self.get_moviePoster()
            self.get_movieVideo()
            self.get_movieCredits()
            return {
                'tmdbId' : self.tmdbId, 'movieVote': self.movieVoteAverage,
                'movieTitle': self.movieTitle, 'movieRuntime' : self.movieRuntime, 'movieReleaseDate' : self.movieReleaseDate,
                'movieAdult': self.movieAdult, 'movieOverview': self.movieOverview, 'movieGenres' : self.movieGenres,
                'movieLanguage': self.movieLanguage, 'movieBgDropPath': self.movieBgDropPath, 'moviePosterPath': self.moviePosterPath,
                'movieCreditActorData': self.movieCreditActorData, 'movieCreditDirectorData': self.movieCreditDirectorData,
                'movieTrailerPath': self.movieTrailerPath, 'movieTeaserPath': self.movieTeaserPath, 'movieClipPath': self.movieClipPath
            }
        else:
            return{
                'message' :"The resource you requested could not be found"
            }
