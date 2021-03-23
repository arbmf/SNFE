import flask_socketio
import json
from flask import (render_template, url_for, flash,
                   redirect, request, Blueprint, session)
from flask_login import current_user, login_required
from app import db
from app.models import Chatroom, User, Chat
from app.chatrooms.forms import NewChatroom, NewChat

from datetime import timedelta

# The first argument is use to navigate different routes using that Blueprint
from app import socketio

chatrooms = Blueprint('chatrooms', __name__)


@chatrooms.route("/create_chatroom", methods=['GET', 'POST'])
@login_required
def create_chatroom():
    form = NewChatroom()
    if form.validate_on_submit():
        chat_room = Chatroom(
            Title=form.title.data,
            OwnerUser=current_user
        )
        db.session.add(chat_room)
        db.session.commit()
        flash("Succesfully Created!", category='success')
        return redirect(url_for('main.chatroom'))

    return render_template('chatroom/create-chatroom.html', form=form, title="Make a chatroom")


@chatrooms.route("/chatrooms/<int:chatroomID>", methods=['GET', 'POST'])
def chatroom(chatroomID):
    chatroom = Chatroom.query.get_or_404(chatroomID)
    members = db.session.query(User).with_parent(chatroom).all()
    chats = db.session.query(Chat).with_parent(chatroom).all()
    # flask_socketio.join_room(chatroom.id)
    socketio.on_event("join",join)
    socketio.on_event("disconnect",disconnect)
    socketio.on_event("chat",create_and_update_chats)
    return render_template('chatroom/chatroom.html', title="Chatroom", chatroom=chatroom, members=members, chats=chats)

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')

def join(roomID):
    session['room'] = roomID
    flask_socketio.join_room(roomID)

@socketio.on("chat")
def create_and_update_chats(message, methods=['GET','POST']):
    room = session.get('room')
    chatroom = Chatroom.query.get_or_404(room)
    chat = Chat(
        Content=message['data'],
        OwnerUser=current_user,
        ChatroomId = room
    )
    # db.session.add(chat)
    # db.session.commit()
    socketio.emit("chat_b",{"message": message['data'],
                            "ProfilePicture": current_user.ProfilePicture,
                            "FirstName": current_user.FirstName
                            }
                  ,room=room)
@chatrooms.route("/posts/<int:postID>/update", methods=['GET', 'POST'])
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


@chatrooms.route("/posts/<int:postID>/delete", methods=['POST'])
@login_required
def delete_post(postID):
    post = Post.query.get_or_404(postID)
    if post.Author != current_user:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    flash("Post has been deleted", category='danger')
    return redirect(url_for('users.profile'))

