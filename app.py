from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_very_secret_key'  # Змініть на свій ключ
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Models

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    tracklist = db.Column(db.Text, nullable=False)  # Список пісень через кому
    image_url = db.Column(db.String(200))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/')
def index():
    albums = Album.query.all()
    return render_template('index.html', albums=albums)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/history')
def history():
    return render_template('history.html')


@app.route('/album/<int:album_id>')
def view_album(album_id):
    album = Album.query.get_or_404(album_id)
    tracks = album.tracklist.split('\n')  # Розбиваємо текст на список
    return render_template('album.html', album=album, tracks=tracks)




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Невірний логін або пароль')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))



@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add_album():
    if request.method == 'POST':
        new_album = Album(
            title=request.form.get('title'),
            year=request.form.get('year'),
            description=request.form.get('description'),
            tracklist=request.form.get('tracklist'),
            image_url=request.form.get('image_url')
        )
        db.session.add(new_album)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_edit_album.html', action='Додати')


@app.route('/admin/edit/<int:album_id>', methods=['GET', 'POST'])
@login_required
def edit_album(album_id):
    album = Album.query.get_or_404(album_id)
    if request.method == 'POST':
        album.title = request.form.get('title')
        album.year = request.form.get('year')
        album.description = request.form.get('description')
        album.tracklist = request.form.get('tracklist')
        album.image_url = request.form.get('image_url')
        db.session.commit()
        return redirect(url_for('view_album', album_id=album.id))
    return render_template('create_edit_album.html', album=album, action='Редагувати')


@app.route('/admin/delete/<int:album_id>')
@login_required
def delete_album(album_id):
    album = Album.query.get_or_404(album_id)
    db.session.delete(album)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username='admin').first():
            hashed_pw = generate_password_hash('admin123')
            admin = User(username='admin', password_hash=hashed_pw)
            db.session.add(admin)
            db.session.commit()
            print("Створено користувача 'admin' з паролем 'admin123'")

    app.run(debug=True)