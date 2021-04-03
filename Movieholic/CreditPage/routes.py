from flask import Blueprint, render_template, request,  redirect, url_for
from .tmdbAPI import tmdbAPI

credit = Blueprint("credit", __name__ ,  template_folder='Templates', static_folder= 'static')

@credit.route('/credit/<tmdbId>/<creditId>')
def credit_page(tmdbId,creditId):
    tmdb_api = tmdbAPI(debug = True, API_KEY= '673da2e5ce4c2bad166f72d315081927', language ='en-US')
    contents = tmdb_api.get_info(tmdbId)
    for val in contents['movieCreditActorData']:
        if val['Id'] == int(creditId):
            contents = val
            return render_template('CreditPageHTML.html', contents= contents)
    if contents['movieCreditDirectorData']['Id']== int(creditId): 
            contents = contents['movieCreditDirectorData']
            return render_template('CreditPageHTML.html', contents= contents)
    