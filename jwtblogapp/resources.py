from datetime import datetime
from flask_restful import Resource, reqparse
from .models import User, RevokedToken, Post, Rating
from sqlalchemy.exc import IntegrityError, OperationalError
from jwtblogapp import jwt
from flask_jwt_extended import jwt_required, create_access_token, get_jwt, get_jwt_identity

HELP_MSG = 'Can not be blank'

# ---Instantiate the argument's parsers---

# parser for parse credentials
auth_arguments_parser = reqparse.RequestParser()
# parser for parse post text
post_arguments_parser = reqparse.RequestParser()
# parser for parse post id and like value (0 or 1)
rating_arguments_parser = reqparse.RequestParser()

# ---Add arguments for parsing in API endpoints---

# add credentials arguments for parsing
auth_arguments_parser.add_argument('username', required=True, help=HELP_MSG)
auth_arguments_parser.add_argument('password', required=True, help=HELP_MSG)

# add post_text argument for parsing
post_arguments_parser.add_argument('post_text', required=True, help=HELP_MSG)

# add post_id and like arguments for parsing
rating_arguments_parser.add_argument('post_id', type=int, required=True, help=HELP_MSG)
rating_arguments_parser.add_argument('like', type=int, required=True, help=HELP_MSG)


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:  # noqa
    """
    Callback checks if the token is stored in revoked tokens.
    Returns a boolean value, respectively.

    :param jwt_payload:
    :type jwt_payload: dict
    :return: True if token persists in revoked tokens, False otherwise
    :rtype: bool
    """
    jti = jwt_payload["jti"]
    token = RevokedToken.query.filter_by(jti=jti).first()
    return token is not None


# define a class for user signup endpoint
class SignupUser(Resource):
    """
    Represents RESTful resource for user signup endpoint.

    """

    @staticmethod
    def post():
        """
        Method for POST. Parses new user credentials, hash password,
        adds record to database.
        :returns: JSON response object, where are headers, informational message with 'msg' key, status code
        :rtype: object
        """
        # parse arguments to the arguments dictionary
        arguments = auth_arguments_parser.parse_args()
        # instantiate User model
        new_user = User(username=arguments['username'],
                        password=arguments['password'])
        # hash the new user password
        new_user.make_hash()

        try:
            # store the new user record to database and return response
            new_user.store()
            return {'msg': f'User {new_user.username} successfully signed up'}
        except IntegrityError:
            # if the new user already exists response with code 202
            return {'msg': f'User {new_user.username} already exist'}, 202
        except OperationalError:
            return {'msg': 'Internal server error'}, 502


# define a class for user login
class LoginUser(Resource):
    """
    Represents RESTful resource for user login endpoint.

    """

    @staticmethod
    def post():
        """
        Method for POST. Parses a user credentials, looks up if username and password exists in database,
        in case of success return token.
        :returns: JSON response object, where are headers, informational message with 'msg' key,
        token with 'token' key, status code
        :rtype: object
        """
        # parse arguments to the arguments dictionary
        arguments = auth_arguments_parser.parse_args()
        # check if user already exists in database
        if not User.query.filter_by(username=arguments['username']).first():

            return {'msg': 'Bad credentials! Login again or signup'}, 401

        else:
            # instantiate User model class
            user = User.query.filter_by(username=arguments['username']).first()
            # check if user password already exists in database
            if user.ensure_password(arguments['password']):
                # create a token
                token = create_access_token(identity=user.username)
                # return response with token
                return {'msg': f'User {arguments["username"]} successfully logged in', 'token': token}
            else:
                # otherwise return a warning
                return {'msg': 'Bad credentials! Login again or signup'}, 401


# define a class for user logout
class LogoutUser(Resource):
    """
    Represents RESTful resource for user signup endpoint.
    Accepts token stored in 'Authorisation' header with Bearer prefix (Bearer <JWT>) or in JSON body.
    """

    # protect the endpoint
    @jwt_required()
    def post(self):
        """
        Method for POST. Logs out user by saving token in revoked tokens in the database.
        :returns: JSON response object, where are headers, informational message with 'msg' key,
        status code.
        :rtype: object
        """
        # instantiate RevokedToken model class
        revoked_token = RevokedToken(jti=get_jwt()['jti'])
        # save token to the database
        revoked_token.store()
        return {'msg': 'You are successfully logged out'}


class Posts(Resource):
    """
    Represents RESTful resource for blog posts.
    Accepts token stored in 'Authorisation' header with Bearer prefix (Bearer <JWT>) or in JSON body.
    """

    # protect the endpoint
    @jwt_required()
    def get(self):
        """
        Method for GET request. Return all posts.
        :returns: JSON response object, where are headers, JSON object with the 'posts' key with it members with keys
        ['post_id', 'user_id', 'username', 'post_text', 'likes', 'dislikes', 'like_it', 'created_time'],
        status code.
        :rtype: object
        """
        user = User.query.filter_by(username=get_jwt_identity()).first()
        user_ratings = Rating.query.filter_by(user_id=user.id).all()

        def likes_status(post_id):
            """
            Return status of post like for current user

            :param post_id: Get post id
            :return: 0 if post never been liked by user, 1, -1 if liked or disliked respectively
            :rtype: int
            """
            # assign original value
            like_it = 0
            # check if the user has any rating for the post
            if user_ratings:
                # check if the user has 'like' rating for the post
                if post_id in [result.post_like_id for result in user_ratings]:
                    like_it = 1
                # check if the user has 'dislike' rating for the post
                elif post_id in [result.post_dislike_id for result in user_ratings]:
                    like_it = -1

            return like_it

        # make a list of dictionaries by querying all post records from the database
        posts_json = [{'post_id': post.id, 'user_id': post.user_id, 'username': post.username, 'post_text': post.text,
                       'likes': post.likes,
                       'dislikes': post.dislikes, 'like_it': likes_status(post.id),
                       'created_time': post.created_time.strftime("%d-%m-%Y %H:%M:%S")
                       } for post in Post.query.all()]

        return {'posts': posts_json}

    # protect the endpoint
    @jwt_required()
    def post(self):
        """
        Method for POST request. Saves the new post to the database.
        :returns: JSON response object, where are headers, informational message with 'msg' key,
        status code.
        :rtype: object
        """
        # assign the current username to variable
        user = User.query.filter_by(username=get_jwt_identity()).first()
        # parse arguments to the arguments dictionary
        arguments = post_arguments_parser.parse_args()
        # instantiate Posts model class
        new_post = Post(user_id=user.id, username=user.username, text=arguments['post_text'], likes=0, dislikes=0,
                        created_time=datetime.now())
        # save new post to database
        new_post.store()

        return {'msg': 'Post successfully created'}


class PostRating(Resource):
    """
    Represents RESTful resource for blog posts rating.
    Accepts token stored in 'Authorisation' header with Bearer prefix (Bearer <JWT>) or in JSON body.
    """

    # protect the endpoint
    @jwt_required()
    def post(self):
        """
        Method for POST request. Parses the values of 'post_id' and 'like'. Creates a new post's rating or
        modify an existing one if a user already likes or dislikes post.
        :returns: JSON response object, where are headers, informational message with 'msg' key,
        status code.
        :rtype: object
        """

        # assign original values to None
        post_like_id = None
        post_dislike_id = None
        # assign the current username to variable
        user = User.query.filter_by(username=get_jwt_identity()).first()
        # parse arguments to the arguments dictionary
        arguments = rating_arguments_parser.parse_args()
        post_id = arguments['post_id']

        # delete unused (indifferent liked) records
        rating = Rating()
        rating.del_indifferent()

        # get all post ids rated by current user
        user_ratings = Rating.query.filter_by(user_id=user.id).all()
        # check if the parsed post id exist in the database, if not response warning
        if not Post.query.get(post_id):
            return {'msg': 'Not such post_id in database'}, 404
        # query post record bu post id

        post = Post.query.filter_by(id=post_id).first()

        # check if the user wants like or dislike the post

        # if like
        if arguments['like'] == 1:

            # if the user already 'like' the post trigger indifferent

            if post_id in [result.post_like_id for result in user_ratings]:
                # find 'liked' post's rating
                rating = Rating.query.filter_by(user_id=user.id, post_like_id=post_id).one()

                rating.post_like_id = None

                # update rating
                rating.update()
                # change counts of likes and dislikes in post's record

                post.likes = Post.likes - 1
                # update post
                post.update()

                return {'msg': 'Rating updated to indifferent'}

            if post_id in [result.post_dislike_id for result in user_ratings]:
                # find 'disliked' post's rating
                rating = Rating.query.filter_by(user_id=user.id, post_dislike_id=post_id).one()

                rating.post_like_id = post_id
                rating.post_dislike_id = None

                # update rating
                rating.update()
                # change counts of likes and dislikes in post's record

                post.likes = Post.likes + 1
                post.dislikes = Post.dislikes - 1
                # update post
                post.update()

                return {'msg': 'Rating updated to Like'}

            # If the post has never been 'likes' rated by current user
            post.likes = Post.likes + 1
            post_like_id = post_id
            post.update()
            new_rating = Rating(user_id=user.id, post_like_id=post_like_id, post_dislike_id=post_dislike_id,
                                created_time=datetime.now())
            # save the new rating to  the database
            new_rating.store()

        # if dislike
        else:
            # if the user already 'dislike' the post response warning
            if post_id in [result.post_dislike_id for result in user_ratings]:
                rating = Rating.query.filter_by(user_id=user.id, post_dislike_id=post_id).one()
                # reassign post's dislike and like ids
                rating.post_dislike_id = None
                # update rating
                rating.update()
                # change counts of dislikes in post's record
                post.dislikes = Post.dislikes - 1
                # update post
                post.update()
                return {'msg': 'Rating updated to indifferent'}

            # If the post has never been 'dislikes' rated by current user
            if post_id in [result.post_like_id for result in user_ratings]:
                # find 'disliked' post's rating
                rating = Rating.query.filter_by(user_id=user.id, post_like_id=post_id).one()

                rating.post_dislike_id = post_id
                rating.post_like_id = None

                # update rating
                rating.update()
                # change counts of likes and dislikes in post's record

                post.likes = Post.likes - 1
                post.dislikes = Post.dislikes + 1
                # update post
                post.update()

                return {'msg': 'Rating updated to Dislike'}

            # If the post has never been 'likes' rated by current user
            post.dislikes = Post.dislikes + 1
            post_dislike_id = post_id
            post.update()
            new_rating = Rating(user_id=user.id, post_like_id=post_like_id, post_dislike_id=post_dislike_id,
                                created_time=datetime.now())
            # save the new rating to  the database
            new_rating.store()

        return {'msg': 'Rating successfully created'}
