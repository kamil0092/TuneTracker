from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

##CREATE DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///songs.db"
# Create the extension
db = SQLAlchemy()
# initialise the app with the extension
db.init_app(app)


##CREATE TABLE Model
class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    songs = db.relationship('Song', backref='artist', lazy=True)


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)


# Create table schema in the database. Requires application context.
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    ##READ ALL RECORDS
    result = db.session.execute(db.select(Song).order_by(Song.title))
    all_songs = result.scalars()

    return render_template("index.html", songs=all_songs)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        # Create Artist
        new_artist = Artist(name=request.form["name"])
        db.session.add(new_artist)
        db.session.commit()

        # Create Song and associate it with the created Artist
        new_song = Song(title=request.form["title"], artist=new_artist)
        db.session.add(new_song)
        db.session.commit()

        return redirect(url_for('home'))
    return render_template("add.html")


@app.route('/song/<int:song_id>')
def song_details(song_id):
    song = Song.query.get(song_id)
    return render_template('details.html', song=song)


@app.route('/home', methods=['GET'])
def return_home():
    return redirect(url_for('home'))


@app.route('/delete')
def delete_song():
    song_id = request.args.get('song_id')
    song_to_delete = db.get_or_404(Song, song_id)
    db.session.delete(song_to_delete)
    db.session.commit()

    artist_id = request.args.get('artist_id')
    artist_to_delete = db.get_or_404(Artist, artist_id)
    db.session.delete(artist_to_delete)
    db.session.commit()

    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
