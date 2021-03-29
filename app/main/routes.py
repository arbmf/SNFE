from flask import (render_template, request, Blueprint,
                   redirect, url_for, flash, make_response)
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User, Post, Chatroom, Living,News,Job,Volunteer,Family
from app.main.forms import RegistrationForm, SearchForm, InterestForm
from datetime import timedelta
from sqlalchemy.sql.expression import func
import pdfkit
from app.main.forms import  FamilyForm,JobForm,VolunteerForm,NewsForm,LivingForm
from app.posts.utils import save_post_image

main = Blueprint('main', __name__)


@main.route("/", methods=['GET', 'POST'])
def home():
    users = []
    form = RegistrationForm()
    if form.validate_on_submit():
        firstName = form.firstName.data.capitalize()
        lastName = form.lastName.data.capitalize()
        email = form.email.data.lower()
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('UTF-8')  # Encrypt the password stored in form.password.data
        user = User(FirstName=firstName, LastName=lastName,
                    Email=email, Password=hashed_password)
        db.session.add(user)
        db.session.commit()
        # Login the user with the session duration set
        login_user(user, duration=timedelta)
        # Second argument is optional, uses to assign what category the message is
        flash('Signed in!', 'success')
        return redirect(url_for('main.home'))
    if current_user.is_authenticated:
        posts = current_user.followed_posts().all()
        # users = User.query.filter(User.id != current_user.id).order_by(
        #     func.random()).limit(3).all()
        tempUsers = User.query.filter(
            User.id != current_user.id).order_by(func.random()).all()

        for tempUser in tempUsers:
            if not current_user.is_following(tempUser) and len(users) <= 2:
                users.append(tempUser)

        return render_template('user-index.html', posts=posts, users=users, active='home')

    # posts = Post.query.order_by(Post.DatePosted.desc())
    return render_template('index.html', form=form)

@main.route("/family")
@login_required
def family():
    if current_user.is_authenticated:
        family_posts = Family.query.all()
        for post in family_posts:
            print(post.Title,post.Content)
        return render_template('family/family.html', posts=family_posts, active='family')

@main.route("/create_family_post", methods=['GET', 'POST'])
@login_required
def create_family_post():
    form = FamilyForm()
    if form.validate_on_submit():
        postImage = ""
        if form.postImage.data:
            postImage = save_post_image(form.postImage.data)
        post = Family(
            Title=form.title.data,
            Content=form.content.data,
            ImageFile=postImage
        )
        db.session.add(post)
        db.session.commit()
        flash("Succesfully Posted!", category='success')
        return redirect(url_for('main.family'))

    return render_template('family/create-family-post.html', form=form, title="Make a story")

@main.route("/chatrooms")
@login_required
def chatroom():
    chatrooms = []
    if current_user.is_authenticated:
        chatrooms = Chatroom.query.all()
        for chatroom in chatrooms:
            print(chatroom.Title)

    return render_template('chatroom/chatrooms.html', chatrooms=chatrooms, active='chatroom')

@main.route("/groups")
@login_required
def group():
    users = []
    if current_user.is_authenticated:
        posts = current_user.followed_posts().all()
        tempUsers = User.query.filter(
            User.id != current_user.id).order_by(func.random()).all()
        for tempUser in tempUsers:
            if not current_user.is_following(tempUser) and len(users) <= 2:
                users.append(tempUser)
        return render_template('group/groups.html', posts=posts, users=users, active='group')

@main.route("/dating")
@login_required
def dating():
    users = []
    if current_user.is_authenticated:
        posts = current_user.followed_posts().all()
        tempUsers = User.query.filter(
            User.id != current_user.id).order_by(func.random()).all()
        for tempUser in tempUsers:
            if not current_user.is_following(tempUser) and len(users) <= 2:
                users.append(tempUser)
        return render_template('dating/dating.html', posts=posts, users=users, active='dating')

@main.route("/job")
@login_required
def job():
    if current_user.is_authenticated:
        job_posts = Job.query.all()
        for post in job_posts:
            print(post.Title, post.Content)
        return render_template('job/jobs.html', posts=job_posts, active='family')

@main.route("/create_job_post", methods=['GET', 'POST'])
@login_required
def create_job_post():
    form = JobForm()
    if form.validate_on_submit():
        postImage = ""
        if form.postImage.data:
            postImage = save_post_image(form.postImage.data)
        post = Job(
            Title=form.title.data,
            Content=form.content.data,
            ImageFile=postImage
        )
        db.session.add(post)
        db.session.commit()
        flash("Succesfully Posted!", category='success')
        return redirect(url_for('main.job'))

    return render_template('job/create-job-post.html', form=form, title="Make a story")

@main.route("/volunteer")
@login_required
def volunteer():
    if current_user.is_authenticated:
        volunteer_posts = Volunteer.query.all()
        for post in volunteer_posts:
            print(post.Title, post.Content)
        return render_template('volunteer/volunteers.html', posts=volunteer_posts, active='volunteer')

@main.route("/create_volunteer_post", methods=['GET', 'POST'])
@login_required
def create_volunteer_post():
    form = VolunteerForm()
    if form.validate_on_submit():
        postImage = ""
        if form.postImage.data:
            postImage = save_post_image(form.postImage.data)
        post = Volunteer(
            Title=form.title.data,
            Content=form.content.data,
            ImageFile=postImage
        )
        db.session.add(post)
        db.session.commit()
        flash("Succesfully Posted!", category='success')
        return redirect(url_for('main.volunteer'))

    return render_template('volunteer/create-volunteer-post.html', form=form, title="Make a story")

@main.route("/living")
@login_required
def living():
    if current_user.is_authenticated:
        living_posts = Living.query.all()
        for post in living_posts:
            print(post.Title, post.Content)
        return render_template('living/living.html', posts=living_posts, active='living')

@main.route("/create_living_post", methods=['GET', 'POST'])
@login_required
def create_living_post():
    form = LivingForm()
    if form.validate_on_submit():
        postImage = ""
        if form.postImage.data:
            postImage = save_post_image(form.postImage.data)
        post = Living(
            Title=form.title.data,
            Content=form.content.data,
            ImageFile=postImage
        )
        db.session.add(post)
        db.session.commit()
        flash("Succesfully Posted!", category='success')
        return redirect(url_for('main.living'))

    return render_template('living/create-living-post.html', form=form, title="Make a story")

@main.route("/games")
@login_required
def game():
    users = []
    if current_user.is_authenticated:
        posts = current_user.followed_posts().all()
        tempUsers = User.query.filter(
            User.id != current_user.id).order_by(func.random()).all()
        for tempUser in tempUsers:
            if not current_user.is_following(tempUser) and len(users) <= 2:
                users.append(tempUser)
        return render_template('games/games.html', posts=posts, users=users, active='games')

@main.route("/news")
@login_required
def news():
    if current_user.is_authenticated:
        news_posts = News.query.all()
        for post in news_posts:
            print(post.Title, post.Content)
        return render_template('news/news.html', posts=news_posts, active='news')

@main.route("/create_news_post", methods=['GET', 'POST'])
@login_required
def create_news_post():
    form = NewsForm()
    if form.validate_on_submit():
        postImage = ""
        if form.postImage.data:
            postImage = save_post_image(form.postImage.data)
        post = News(
            Title=form.title.data,
            Content=form.content.data,
            ImageFile=postImage
        )
        db.session.add(post)
        db.session.commit()
        flash("Succesfully Posted!", category='success')
        return redirect(url_for('main.news'))

    return render_template('news/create-news-post.html', form=form, title="Make a story")

@main.route('/schedule')
def calendar():
    return render_template('scheduler/calendar.html')

@main.route("/profile/<string:email>")
def friends(email):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(Email=email).first_or_404()
    visitor = User.query.filter_by(Email=current_user.Email).first_or_404()
    posts = Post.query.filter_by(Author=user)\
        .order_by(Post.DatePosted.desc())\
        .paginate(page=page, per_page=5)

    followers = user.Followers.all()
    following = user.Followed.all()

    friends = []
    friendlists = []

    if len(followers) > len(following):
        for follower in followers:
            for followed in following:
                if (followed.id == follower.id):
                    friendlists.append(followed.id)
    else:
        for followed in following:
            for follower in followers:
                if (followed.id == follower.id):
                    friendlists.append(follower.id)

    visitorFollowers = visitor.Followers.all()
    visitorFollowing = visitor.Followed.all()

    visitorFriends = []
    visitorFriendlists = []

    if len(visitorFollowers) > len(visitorFollowing):
        for follower in visitorFollowers:
            for followed in visitorFollowing:
                if (followed.id == follower.id):
                    visitorFriendlists.append(followed.id)
    else:
        for followed in visitorFollowing:
            for follower in visitorFollowers:
                if (followed.id == follower.id):
                    visitorFriendlists.append(follower.id)

    # Compare if they have same friends using the user id's.
    mutuals = []

    if len(visitorFriendlists) > len(friendlists):
        for user1 in visitorFriendlists:
            for user2 in friendlists:
                if user1 == user2:
                    mutuals.append(user2)
    else:
        for user1 in friendlists:
            for user2 in visitorFriendlists:
                if user1 == user2:
                    mutuals.append(user2)

    for friendlist in friendlists:
        friends.append(User.query.filter_by(id=friendlist).first())

    return render_template('user-profile.html', posts=posts, user=user,
                           active=('profile' if user.Email ==
                                   current_user.Email else ''),
                           followers=followers, following=following, friends=friends,
                           friendlists=friendlists, visitorFriendlists=visitorFriendlists, mutuals=mutuals)

@main.route("/profile/<string:email>")
def user_profile(email):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(Email=email).first_or_404()
    visitor = User.query.filter_by(Email=current_user.Email).first_or_404()
    posts = Post.query.filter_by(Author=user)\
        .order_by(Post.DatePosted.desc())\
        .paginate(page=page, per_page=5)

    followers = user.Followers.all()
    following = user.Followed.all()

    friends = []
    friendlists = []

    if len(followers) > len(following):
        for follower in followers:
            for followed in following:
                if (followed.id == follower.id):
                    friendlists.append(followed.id)
    else:
        for followed in following:
            for follower in followers:
                if (followed.id == follower.id):
                    friendlists.append(follower.id)

    visitorFollowers = visitor.Followers.all()
    visitorFollowing = visitor.Followed.all()

    visitorFriends = []
    visitorFriendlists = []

    if len(visitorFollowers) > len(visitorFollowing):
        for follower in visitorFollowers:
            for followed in visitorFollowing:
                if (followed.id == follower.id):
                    visitorFriendlists.append(followed.id)
    else:
        for followed in visitorFollowing:
            for follower in visitorFollowers:
                if (followed.id == follower.id):
                    visitorFriendlists.append(follower.id)

    # Compare if they have same friends using the user id's.
    mutuals = []

    if len(visitorFriendlists) > len(friendlists):
        for user1 in visitorFriendlists:
            for user2 in friendlists:
                if user1 == user2:
                    mutuals.append(user2)
    else:
        for user1 in friendlists:
            for user2 in visitorFriendlists:
                if user1 == user2:
                    mutuals.append(user2)

    for friendlist in friendlists:
        friends.append(User.query.filter_by(id=friendlist).first())

    return render_template('user-profile.html', posts=posts, user=user,
                           active=('profile' if user.Email ==
                                   current_user.Email else ''),
                           followers=followers, following=following, friends=friends,
                           friendlists=friendlists, visitorFriendlists=visitorFriendlists, mutuals=mutuals)


@main.route("/search", methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        inp = form.inp.data.lower()
        results = User.query.filter(User.Email.contains(inp))

        return render_template('search-list.html', results=results, form=form)

    return render_template('search-list.html', form=form)


@main.route("/profile/print-user-data/<string:email>")
def pdf_template(email):

    user = User.query.filter_by(Email=email).first()
    visitor = User.query.filter_by(Email=current_user.Email).first_or_404()

    followers = user.Followers.all()
    following = user.Followed.all()

    friends = []
    friendlists = []

    if len(followers) > len(following):
        for follower in followers:
            for followed in following:
                if (followed.id == follower.id):
                    friendlists.append(followed.id)
    else:
        for followed in following:
            for follower in followers:
                if (followed.id == follower.id):
                    friendlists.append(follower.id)

    visitorFollowers = visitor.Followers.all()
    visitorFollowing = visitor.Followed.all()

    visitorFriends = []
    visitorFriendlists = []

    if len(visitorFollowers) > len(visitorFollowing):
        for follower in visitorFollowers:
            for followed in visitorFollowing:
                if (followed.id == follower.id):
                    visitorFriendlists.append(followed.id)
    else:
        for followed in visitorFollowing:
            for follower in visitorFollowers:
                if (followed.id == follower.id):
                    visitorFriendlists.append(follower.id)

    # Compare if they have same friends using the user id's.
    mutuals = []

    if len(visitorFriendlists) > len(friendlists):
        for user1 in visitorFriendlists:
            for user2 in friendlists:
                if user1 == user2:
                    mutuals.append(user2)
    else:
        for user1 in friendlists:
            for user2 in visitorFriendlists:
                if user1 == user2:
                    mutuals.append(user2)

    for friendlist in friendlists:
        friends.append(User.query.filter_by(id=friendlist).first())

    rendered = render_template(
        'pdf-template.html', friends=friends, posts=user.Posts, user=user, mutuals=mutuals, followers=followers)
    pdf = pdfkit.from_string(rendered, False)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=output.pdf'

    return response


@main.route("/suggested-people")
def suggested_people():
    users = []
    tempUsers = User.query.filter(
        User.id != current_user.id).order_by(func.random()).all()

    for tempUser in tempUsers:
        if not current_user.is_following(tempUser):
            users.append(tempUser)
    return render_template('suggested-people.html', users=users, active='home')
