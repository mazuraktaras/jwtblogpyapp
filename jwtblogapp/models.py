from jwtblogapp import database
from passlib.hash import pbkdf2_sha512


class User(database.Model):
    # The table with user credentials in database
    __tablename__ = 'blog_users'

    # Description of a record in database
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(128), unique=True)  # column for username
    password = database.Column(database.String(512))  # column for hashed password
    created_time = database.Column(database.DateTime)

    def store(self):
        """
        Add a new record to database and save it
        """
        database.session.add(self)
        database.session.commit()

    def make_hash(self):
        """
        Make a hash of native password by sha512 algorithm
        """
        self.password = pbkdf2_sha512.hash(self.password)

    def ensure_password(self, password):
        """
        Takes password and checks if it matches the hash
        :rtype: bool
        """
        return pbkdf2_sha512.verify(password, self.password)

    def __repr__(self):
        return f'{self.username}'


class RevokedToken(database.Model):
    # The table with revoked tokens in database
    __tablename__ = 'revoked_tokens'

    # Description of a record in database
    id = database.Column(database.Integer, primary_key=True)
    jti = database.Column(database.String(128))  # column for JW token identifier

    def store(self):
        """
        Add a new record to database and save it
        """
        database.session.add(self)
        database.session.commit()


class Post(database.Model):
    # The table with posts in database
    __tablename__ = 'posts'

    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer)
    username = database.Column(database.String(128))  # column for username
    text = database.Column(database.UnicodeText)  # column for post text
    likes = database.Column(database.Integer)  # column for post likes count
    dislikes = database.Column(database.Integer)  # column for post dislikes count
    created_time = database.Column(database.DateTime)

    def store(self):
        """
        Add a new record to database and save it
        """
        database.session.add(self)
        database.session.commit()

    @staticmethod
    def update():
        """
        Update a record in database
        """
        database.session.commit()


class Rating(database.Model):
    # The table with ratings in database
    __tablename__ = 'ratings'

    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer)  # column for user id
    post_like_id = database.Column(database.Integer)  # column for post id liked by user
    post_dislike_id = database.Column(database.Integer)  # column for post id disliked by user
    created_time = database.Column(database.DateTime)

    def store(self):
        """
        Add a new record to database and save it
        """
        database.session.add(self)
        database.session.commit()

    @staticmethod
    def update():
        """
        Update a record in the database
        """
        database.session.commit()

    @staticmethod
    def del_indifferent():
        """
        Delete unused (indifferent liked) records in the database
        """
        database.session.query(Rating).filter_by(post_like_id=None, post_dislike_id=None).delete()
        database.session.commit()
