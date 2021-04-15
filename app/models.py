from datetime import datetime
# Use to generate token
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from app import db, login_manager
from flask_login import UserMixin
from flask_authorize import RestrictionsMixin, AllowancesMixin


UserGroup = db.Table(
    'user_group', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)


UserRole = db.Table(
    'user_role', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)



# This is where the session or current_user gets the data when login_user is triggered
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


Followers = db.Table('followers',
                     db.Column('follower_id', db.Integer,
                               db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer,
                               db.ForeignKey('user.id'))
                     )

UserLikedPosts = db.Table('user_liked_posts',
                          db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                          db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
                          )

UserLikedQuestions = db.Table('user_liked_questions',
                          db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                          db.Column('question_id', db.Integer, db.ForeignKey('question.id'))
                          )

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(20), nullable=False)
    LastName = db.Column(db.String(20), nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    Password = db.Column(db.String(60), nullable=False)
    ProfilePicture = db.Column(
        db.String(20), nullable=False, default='default.png')
    Posts = db.relationship('Post', backref='Author', lazy=True)
    # Questions = db.relationship('Question',backref='Authorq',lazy=True)
    ChatroomId = db.Column(db.Integer, db.ForeignKey('chatroom.id'))
    Followed = db.relationship('User', secondary=Followers, primaryjoin=(Followers.c.follower_id == id),
                               secondaryjoin=(Followers.c.followed_id == id),
                               backref=db.backref('Followers', lazy='dynamic'), lazy='dynamic')
    UserLikedPosts = db.relationship('Post',primaryjoin=(UserLikedPosts.c.user_id == id), secondary=UserLikedPosts,backref=db.backref('LikedUsers', lazy='dynamic'), lazy='dynamic')
    # UserLikedQuestions = db.relationship('Question', primaryjoin=(UserLikedQuestions.c.user_id == id), secondary=UserLikedQuestions,
    #                                  backref=db.backref('LikedUsers', lazy='dynamic'), lazy='dynamic')
    roles = db.relationship('Role', secondary=UserRole)
    groups = db.relationship('Group', secondary=UserGroup)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        # Store the token into SECRET_KEY.
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        # Get the token stored in SECRET_KEY.
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            # Load or Decrypt the token stored in SECRET_KEY.
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    # Function to print the value of User model

    def __repr__(self):
        return f"User('{self.FirstName}', '{self.LastName}', '{self.Email}', '{self.ProfilePicture}')"

    def follow(self, user):
        if not self.is_following(user):
            self.Followed.append(user)

    def like(self, post):
        if not self.has_liked(post):
            self.UserLikedPosts.append(post)

    def like_q(self, question):
        if not self.has_liked_q(question):
            self.UserLikedQuestions.append(question)

    def unfollow(self, user):
        if self.is_following(user):
            self.Followed.remove(user)

    def is_following(self, user):
        return self.Followed.filter(Followers.c.followed_id == user.id).count() > 0

    def has_liked(self, post):
        return self.UserLikedPosts.filter(UserLikedPosts.c.post_id == post.id ).count() > 0

    def has_liked_q(self, question):
        return self.UserLikedQuestions.filter(UserLikedQuestions.c.question_id == question.id ).count() > 0

    def followed_posts(self):
        Followed = Post.query.join(Followers, (Followers.c.followed_id == Post.UserID)).filter(
            Followers.c.follower_id == self.id)
        own = Post.query.filter_by(UserID=self.id)
        return Followed.union(own).order_by(Post.DatePosted.desc())

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(100), nullable=False)
    DatePosted = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    Content = db.Column(db.Text, nullable=False)
    ImageFile = db.Column(db.String(20))
    # UserID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Question('{self.Title}', '{self.DatePosted}')"

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(100), nullable=False)
    DatePosted = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    Content = db.Column(db.Text, nullable=False)
    ImageFile = db.Column(db.String(20))


class Group(db.Model, RestrictionsMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)


class Role(db.Model, AllowancesMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(100), nullable=False)
    ImageFile = db.Column(db.String(20))
    DatePosted = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    Content = db.Column(db.Text, nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.Title}', '{self.DatePosted}')"

class Interest(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    Chess = db.Column(db.Boolean)
    Sudoku = db.Column(db.Boolean)
    Crosswords = db.Column(db.Boolean)
    Job = db.Column(db.Boolean)
    Volunteer = db.Column(db.Boolean)
    Dating = db.Column(db.Boolean)



class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Content = db.Column(db.Text, nullable=False)
    OwnerUser = db.relationship('User', uselist=False)
    OwnerUserId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    DatePosted = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    ChatroomId = db.Column(db.Integer, db.ForeignKey('chatroom.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.Title}', '{self.DatePosted}')"


class Chatroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(100), nullable=False)
    Chats = db.relationship('Chat', backref="Chatroom")
    Members = db.relationship('User', backref="MemberChatrooms")

class Living(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(100), nullable=False)
    DatePosted = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    Content = db.Column(db.Text, nullable=False)
    ImageFile = db.Column(db.String(20))

class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(100), nullable=False)
    DatePosted = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    Content = db.Column(db.Text, nullable=False)
    ImageFile = db.Column(db.String(20))


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(100), nullable=False)
    DatePosted = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    Content = db.Column(db.Text, nullable=False)
    ImageFile = db.Column(db.String(20))

class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(100), nullable=False)
    DatePosted = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    Content = db.Column(db.Text, nullable=False)
    ImageFile = db.Column(db.String(20))

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    class1 = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime,nullable=False)
    end_date = db.Column(db.DateTime,nullable=False)
