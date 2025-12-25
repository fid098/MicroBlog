from datetime import datetime, timezone
from flask import render_template, flash, redirect, url_for, request, g, \
    current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
import sqlalchemy as sa
from langdetect import detect, LangDetectException
from app import db
from app.main.forms import EditProfileForm, EmptyForm, PostForm
from app.models import User, Post
from app.translate import translate
from app.main import bp
from flask import jsonify

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        #this function is executed before every request, if the user is authenticated
        #it updates the last_seen field of the current_user to the current UTC time
    g.locale = str(get_locale())
    #this sets the locale for the current request using the get_locale() function defined in app
    #the locale is stored in the g object, which is a global namespace for holding data during a request


#this is a view function(handlers for the application routes)
@bp.route('/', methods=['GET', 'POST'])  #this is a decorator that modifies the function that follows it
@bp.route('/index', methods=['GET', 'POST'])  #this binds the URL /index to the index() function
#i accept POST requests since the view function will now recieve form data
@login_required
#this decorator ensures that only authenticated (logged-in) users can access this route
def index():
#the route() decorator in flask is used to bind a function to a URL
#when a user accesses the root URL or /index, the index() function is called and "Hello, world" is returned as the response
#the app.route() decorator takes the URL pattern as an argument and associates it with the index() function
    form = PostForm()
    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
            #this uses the detect() function from langdetect to determine the language of the post content
        except LangDetectException:
            language = ''
            #if language detection fails, set language to an empty string
            #this inserts a new Post record into the database
        post = Post(body=form.post.data, author=current_user, language=language)
        #takes the data entered into the text area box in the post form and the author(current user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('main.index'))
        #this allows the user to refresh the page after a submission
    #posts = db.session.scalars(current_user.following_posts()).all()
    #this queries the database for all the post of the users that the current user follows 
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(current_user.following_posts(), page=page,
                        per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    
    next_url=None
    prev_url=None
    if posts.has_next:
        next_url = url_for('main.index', page=posts.next_num)
    else:
        None
    if posts.has_prev:
        prev_url = url_for('main.index', page=posts.prev_num)
    else:
        None
    return render_template('index.html', title=_('Home'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url) #the template now recieves the form object as an additional argument, so it can render it to the page 
#this converts a template file (index.html) into a complete HTML page
#the render_template() function takes the name of the template file as its first argument
#additional arguments are key-value pairs that are passed to the template engine
#these key-value pairs can be used within the template to dynamically generate content

    
@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required 
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        #this updates the current user's username and about_me fields with the data from the form
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        #this populates the form fields with the current user's data when the form is first loaded
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'), form=form)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username)
        )
        if user is None:
            flash(_('User %(username)s not found', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot follow yourself'))
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))

@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %(username)s.', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))

@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())   
    #posts = db.session.scalars(query).all()
    posts = db.paginate(query, page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    #error_out flag: if true when an out of range page is requested a 404 error will be automatically returned to the client.
    #error_out flag: if false, an empty list will be returned for out of range pages
    #items contains the list of items in the requested page.

    next_url=None
    prev_url=None
    
    if posts.has_next:
        next_url = url_for('main.explore', page=posts.next_num)
    else:
        None
    if posts.has_prev:
        prev_url = url_for('main.explore', page=posts.prev_num)
    else:
        None
    return render_template('index.html', title=_('Explore'), next_url=next_url, prev_url=prev_url, posts=posts.items)
    #i reuse the index template but do not include the form argument since i dont want the form to write blog posts


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    data = request.get_json()
    #this gets the JSON data sent in the POST request like the text to be translated, source language, and destination language
    #it returns a dictionary with data that the client has submitted
    return jsonify({
        'text': translate(data['text'], data['source_language'], data['dest_language'])
    })
    #this calls the translate() function from app/translate.py to perform the translation


@bp.route('/user/<username>')
#decorator to define a route with a dynamic segment <username> which captures the username from the URL
@login_required 
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    #db.first_or_404 queries the database for a User with the given username
    #if no such user exists, it returns a 404 error
    page = request.args.get('page', 1, type=int)
    query = user.posts.select().order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    prev_url=None
    next_url=None
    
    if posts.has_next:
        next_url = url_for('main.user', username=user.username, page=posts.next_num)
    else:
        None
    if posts.has_prev:
        prev_url = url_for('main.user', username=user.username, page=posts.prev_num)
    else:
        None
    #this route displays the profile page for a user with the given username
    form = EmptyForm()
    return render_template('user.html',form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url, user=user)
