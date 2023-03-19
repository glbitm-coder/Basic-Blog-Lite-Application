import os
from flask import Blueprint, Flask, request, redirect, flash, url_for
from flask import render_template
from flask_login import login_required, current_user
from .models import Blog, Like, User, Comment, Follow
from . import db
from sqlalchemy.sql import func
import datetime
import pytz
from werkzeug.utils import secure_filename


view = Blueprint('home_views', __name__)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def current_user_following_ids():
    following_details_id = []
    user_stored_following = current_user.stored_following
    for following in user_stored_following:
        tuples = db.session.query(User.id).filter(
            following.stored_following_id == User.id).first()
        following_details_id = following_details_id + [tuples[0]]
    return following_details_id


@view.route('/profile')
@login_required
def profile():
    user_all_blogs = Blog.query.filter(Blog.author == current_user.id).order_by(
        Blog.stored_timestamp.desc()).all()
    return render_template('profile.html', user=current_user, blogs=user_all_blogs)

@view.route('/')
def home():
    return redirect('/login')


# Show posts of our and to all people we are following
@view.route('/feed')
@login_required
def feed():
    current_user_all_following_ids = current_user_following_ids() + \
        [current_user.id]
    user_all_blogs = Blog.query.filter(Blog.author.in_(
        current_user_all_following_ids)).order_by(Blog.stored_timestamp.desc()).all()
    return render_template('feed.html', user=current_user, blogs=user_all_blogs)


@view.route("/create-blog", methods=['GET', 'POST'])
@login_required
def create_blog():
    if request.method == "POST":
        input_caption = request.form.get('caption')
        input_title = request.form.get('title')

        blog_file = request.files.get('url')
        # This works when we don't put enctype in form, which is used for multipart data
        if 'url' not in request.files:
            flash('No file part')
            return render_template('create_blog.html', user=current_user)
        if not input_title:
            flash('Title cannot be empty', category="error")
        elif not input_caption:
            flash('Caption cannot be empty', category="error")
        elif blog_file.filename == '':
            flash('No image selected for uploading', category="error")
        else:
            if blog_file and allowed_file(blog_file.filename):
                blog = Blog(stored_caption=input_caption, stored_title=input_title, author=current_user.id,
                            stored_timestamp=datetime.datetime.now(pytz.timezone('Asia/Kolkata')))
                db.session.add(blog)
                db.session.commit()
                # We have to create unique name otherwise images get replaced or on deleting from one user end, it would automatically delete in other user
                filename = "user_" + str(current_user.id) + "_blogs_" + \
                    str(blog.id) + "_" + secure_filename(blog_file.filename)
                blog_file.save(os.path.join(
                    view.root_path, 'static/blogs/', filename))
                input_url = "/static/blogs/" + filename
                blog.stored_url = input_url
                db.session.commit()
                flash('Blog created successfully', category="success")
                return redirect('/user/' + str(current_user.id) + '/blogs')
            else:
                flash('Image should be in jpg, jpeg or png format', category="error")
    return render_template('create_blog.html', user=current_user, previous_page = request.referrer)


@view.route("/delete-blog/<int:id>")
@login_required
def delete_blog(id):
    blog = Blog.query.filter_by(id=id).first()

    if not blog:
        flash("Blog does not exist", category="error")
    elif blog.author != current_user.id:
        flash("You do not have permission to delete this blog", category="error")
    else:
        folder_path = os.path.realpath(os.path.dirname(__file__))
        replaced_string = folder_path.replace("\\", "/")
        os.remove(replaced_string + blog.stored_url)
        db.session.delete(blog)
        db.session.commit()
        flash("Blog deleted successfully", category="success")

    return redirect(request.referrer)


@view.route("/edit-blog/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_blog(id):
    blog = Blog.query.filter_by(id=id).first()
    if request.method == "GET":
        if not blog:
            flash(f'There is no blog with id {id}', category="error")
            return redirect(url_for('home_views.profile'))
        elif blog.author != current_user.id:
            flash("You do not have permission to delete this blog", category="error")
        else:
            return render_template('edit_blog.html', user=current_user, show_blog=blog)
    elif request.method == "POST":
        input_caption = request.form.get('caption')
        input_title = request.form.get('title')
        if not input_title:
            flash('Title cannot be empty', category="error")
        elif not input_caption:
            flash('Caption cannot be empty', category="error")
        else:
            if 'url' in request.files:
                blog_file = request.files.get('url')
                if blog_file and blog_file.filename != '':
                    if allowed_file(blog_file.filename):
                        folder_path = os.path.realpath(
                            os.path.dirname(__file__))
                        replaced_string = folder_path.replace("\\", "/")
                        os.remove(replaced_string + blog.stored_url)
                        filename = "user_" + str(current_user.id) + "_blogs_" + str(
                            blog.id) + "_" + secure_filename(blog_file.filename)
                        blog_file.save(os.path.join(
                            view.root_path, 'static/blogs/', filename))
                        input_url = "/static/blogs/" + filename
                        blog.stored_url = input_url
                        blog.stored_title = input_title
                        blog.stored_caption = input_caption
                        blog.stored_timestamp = datetime.datetime.now(
                            pytz.timezone('Asia/Kolkata'))
                        db.session.commit()
                        flash('Blog edited successfully', category="success")
                    else:
                        flash('Image should be in jpg, jpeg or png format',
                              category="error")

            return redirect('/user/' + str(current_user.id) + '/blogs')


# blogs - considering we can see any blog irrespective of whether we are following the blog author or not
@view.route('/user/<int:user_id>/blogs')
@login_required
def blogs(user_id):
    user = User.query.filter(User.id == user_id).first()

    if not user:
        flash(f'No user with user id {user_id} exists!', category='error')
        return redirect(url_for('home_views.profile'))

    current_user_all_following_ids = current_user_following_ids()
    if user_id not in current_user_all_following_ids and user_id != current_user.id:
        flash(
            f'You are not allowed to see {user.stored_username} blogs', category="error")
        return redirect('/profile')
    blog = user.stored_blogs.order_by(Blog.stored_timestamp.desc())

    return render_template('user_blogs.html', user=current_user, blogs=blog, other_user=user)


@view.route("/blogs/<int:blog_id>/create-comment", methods=['POST'])
@login_required
def create_comment(blog_id):
    blog = Blog.query.filter_by(id=blog_id).first()
    if not blog:
        flash(f'There is no blog with blog id {blog_id}', category="error")
    else:
        input_text = request.form.get('text')
        if not input_text:
            flash('Comment cannot be empty', category="error")
        else:
            new_comment = Comment(stored_text=input_text, author=current_user.id, blog_id=blog_id,
                                  stored_timestamp=datetime.datetime.now(pytz.timezone('Asia/Kolkata')))
            flash('Comment successfully created', category="success")
            db.session.add(new_comment)
            db.session.commit()
    
    return redirect(request.referrer)


@view.route("delete-comment/<int:comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter(Comment.id == comment_id).first()

    if not comment:
        flash(f'No comment exist with id {comment_id}', category="error")
    elif current_user.id != comment.blog.author and current_user.id != comment.author:
        flash('You don\'t have permission to delete the comment', category="error")
    else:
        flash('Comment successfully deleted', category="success")
        db.session.delete(comment)
        db.session.commit()
    return redirect(request.referrer)

# Like a blog - considering we can any like any blog irrespective of whether we are following the blog author or not


@view.route("/like-blog/<blog_id>", methods=['GET'])
@login_required
def like(blog_id):
    blog = Blog.query.filter(Blog.id == blog_id).first()
    like = Like.query.filter_by(
        author=current_user.id, blog_id=blog_id).first()

    if not blog:
        flash('Blog does not exist!', category="error")
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, blog_id=blog_id)
        db.session.add(like)
        db.session.commit()
    return redirect(request.referrer)


# Getting any user profile view with some conditions
@view.route("/user/<int:user_id>", methods=['GET'])
@login_required
def other_user(user_id):
    get_user = User.query.filter_by(id=user_id).first()
    if not get_user:
        flash(f'User with user id {user_id} does not exist!', category="error")
        return redirect('/profile')
    elif user_id == current_user.id:
        return redirect('/profile')
    else:
        current_user_all_following_ids = current_user_following_ids()
        return render_template('user_view.html', other_user=get_user, user=current_user, following_ids=current_user_all_following_ids)


# Follow and unfollow to any user
@view.route("/user/<int:user_id>/follow", methods=['GET'])
@login_required
def follow(user_id):
    user = User.query.filter_by(id=user_id).first()
    is_following = current_user.stored_following.filter_by(
        stored_following_id=user_id).first()
    if not user:
        flash(f'User with user id {user_id} does not exist!', category="error")
    elif user_id == current_user.id:
        flash('Invalid request', category="error")
    elif is_following:
        db.session.delete(is_following)
        db.session.commit()
    else:
        new_follow = Follow(stored_follower_id=current_user.id,
                            stored_following_id=user.id)
        db.session.add(new_follow)
        db.session.commit()
    return redirect(url_for('.other_user', user_id=user_id))


@view.route("/user/<int:user_id>/followers")
@login_required
def followers(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        flash(f'User with user id {user_id} does not exist!', category="error")
        return redirect('/profile')
    user_stored_followers = user.stored_followers
    followers_details = []
    for follower in user_stored_followers:
        followers_details = followers_details + \
            [User.query.filter(follower.stored_follower_id == User.id).first()]

    current_user_all_following_ids = current_user_following_ids()
    if user_id not in current_user_all_following_ids and user_id != current_user.id:
        flash(
            f'You are not allowed to see {user.stored_username} followers', category="error")
        return redirect('/profile')
    return render_template('user_followers.html', user=current_user, other_user=user, all_followers=followers_details, following_ids=current_user_all_following_ids)


@view.route("/user/<int:user_id>/following")
@login_required
def following(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        flash(f'User with user_id {user_id} does not exist!', category="error")
        return redirect('/profile')
    user_stored_following = user.stored_following
    following_details = []
    for following in user_stored_following:
        following_details = following_details + \
            [User.query.filter(
                following.stored_following_id == User.id).first()]

    current_user_all_following_ids = current_user_following_ids()
    if user_id not in current_user_all_following_ids and user_id != current_user.id:
        flash(
            f'You are not allowed to see {user.stored_username} following', category="error")
        return redirect('/profile')
    return render_template('user_following.html', user=current_user, other_user=user, all_following=following_details, following_ids=current_user_all_following_ids)


@view.route("/search", methods=['POST'])
@login_required
def search():
    to_search = request.form.get("keywords")
    if not to_search:
        flash('Search can\'t be empty', category="error")
    searched_user = User.query.filter(
        User.stored_username.like('%' + to_search + '%'))

    return render_template('search.html', user=current_user, to_search=to_search, users_results=searched_user)


@view.route("/edit-profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == "GET":
        return render_template('edit_profile.html', user=current_user)
    else:
        full_name = request.form.get('name')
        my_bio = request.form.get('bio')
        if 'picture' in request.files:
            file = request.files['picture']
            if file:
                if file.filename != '':
                    if allowed_file(file.filename):
                        if "user_0" not in current_user.stored_profile_photo:
                            folder_path = os.path.realpath(
                                os.path.dirname(__file__))
                            replaced_string = folder_path.replace("\\", "/")
                            os.remove(replaced_string +
                                      current_user.stored_profile_photo)
                        filename = "user_" + \
                            str(current_user.id) + "_" + \
                            secure_filename(file.filename)
                        file.save(os.path.join(view.root_path,
                                  'static/profile_photos/', filename))
                        current_user.stored_profile_photo = "/static/profile_photos/" + filename
                        db.session.commit()
                    else:
                        flash('Image should be in jpg, jpeg or png format',
                              category="error")
        if full_name:
            current_user.stored_name = full_name
            db.session.commit()
        if my_bio:
            current_user.stored_bio = my_bio
            db.session.commit()
        return redirect('/profile')
