from flask import (render_template, request, Blueprint,
                   redirect, url_for, flash, make_response)
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt, authorize
from app.models import User, Post, Chatroom, Living, Job, Volunteer, Family, Role, Question, Interest
from app.main.forms import RegistrationForm, SearchForm, InterestForm, QuestionForm, FamilyForm, JobForm, VolunteerForm, \
    LivingForm
from datetime import timedelta
from sqlalchemy.sql.expression import func
import pdfkit
from app.posts.utils import save_post_image
from werkzeug.exceptions import NotFound, Unauthorized

main = Blueprint('main', __name__)


@main.route("/", methods=['GET', 'POST'])
@main.route("/home/<string:order>", methods=['GET', 'POST'])
def home(order='time'):
    users = []
    form = RegistrationForm()
    init_interests()
    print(len(Interest.query.all()))
    interests = Interest.query.all()

    if form.validate_on_submit():
        user_role = Role(name="user")
        db.session.add(user_role)
        db.session.commit()
        admin_role = Role(name="admin")
        db.session.add(admin_role)
        db.session.commit()
        firstName = form.firstName.data.capitalize()
        lastName = form.lastName.data.capitalize()
        email = form.email.data.lower()
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('UTF-8')  # Encrypt the password stored in form.password.data
        user = User(FirstName=firstName, LastName=lastName,
                    Email=email, Password=hashed_password, roles=[role])
        db.session.add(user)
        db.session.commit()
        # user = db.session.query(User).get(current_user.id)

        # Login the user with the session duration set
        login_user(user, duration=timedelta)
        # Second argument is optional, uses to assign what category the message is
        flash('Signed in!', 'success')
        return redirect(url_for('main.home'))
    if current_user.is_authenticated:
        posts = Post.query.order_by(Post.DatePosted.desc()).all()
        # users = User.query.filter(User.id != current_user.id).order_by(
        #     func.random()).limit(3).all()
        tempUsers = User.query.filter(
            User.id != current_user.id).order_by(func.random()).all()
        likes = {}
        user_interests = current_user.UserInterests.all()
        print(user_interests)
        for i in range(len(posts)):
            likes[posts[i]] = len(posts[i].LikedUsers.all())
        for tempUser in tempUsers:
            if not current_user.is_following(tempUser) and len(users) <= 2:
                users.append(tempUser)
        if order == 'popularity':
            sorted_likes = sorted(likes.items(), key=lambda item: item[1], reverse=True)
            likes = {k: v for k, v in sorted_likes}
            return render_template('user-index.html', posts=likes, users=users, interests=interests, user_interests=user_interests, active='home', subactive='popularity')
        else:
            return render_template('user-index.html', posts=likes, users=users, interests=interests, user_interests=user_interests, active='home', subactive='time')

    # posts = Post.query.order_by(Post.DatePosted.desc())
    return render_template('register.html', form=form)


def init_interests():
    if len(Interest.query.all()) <= 0:
        populateInterests()


@main.route("/save_interests", methods=["GET", "POST"])
@login_required
# @authorize.has_role('user')
def save_interests():
    print("save_interests")
    if current_user.is_authenticated:
        received_interests = request.form.getlist('check')
        for received_interest in received_interests:
            interest = db.session.query(Interest).filter_by(Title=received_interest).first()
            current_user.UserInterests.append(interest)
            db.session.commit()
        print(received_interests)
        return redirect("/")

@main.route("/question/<string:order>")
@login_required
def question(order='time'):
    users = []
    if current_user.is_authenticated:
        posts = Question.query.order_by(Question.DatePosted.desc()).all()
        tempUsers = User.query.filter(
            User.id != current_user.id).order_by(func.random()).all()
        for tempUser in tempUsers:
            if not current_user.is_following(tempUser) and len(users) <= 2:
                users.append(tempUser)
        likes = {}
        for i in range(len(posts)):
            likes[posts[i]] = len(posts[i].LikedUsersQ.all())
        if order == 'popularity':
            sorted_likes = sorted(likes.items(), key=lambda item: item[1], reverse=True)
            likes = {k: v for k, v in sorted_likes}
            return render_template('question/question.html', posts=likes, users=users, active='question',
                                   subactive='popularity')
        else:
            return render_template('question/question.html', posts=likes, users=users, active='question',
                                   subactive='time')


@main.route("/create_question_post", methods=['GET', 'POST'])
@login_required
def create_question_post():
    form = QuestionForm()
    if form.validate_on_submit():
        postImage = ""
        if form.postImage.data:
            postImage = save_post_image(form.postImage.data)
        post = Question(
            Title=form.title.data,
            Content=form.content.data,
            ImageFile=postImage,
            Authorq=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash("Succesfully Posted!", category='success')
        return redirect(url_for('main.question', order='time'))
    return render_template('question/create-question-post.html', form=form, title="Make a story")


@main.route("/family")
@login_required
# @authorize.has_role('user')
def family():
    if current_user.is_authenticated:
        family_posts = Family.query.order_by(Family.DatePosted.desc()).all()
        for post in family_posts:
            print(post.Title, post.Content)
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
        chatrooms = Chatroom.query.order_by(Chatroom.id.desc()).all()
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
        job_posts = Job.query.order_by(Job.DatePosted.desc()).all()
        for post in job_posts:
            print(post.Title, post.Content)
        return render_template('job/jobs.html', posts=job_posts, active='job')


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
        volunteer_posts = Volunteer.query.order_by(Volunteer.DatePosted.desc()).all()
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
        living_posts = Living.query.order_by(Living.DatePosted.desc()).all()
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


@main.route('/schedule')
def calendar():
    return render_template('scheduler/calendar.html', active='schedule')


@main.route("/profile/<string:email>")
def friends(email):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(Email=email).first_or_404()
    visitor = User.query.filter_by(Email=current_user.Email).first_or_404()
    posts = Post.query.filter_by(Author=user) \
        .order_by(Post.DatePosted.desc()) \
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
    posts = Post.query.filter_by(Author=user) \
        .order_by(Post.DatePosted.desc()) \
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
    return render_template('suggested-people.html', users=users, active='add_friends')


def populateInterests():
    interest1 = Interest(
        Title="Science",
        ImageSource="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxAQEBIQEBAVFRIXDQ0ODQ0ODg8VDRANIBEWFiARHxUkHCggJCYlJx8TITEhJSkrLi4uFx8zODMsNygtLisBCgoKDQ0ODg4NDjcZFRkrKy0rLTcrNy0tKysrLisrLS0rNystLSsrNys3LS03KysrLSsrLSs3KzcrKysrKysrLf/AABEIAJYAZAMBIgACEQEDEQH/xAAcAAABBQEBAQAAAAAAAAAAAAAAAQIDBgcFBAj/xAA2EAACAgEDAgQEBQIFBQAAAAABAgARAwQSIQUxBgcTQSIyUWEUcYGR8KGxFSNCUvEzYmSC0f/EABkBAQEBAAMAAAAAAAAAAAAAAAABAgMEBf/EACARAQEAAgICAgMAAAAAAAAAAAABAhEhMQNBBFESInH/2gAMAwEAAhEDEQA/AMNhCEAiwEIBCo4CKRAZUAP+I/bFxjn/ANSf6QIoRahASEIQCEIQCEIQFEcBEAj1EBQJ7emdMzanIMWDGXciwoHAUdySeAB7k8Sbw/oBqNTiwsaVnpiO+0Ak196FfrNeXoydP0Gp1GnXa94STSncocDaQQQe5PII96vkTK6lv01JtTcflRrim45cANWEORif3AqVfrnh/UaJympxlCRSMCGxuLFlXHB/LuPpNaT8e+g/HnVUA1emCwv4q7XVe1cSDpGm/wAX0WoTVd1z41V0VQQdlhxY4PBBPuDzc63i+VPJlcZOm8sNTbEmEbUuHjjwovTziKZGdX3j41AKsKNWODYP9JU2Wdpx2aRxI4iNhBCEIBFAgIoEBwEkURqiejT4WdgqKWYsqqihi7MeAoA5JP0EqrH5dYwdchbsuPI5IDGuABwPua/WbH14D/C9Up4BwXiDHllV0ugee4qc7y28CtgwXm/y875VyZl4ZxhA+BAQaBsknvzxLi/h/Hj3Fwc2NgpfE6o44HzAEdx9uZnPG3HKTtrH1tl2THqMI0+kzsBgy+jmIRlKbGat5PYEC+/aWXw9jwYcmv0umyAj1sL4S2RbYDF8RvsQDxf5SzDw/wBMYWMHt2LOAP62JNi6XiCFMOHYCPhXGiqA275yTya+/A/aef4PjZ4Z/lenNlnjZplfm/q09DFhBG9sq5dvchACLvt3NTKGWbV5t+DMpx4tRiUOcYOLIFKhihawwB7kGhQ55mNZEo0fqQQRRBHcET0ZNRwZPMyyMiTsJEwhDIRYkIUCPAjRHgQHqJrfkl0UA5Nc63QbDgsWVqizgfXlRY9r+syVBPoTyuxhenaUghfgfcrcKxZ3JNgcGqlX2ueQeptfHaupIxswrcxXkEe47fwT1dP1vqjZkTa90R7FgCbH17GcnqWqbEcR73lRbU7qBPJI9gO5/KdJn3ZEVGT1AhzAFb2obAN+wJsfejDVnHDqjTJd7Rfcmvec/X6IswKs3B9nYba5/UduPznEbxDnbH6pxk4RiOR2xfOUFn4aBNULucvN1heo6DP+FyHT7DiyetqX2o+M8m3BNXX1+n1lktrGWWu111OBcnwOAw2jcrBSD8Xev0uYt53+FMeL09dgFbmXFqVAUW234cvHcnkE+5qab0nVqEAXKzr6eJceclWdqBsEjgkGwePbmcHzOxer0zVH53GJCCVYFVVw5IHY0ATJeLw1N65fObCQuJ6HEgYSMo6hFqEAEeIwR6iBIgn0b5cYWGh0xHKnS4moiqauQQe/PvPnIH+xn1D4Qx+nocA/26XCK/7gn/2WLD2yb86qKO0O2RVFIoIKKpPuSTf2AM8/WeshcuPQY3/z82MliB8qAGlsdr5r7An6Xy+ieJcWqDvgB/6i48vwkU+3nk9z9K4ozodI0mnXVsSU9cqcpLvuzbeBursBQA4rgD6Sb54bkiTy6bXKmRNZkU0VTBhtN+NF4BFADaRVDkivaevxL0FM+ny6cEoA41OP0gqlXBJNAcEE3Yru08B1JfVZEONkQPa6imIZj/qFoB7cgEzoDXvjZQXD4923kU4tfYkm+Zq5c7ZmE6ePwZ0Z9KvoHMzrubNhdFUIULD4CTdkUCSPrJ/MV8o6dqxhFv8Ahc1sQu1Er4uT77Qalb1niFtP1vT6R6GkdVfThQwrMyFNpF1V2KruQfpLX5gZgOmas/8AiZgRX1Qjt+ZEb3d0s1xHyw3/ABImkrSJpllGRCLCFII4RgjxCHibp4Z8VM+iVXAs4gpyNuBsit9CgLNE0e/MwtTLX0LXqNBq8bn5UQYjZB3NdIK5HIH7x/F3pdfKXoeTFk1fr7htyjTnGGamcKSX+/BFH6GaW+hwrkVnQLeIoroFOTaGBJJ70LH25lV8tXZtDifLkZncFy7G/iBIWzV8KAK+gl4xZfh5+lMtqQfYy6iy1G2PHXA+XaQaXefezXfiS59IuRGUrxVAgcg+zD6Tm4NWVzZEFbPSDbh3UgkBTf2/tPbm6qFxlRe/bQYigrH3v3Pv+0XUi874ZF42zNreoYNIMbYn0pd9Tqcm5KQMhLrXNcAg2CSRVSy+PvFezRZ1RLyNiOFXYb0RCQDwe5onk3z+U43mTqBgGmORsgTIdSmYIzF8mIBHGMk9lLUTX3meeIuveuNiM+3ezZN24LkPBB7/AFvih7Sc64Teu3AMY0UmNMIQiEQxYNmCPEjEeDCHrJFMiEkBgbt4Pdsei0vwmvw2IgjkMtXfH6/lLTn1xGPcBXw3Z2j85SPKvqeT8AFyfIuV007UxLIGBKke1EkA/b7SyajU77HyLRPAoBRyfy9zDccToPWjm1mpx99i4WJH0N33+nH7yzarX46FMDxYAVt5Y139h2mdeXuX1X12oH+rUYgoP+whyB+xH7S463KEHym6sKF5+5P2+8lJWc+a/Xcepy4sWNy3otqA6kN/lklAEs9zQ57ygEyxeO1A1jEd2xYmcEUboi/2AlbJidM3mluNMLgJQVCFQgRAx4Mji1CJQY4GQiOEDWfKXrNY2wGqXIWKsLAVjw372D+k0PqDoRTOqhlpk2rZX3+/7zIfKzTE5cuQA8KmE0fhG4k2R7/KK5FcnmWfxn1NtJpMi/H62RdvrbaRSxI2g9rABFew57zPtudbcXyo1WP8TqdM7UmTEGQ3VOmUgEfemmmDp+QWroHG3bvVqcr7VZnzv0rXHBmTKo+VrK+zIeCp/MEibv0freTNgBAKoEvflDeps2ghrHBFWL79uJaY/THPHOly4tdnTKwZtysrDscZW1FWaIFAj2IMrxM7njLM763MchFh2Va3Vs7jvzZBvn6zhsJYzezLjgYmyLthBcIVCAwfzmOA/lQEdAAv8qAEUD+ERa/ggaz5d67FptHtfKwZicm3Y3pqDVAEDknuSfsBxOJ5jeJV1SjCMYBGS1dMinGwHdyK4PsPsTK3g68yoE2jhQAQzAcCrIqczNlLsWPf+01lMdSztjDLPdmXSIJNt8H+KNM+nAFYQpRVV33ZCoHzXR7EHiqmK3Pb03qTYDwLF2VJqm+oMmMlv7NZXKTePbveZao+s9bHl3h05pFRlI4o0BfB4J5oUe0qNT3dU6gc5B21W6husm54ZcpJdRMblZvIhjajjGzLRtQjq/lRICCOuJCAXHCEICgxbhCAtwuEICGITCEBIkIQohCED//Z"
    )
    interest2 = Interest(
        Title="Books",
        ImageSource="https://i.pinimg.com/736x/18/fc/c3/18fcc378c67c941f028dd37008df24fe--redd-foxx-funny-people.jpg"
    )
    interest3 = Interest(
        Title="Photography",
        ImageSource="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQsiViwtNmqi1XuSE96XbIdHxbKG1uphIWBsk-8d-1MNTrKQSniMQ"
    )
    interest4 = Interest(
        Title="Technology",
        ImageSource="http://files.abovetopsecret.com/files/img/to56cb7f32.jpg"
    )
    interest5 = Interest(
        Title="Education",
        ImageSource="data:image/jpeg;base64,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"
    )
    interest6 = Interest(
        Title="Cloud Computing",
        ImageSource="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTg9empmm9j40YUfl-44iaPC7637Gv-r-5Uh8DmJy1gXfcdJcTG"
    )
    interest7 = Interest(
        Title="Movies",
        ImageSource="https://images.pexels.com/photos/390089/film-movie-motion-picture-390089.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    )
    interest8 = Interest(
        Title="Health",
        ImageSource="https://images.pexels.com/photos/235922/pexels-photo-235922.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    )
    interest9 = Interest(
        Title="Business",
        ImageSource="https://images.pexels.com/photos/872957/pexels-photo-872957.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    )
    interest10 = Interest(
        Title="Cooking",
        ImageSource="https://images.pexels.com/photos/277253/pexels-photo-277253.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    )
    interest11 = Interest(
        Title="Big Data",
        ImageSource="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQNOE77gmOh5uxrsPxQNG3HJdQOPLXlXNb8iDYKHdrI2eA1OwGLXA"
    )
    interest12 = Interest(
        Title="Angular Js",
        ImageSource="data:image/jpeg;base64,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"
    )
    interest13 = Interest(
        Title="Food",
        ImageSource="https://images.pexels.com/photos/5317/food-salad-restaurant-person.jpg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    )
    interest14 = Interest(
        Title="Money",
        ImageSource="https://images.pexels.com/photos/47344/dollar-currency-money-us-dollar-47344.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    )
    interest15 = Interest(
        Title="Adventure",
        ImageSource="https://images.pexels.com/photos/6758/wildernessculture-rei1440project-welltravelled-awesomeearth.jpg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    )
    interest16 = Interest(
        Title="Design",
        ImageSource="https://images.pexels.com/photos/5836/yellow-metal-design-decoration.jpg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    )
    interest17 = Interest(
        Title="Sports",
        ImageSource="https://images.pexels.com/photos/207710/pexels-photo-207710.jpeg?auto=compress&cs=tinysrgb&h=350"
    )
    interest18 = Interest(
        Title="Shopping",
        ImageSource="https://images.pexels.com/photos/972804/pexels-photo-972804.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
    )
    db.session.add(interest1)
    db.session.add(interest2)
    db.session.add(interest3)
    db.session.add(interest4)
    db.session.add(interest5)
    db.session.add(interest6)
    db.session.add(interest7)
    db.session.add(interest8)
    db.session.add(interest9)
    db.session.add(interest10)
    db.session.add(interest11)
    db.session.add(interest12)
    db.session.add(interest13)
    db.session.add(interest14)
    db.session.add(interest15)
    db.session.add(interest16)
    db.session.add(interest17)
    db.session.add(interest18)
    db.session.commit()
