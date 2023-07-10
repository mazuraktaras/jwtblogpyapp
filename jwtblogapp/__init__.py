from sqlalchemy import exc
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_jwt_extended import JWTManager
from jwtblogapp import config

# Initialize application object
app = Flask(__name__)

# Configure app from python object i.e. from python module (config.py)
app.config.from_object(config)

# Initialize database object
database = SQLAlchemy()

database.init_app(app)

# Initialize api object
blog_api = Api(app)
# Initialize JWT support object
jwt = JWTManager(app)

# All that modules must be imported after app object created due Flask developers recommendation
from jwtblogapp import views, models  # noqa
from jwtblogapp.resources import SignupUser, LoginUser, LogoutUser, Posts, PostRating  # noqa

# Create endpoints with paths by adding resource classes
blog_api.add_resource(SignupUser, '/api/signup', endpoint='api_signup_user')
blog_api.add_resource(LoginUser, '/api/login', endpoint='api_login_user')
blog_api.add_resource(LogoutUser, '/api/logout', endpoint='api_logout_user')
blog_api.add_resource(Posts, '/api/posts', endpoint='api_posts')
blog_api.add_resource(PostRating, '/api/rating', endpoint='api_rating')

# Trying to request to a database engine in application context to check the connectivity
with app.app_context():
    try:
        database.create_all()
    # If no connect print error message and exit application
    except exc.OperationalError as error:
        print(error, flush=True)
        exit(1)
