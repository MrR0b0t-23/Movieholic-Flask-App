from flask import Blueprint, render_template, request,  redirect, url_for
import pandas as pd 

login = Blueprint("login", __name__ ,  template_folder='Templates', static_folder= 'static')
usersData = pd.read_csv("Dataset/updatedRatings.csv")
userIdList = usersData['userId'].unique()

@login.route('/', methods =[ 'POST', 'GET'])
def login_page():
    if request.method == 'POST':
       # getting input with name = fname in HTML form
       userId = request.form.get("userId")
       return redirect(url_for('landing.landing_page', userId= userId))
    content = {
        'users': userIdList
    }
    return render_template('LoginPageHTML.html', **content)