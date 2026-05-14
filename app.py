from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


from models import db, User, Post, Comment
from forms import RegisterForm, LoginForm, PostForm, EditProfileForm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret123'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///social.db'

app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)

login_manager = LoginManager()

login_manager.login_view = 'login'

login_manager.init_app(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_picture(file):

    if not allowed_file(file.filename):
        return None

    filename = secure_filename(file.filename)

    path = os.path.join(
        app.config['UPLOAD_FOLDER'],
        filename
    )

    file.save(path)

    return filename


@login_manager.user_loader
def load_user(user_id):

    return db.session.get(User, int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():

    form = RegisterForm()

    if form.validate_on_submit():

        existing_user = User.query.filter_by(
            username=form.username.data
        ).first()

        if existing_user:
            flash('Username already exists')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(
            form.password.data
        )

        user = User(
            username=form.username.data,
            password=hashed_password
        )

        db.session.add(user)

        db.session.commit()

        flash('Registration successful')

        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            username=form.username.data
        ).first()

        if user and check_password_hash(
                user.password,
                form.password.data
        ):

            login_user(user)

            return redirect(url_for('index'))

        flash('Invalid username or password')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():

    form = PostForm()

    if form.validate_on_submit():

        image_file = None

        if form.image.data:
            image_file = save_picture(form.image.data)

        post = Post(
            content=form.content.data,
            image=image_file,
            user_id=current_user.id
        )

        db.session.add(post)

        db.session.commit()

        return redirect(url_for('index'))

    followed_users = current_user.followed.all()

    followed_ids = [user.id for user in followed_users]

    followed_ids.append(current_user.id)

    posts = Post.query.filter(
        Post.user_id.in_(followed_ids)
    ).order_by(Post.id.desc()).all()

    return render_template(
        'index.html',
        form=form,
        posts=posts
    )


@app.route('/profile/<username>')
@login_required
def profile(username):

    user = User.query.filter_by(
        username=username
    ).first_or_404()

    return render_template(
        'profile.html',
        user=user
    )


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():

    form = EditProfileForm()

    if form.validate_on_submit():

        current_user.bio = form.bio.data

        if form.profile_pic.data:

            pic = save_picture(form.profile_pic.data)

            if pic:
                current_user.profile_pic = pic

        db.session.commit()

        return redirect(
            url_for(
                'profile',
                username=current_user.username
            )
        )

    return render_template(
        'edit_profile.html',
        form=form
    )


@app.route('/follow/<int:user_id>')
@login_required
def follow(user_id):

    user = User.query.get_or_404(user_id)

    if user not in current_user.followed:
        current_user.followed.append(user)

        db.session.commit()

    return redirect(
        url_for(
            'profile',
            username=user.username
        )
    )


@app.route('/unfollow/<int:user_id>')
@login_required
def unfollow(user_id):

    user = User.query.get_or_404(user_id)

    if user in current_user.followed:
        current_user.followed.remove(user)

        db.session.commit()

    return redirect(
        url_for(
            'profile',
            username=user.username
        )
    )


@app.route('/like/<int:post_id>')
@login_required
def like(post_id):

    post = Post.query.get_or_404(post_id)

    if current_user not in post.liked_by:

        post.liked_by.append(current_user)

        db.session.commit()

    return redirect(url_for('index'))


@app.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def comment(post_id):

    text = request.form.get('text')

    if text:

        comment = Comment(
            text=text,
            user_id=current_user.id,
            post_id=post_id
        )

        db.session.add(comment)

        db.session.commit()

    return redirect(url_for('index'))


import os

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 2000))

    app.run(host="0.0.0.0", port=port, debug=True)