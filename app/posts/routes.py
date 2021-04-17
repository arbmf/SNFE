from flask import (render_template, url_for, flash,
                   redirect, request, Blueprint)
from flask_login import current_user, login_required
from app import db, Interest
from app.models import Post, User,Family,Job,Living,Volunteer,Question,Answer
from app.posts.forms import NewPost,AnswerForm
from app.posts.utils import save_post_image
from datetime import timedelta
from app import socketio

# The first argument is use to navigate different routes using that Blueprint
posts = Blueprint('posts', __name__)


@posts.route("/create_post", methods=['GET', 'POST'])
@login_required
def create_post():
    form = NewPost()
    if form.validate_on_submit():
        postImage = ""
        if form.postImage.data:
            postImage = save_post_image(form.postImage.data)
        received_interests = request.form.getlist('check')
        interests_db = []
        for received_interest in received_interests:
            interest = db.session.query(Interest).filter_by(Title=received_interest).first()
            interests_db.append(interest)
        post = Post(
            Title=form.title.data,
            Content=form.content.data,
            ImageFile=postImage,
            Author=current_user,
            PostInterests=interests_db
        )
        db.session.add(post)
        db.session.commit()
        flash("Succesfully Posted!", category='success')
        return redirect(url_for('users.profile'))
    interests = Interest.query.all()
    return render_template('posts/create-post.html', form=form, interests=interests, title="Make a story")


@posts.route("/posts/<int:postID>", methods=['GET', 'POST'])
def post(postID):
    post = Post.query.get_or_404(postID)
    socketio.on_event("like", like)
    user = db.session.query(User).get(current_user.id)
    print(user.has_liked(post))
    likedUsers = len(post.LikedUsers.all())
    interests = post.PostInterests.all()
    return render_template('posts/post.html', title="Posts", post=post, interests=interests, likedUsers=likedUsers)

@posts.route("/questions/<int:questionID>", methods=['GET', 'POST'])
def question(questionID):
    form = AnswerForm()
    if form.validate_on_submit():
        post = Answer(
            Content=form.content.data,
            QuestionID=questionID,
            Authora=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash("Succesfully Answered!", category='success')
        return redirect(url_for('posts.question',questionID=questionID))
    post = Question.query.get_or_404(questionID)
    answers = Answer.query.filter(Answer.QuestionID==questionID)
    print(answers)
    socketio.on_event("likeq", likeq)
    user = db.session.query(User).get(current_user.id)
    print(user.has_liked_q(post))
    likedUsersQ = len(post.LikedUsersQ.all())
    return render_template('question/question_post.html', title="Questions", post=post,likedUsersQ=likedUsersQ,answers=answers,form=form)

@posts.route("/family_posts/<int:postID>", methods=['GET', 'POST'])
def family_post(postID):
    post = Family.query.get_or_404(postID)
    return render_template('family/family_post.html', title="Posts", post=post)


@posts.route("/job_post/<int:postID>", methods=['GET', 'POST'])
def job_post(postID):
    post = Job.query.get_or_404(postID)
    return render_template('job/job_post.html', title="Posts", post=post)

@posts.route("/vol_post/<int:postID>", methods=['GET', 'POST'])
def vol_post(postID):
    post = Volunteer.query.get_or_404(postID)
    return render_template('volunteer/volunteer_post.html', title="Posts", post=post)

@posts.route("/living_post/<int:postID>", methods=['GET', 'POST'])
def living_post(postID):
    post = Living.query.get_or_404(postID)
    return render_template('living/living_post.html', title="Posts", post=post)

@socketio.on("like")
def like(postID):
    print(postID)
    # chatroom = Chatroom.query.get_or_404(room_id)
    post = Post.query.get_or_404(postID)
    user = db.session.query(User).get(current_user.id)
    if(not user.has_liked(post)):
        user.like(post)
        db.session.commit()
    likedUsers = len(post.LikedUsers.all())
    socketio.emit("likedUsers", {"likedUsers": likedUsers})
    # user.ChatroomId = chatroom.id
    # chatroom.Members.append(user)
    # db.session.commit()
    # flask_socketio.join_room(room_id)
    # socketio.emit("join_b", {"ProfilePicture": current_user.ProfilePicture,
    #                          "FirstName": current_user.FirstName,
    #                          "Members" : getMembersAsList(chatroom.Members)
    #                          }
    #               , room=room_id)
    print(user.has_liked(post))

@socketio.on("likeq")
def likeq(questionID):
    print(questionID)
    post = Question.query.get_or_404(questionID)
    user = db.session.query(User).get(current_user.id)
    if(not user.has_liked_q(post)):
        user.like_q(post)
        db.session.commit()
    likedUsersQ = len(post.LikedUsersQ.all())
    socketio.emit("likedUsersQ", {"likedUsersQ": likedUsersQ})
    print(user.has_liked_q(post))


@posts.route("/posts/<int:postID>/update", methods=['GET', 'POST'])
@login_required
def update_post(postID):
    post = Post.query.get_or_404(postID)
    if post.Author != current_user:
        abort(403)
    form = NewPost()
    if form.validate_on_submit():
        if form.postImage.data:
            postImage = save_post_image(form.postImage.data)
            post.ImageFile = postImage
        post.Title = form.title.data
        post.Content = form.content.data
        db.session.commit()
        return redirect(url_for('posts.post', postID=post.id))
    elif request.method == 'GET':
        form.title.data = post.Title
        form.content.data = post.Content
        form.postImage.data = post.ImageFile
    return render_template('posts/update-post.html', title="Update Post", form=form, post=post)


@posts.route("/posts/<int:postID>/delete", methods=['POST'])
@login_required
def delete_post(postID):
    post = Post.query.get_or_404(postID)
    if post.Author != current_user:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    flash("Post has been deleted", category='danger')
    return redirect(url_for('users.profile'))
