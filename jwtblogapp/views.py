import re
import requests
from flask import flash, jsonify, make_response, request, render_template, redirect, session, url_for

from jwtblogapp import app
from jwtblogapp import jwt
from flask_jwt_extended import jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies

from jwtblogapp.forms import LoginForm, PostForm, RateForm
from jwtblogapp.bot import BlogBot

api_url = app.config['API_URL']


@jwt.expired_token_loader
def expired_token(jwt_header, jwt_payload):  # noqa
    """
    Callback for expired token

    :param jwt_header: a dictionary containing the header data of the JWT.
    :param jwt_payload: a dictionary containing the payload data of the JWT.
    :return: Flask HTML response object if request was from a browser user agent, otherwise returns the JSON response.
    """
    # check if a request was from a /web/ route
    match = re.search('web', request.full_path)
    if match:
        # make Flask response with redirect to login page
        response = make_response(redirect(url_for('web_login')))
        # Reset logged in session
        session['logged'] = False
        # show notification message in a web page
        flash('Your token has expired! Log in, please', 'danger')
        return response

    return jsonify(msg='Token has expired!'), 401


@jwt.unauthorized_loader
def unauthorized_token(jwt_header, jwt_payload):  # noqa
    """
    Callback for unauthorized token

    :param jwt_header: a dictionary containing the header data of the JWT.
    :param jwt_payload: a dictionary containing the payload data of the JWT.
    :return: Flask HTML response object if request was from a browser user agent, otherwise returns the JSON response.
    """
    # check if a request was from a /web/ route
    match = re.search('web', request.full_path)
    if match:
        # make Flask response with redirect to login page
        response = make_response(redirect(url_for('web_login')))
        # Reset logged in session
        session['logged'] = False
        # show notification message in a web page
        flash('Your are unauthorized! Log in, please', 'danger')
        return response

    return jsonify(msg='Your token is unauthorized!'), 401


@app.route('/')
@jwt_required(optional=True)
def index():
    """
    View for base page Kotova test

    :return: Flask HTML response object
    """
    current_identity = get_jwt_identity()
    if current_identity and session['logged'] is True:
        return redirect(url_for('blog'))

    return render_template('blog_base.j2')


@app.route('/web/signup', methods=['GET', 'POST'])
def web_signup():
    """
    View for signup page

    :return: Flask HTML response object
    """
    # instantiate credentials form object
    form = LoginForm()
    # checks if form was submitted and validated
    if form.validate_on_submit():
        # get values from form
        username = form.username.data
        password = form.password.data
        # request signup from API
        payload = {'username': username, 'password': password}
        response = requests.post(f"{api_url}{url_for('api_signup_user')}", json=payload)
        # check if user already exist
        if response.status_code == 202:
            form.username.data = ''
            form.password.data = ''
            # show notification message in a web page
            flash(response.json()['msg'], 'danger')
            # if already exists redirect to signup view
            return redirect(url_for('web_signup'))
        # show notification message in a web page
        flash(response.json()['msg'], 'success')
        # # if user successfully signed up, redirect to login view
        return redirect(url_for('web_login'))
    # render template for signup
    return render_template('blog_signup.j2', form=form)


@app.route('/web/login', methods=['GET', 'POST'])
def web_login():
    """
    View for login page

    :return: Flask HTML response object
    """
    # instantiate credentials form object
    form = LoginForm()
    form.submit.label.text = 'Login'
    #  checks if form was submitted and validated
    if form.validate_on_submit():
        # get values from form
        username = form.username.data
        password = form.password.data
        # make login request from API
        payload = {'username': username, 'password': password}
        response = requests.post(f"{api_url}{url_for('api_login_user')}", json=payload)
        # check if login is not authenticate
        if response.status_code == 401:
            # show notification message in a web page
            flash(response.json()['msg'], 'danger')
            # redirect to login view
            return redirect(url_for('web_login'))
        # if login is authenticated

        # Take token from JSON response
        token = response.json()['token']
        # show notification message in a web page
        flash(response.json()['msg'], 'success')
        # make HTML response with saving token in cookies and redirection to blog view
        response = make_response(redirect(url_for('blog')))
        set_access_cookies(response, token)
        # Reset logged in session storage
        session['logged'] = True
        return response
    # render template for login and make HTML response
    return render_template('blog_login.j2', form=form)


@app.route('/web/logout', methods=['GET', 'POST'])
@jwt_required()  # protect route
def web_logout():
    """
    View for logout page

    :return: Flask HTML response object
    """
    # get token from cookies
    token = request.cookies.get('access_token_cookie')
    # request API logout endpoint
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(f"{api_url}{url_for('api_logout_user')}", headers=headers)
    # show notification message in a web page
    flash(response.json()['msg'], 'warning')
    # make HTML response with erasing token from cookies and redirection to index view
    response = make_response(redirect(url_for('index')))
    unset_jwt_cookies(response)
    # Reset logged in session storage
    session['logged'] = False

    return response


@app.route('/web/blog', methods=['GET', 'POST'])
@jwt_required()  # protect route
def blog():
    """
    View for blog page

    :return: Flask HTML response object
    """
    # get username
    current_user = get_jwt_identity()
    # instantiate post form object
    form = PostForm()
    # instantiate rate form object
    rate_form = RateForm()
    # get token from cookies
    token = request.cookies.get('access_token_cookie')
    headers = {'Authorization': f'Bearer {token}'}
    # checks if rate form was submitted
    if rate_form.is_submitted() and rate_form.like.data:
        # get values from form POST
        post_id = rate_form.post_id.data
        like = rate_form.like.data
        # request API prostrating endpoint
        payload = {'post_id': post_id, 'like': like}
        response = requests.post(f"{api_url}{url_for('api_rating')}", headers=headers, json=payload)
        # show notification message in a web page
        flash(response.json()['msg'], 'success')
        # response with redirect back to blog view
        return redirect(url_for('blog'))

    if form.validate_on_submit():
        # get value from form POST
        post_text = form.post_text.data
        # request API posts endpoint to make new post
        payload = {'post_text': post_text}
        response = requests.post(f"{api_url}{url_for('api_posts')}", headers=headers, json=payload)
        # show notification message in a web page
        flash(response.json()['msg'], 'success')
        # response with redirect back to blog view
        return redirect(url_for('blog'))
    # request API posts endpoint to obtain all posts data
    response = requests.get(f"{api_url}{url_for('api_posts')}", headers=headers)
    # parse JSON
    blog_posts = response.json()['posts']
    # render template for blog and make HTML response
    return render_template('blog_posts.j2', user=current_user, form=form, rate_form=rate_form, posts=blog_posts)


@app.route('/web/bot')
@jwt_required()  # protect route
def bot():
    """
    View for blog bot

    :return: Flask HTML response object
    """
    # takes parameters from the app config file (config.py) and instantiate BlogBot object
    blog_bot = BlogBot(api_url, number_of_users=app.config['BOT_NUMBER_OF_USERS'],
                       max_posts_per_user=app.config['BOT_MAX_POSTS_PER_USER'],
                       max_likes_per_user=app.config['BOT_MAX_LIKES_PER_USER'])
    # run bot on the background
    blog_bot.background_run()
    # show notification message in a web page
    flash(f'Bot started {request.referrer}', 'success')
    # redirect to the origin location
    return redirect(request.referrer)


@app.route('/test')
@jwt_required(optional=True)
def test():
    current_user = get_jwt_identity()
    return jsonify({"msg": "Ok", "current_user": current_user}), 200
