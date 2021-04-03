from flask import Flask, session
from LoginPage.routes import login
from LandingPage.routes import landing
from VideoPage.routes import video
from CreditPage.routes import credit

def create_app():
    app = Flask(__name__)
    app.register_blueprint(login)
    app.register_blueprint(landing)
    app.register_blueprint(video)
    app.register_blueprint(credit)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
