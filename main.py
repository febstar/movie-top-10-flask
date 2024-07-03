from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, InputRequired, NumberRange
import requests
from database import db, Movie
from dotenv import load_dotenv
import os

load_dotenv()

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

MOVIE_DB_API_KEY = os.getenv('API_KEY')
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


class Form1(FlaskForm):
    rating = StringField(label='new rating', validators=[InputRequired()])
    review = StringField(label='new review', validators=[InputRequired()])
    rank = StringField(label="Rank out of 10", validators=[InputRequired()])
    submit = SubmitField(label='Update')


class Form2(FlaskForm):
    title = StringField(label='Movie Title', validators=[InputRequired()])
    submit = SubmitField(label='Add Movie')


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
db.init_app(app)

with app.app_context():
    db.create_all()

Bootstrap5(app)

# CREATE DB


# CREATE TABLE


@app.route("/")
def home():
    result = db.session.execute(db.select(Movie).order_by(Movie.title))
    movies = list(result.scalars())

    sorted_movies_by_ranking = sorted(movies, key=lambda movie: movie.ranking,reverse=True)
    # rankings = [movie.ranking for movie in sorted_movies_by_ranking]
    # print(sorted_movies_by_ranking)

    return render_template("index.html", movie=sorted_movies_by_ranking)


# @app.route('/add')
# def add():
#     form = Form2()
#     form.validate_on_submit()
#     return render_template("add.html", form=form)



@app.route('/edit/<int:id>', methods=["GET", "POST"])
def edit(id):
    form = Form1()
    form.validate_on_submit()
    movie = db.get_or_404(Movie, id)
    if form.validate_on_submit():
        new_rating = form.rating.data
        new_review = form.review.data
        new_rank = form.rank.data
        movie_to_update = db.session.execute(db.select(Movie).where(Movie.id == id)).scalar()
        movie_to_update.rating = new_rating
        movie_to_update.review = new_review
        movie_to_update.ranking = new_rank
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', movie=movie, form=form)


@app.route('/delete/<int:id>')
def delete(id):
    movie_to_delete = db.get_or_404(Movie, id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=["GET", "POST"])
def add():
    form = Form2()
    if form.validate_on_submit():
        movie_title = form.title.data

        response = requests.get(url=MOVIE_DB_SEARCH_URL, params={"api_key": MOVIE_DB_API_KEY, "query": movie_title})
        data = response.json()["results"]
        print(data)
        return render_template("select.html", options=data)
    return render_template("add.html", form=form)




@app.route("/find")
def find():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"
        response = requests.get(url=movie_api_url, params={"api_key": MOVIE_DB_API_KEY, "language": "en-US"})
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            year=data["release_date"].split("-")[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()

        return redirect(url_for("edit", id=new_movie.id))




if __name__ == '__main__':
    app.run(debug=True)
