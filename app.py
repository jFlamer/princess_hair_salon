from datetime import datetime
from urllib.parse import quote

from flask import Flask, render_template, request, redirect, url_for
from models import db, Princess, Hairstyle, Appointment
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'dev'
db.init_app(app)


OMDB_API_KEY = 'ea3ffd44'
OMDB_BASE_URL = 'http://www.omdbapi.com/'

# Create all tables within the context of the app
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    search = request.args.get('search', '')
    sort_by = request.args.get('sort', 'id')
    page = request.args.get('page', 1, type=int)

    # Querying princesses with pagination
    query = Princess.query
    if search:
        query = query.filter(Princess.name.contains(search))
    query = query.order_by(getattr(Princess, sort_by))

    princess_pagination = query.paginate(page=page, per_page=10)
    appointment_pagination = Appointment.query.paginate(page=page, per_page=10)
    hairstyle_pagination = Hairstyle.query.paginate(page=page, per_page=10)
    #
    # return render_template('index.html',
    #                        pagination=princess_pagination,
    #                        princesses=princess_pagination.items,
    #                        appointments=appointment_pagination.items,
    #                        hairstyles=hairstyle_pagination.items)

    movies = db.session.query(Princess.movie).distinct().all()
    titles = list(set([title.strip() for (title,) in movies if title]))

    ratings = [get_movie_rating(title) for title in titles]

    return render_template('index.html',
                           movie_ratings=ratings,
                           pagination=princess_pagination,
                           princesses=princess_pagination.items,
                           appointments=appointment_pagination.items,
                           hairstyles=hairstyle_pagination.items)


@app.route('/princesses', methods=['GET'])
def princesses():
    search = request.args.get('search', '')
    sort_by = request.args.get('sort', 'id')  # Default sort by 'id'
    page = request.args.get('page', 1, type=int)

    # Querying princesses with pagination and sorting
    query = Princess.query
    if search:
        query = query.filter(Princess.name.contains(search))

    # Sorting logic
    query = query.order_by(getattr(Princess, sort_by))

    # Paginate the results
    princess_pagination = query.paginate(page=page, per_page=7)

    return render_template('princesses.html', princesses=princess_pagination.items, pagination=princess_pagination)


@app.route('/hairstyles', methods=['GET'])
def hairstyles():
    page = request.args.get('page', 1, type=int)
    hairstyle_pagination = Hairstyle.query.paginate(page=page, per_page=7)

    return render_template('hairstyles.html', hairstyles=hairstyle_pagination.items, pagination=hairstyle_pagination)


@app.route('/appointments', methods=['GET'])
def appointments():
    page = request.args.get('page', 1, type=int)
    appointment_pagination = Appointment.query.paginate(page=page, per_page=7)

    return render_template('appointments.html', appointments=appointment_pagination.items,
                           pagination=appointment_pagination)


@app.route('/add_princess', methods=['GET', 'POST'])
def add_princess():
    poster = None
    genre = None
    rating = None
    if request.method == 'POST':
        try:
            name = request.form['name']
            movie = request.form['movie']
            # release_date = datetime.strptime(request.form['release_date'], "%Y-%m-%d")
            is_animated = request.form.get('is_animated') == 'on'
            # rating = float(request.form['rating'])

            # fetching rest of the data
            movie_encoded = movie.replace(" ", "+")
            response = requests.get(f"{OMDB_BASE_URL}?t={movie_encoded}&apikey={OMDB_API_KEY}")
            # response = requests.get(f"{OMDB_BASE_URL}?t={movie}")
            data = response.json()
            print(f"Requesting: {OMDB_BASE_URL}?t={movie.lower()}&apikey={OMDB_API_KEY}")

            if data.get('Response') == 'True':
                try:
                    # Try parsing the release date
                    release_date_str = data.get('Released', 'Unknown')
                    if release_date_str != 'Unknown':
                        release_date = datetime.strptime(release_date_str, "%d %b %Y")
                    else:
                        release_date = None  # Set to None if no valid date
                except ValueError:
                    release_date = None  # Set to None if parsing fails

                rating = data.get('imdbRating', 'N/A')
            else:
                print(movie_encoded)
                release_date = None
                rating = None

            # print(movie)
            # print(f"Release Date: {release_date}")
            # print(f"Rating: {rating}")

            genre = data.get('Genre')
            poster = data.get('Poster')

            new_princess = Princess(
                name=name,
                movie=movie,
                release_date=release_date,
                is_animated=request.form.get('is_animated') == 'on',
                rating=rating,
                poster_url = poster,
                genre=genre,
            )

            db.session.add(new_princess)
            db.session.commit()
            return redirect(url_for('princesses'))
        except Exception as e:
            # This will print the error to your terminal
            print("ERROR:", e)
            return f"<h3>Something went wrong: {e}</h3>", 500

    return render_template('add_princess.html', poster=poster, genre=genre, rating=rating)


@app.route('/add_hairstyle', methods=['GET', 'POST'])
def add_hairstyle():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        duration = int(request.form['duration'])
        price = float(request.form['price'])
        new_hairstyle = Hairstyle(name=name, description=description, duration=duration, price=price)
        db.session.add(new_hairstyle)
        db.session.commit()
        return redirect(url_for('hairstyles'))
    return render_template('add_hairstyle.html')


@app.route('/add_appointment', methods=['GET', 'POST'])
def add_appointment():
    princesses = Princess.query.all()
    hairstyles = Hairstyle.query.all()
    if request.method == 'POST':
        princess_id = int(request.form['princess_id'])
        hairstyle_id = int(request.form['hairstyle_id'])
        appointment_time = datetime.strptime(request.form['appointment_time'], "%Y-%m-%dT%H:%M")
        new_appointment = Appointment(princess_id=princess_id, hairstyle_id=hairstyle_id,
                                      appointment_time=appointment_time)
        db.session.add(new_appointment)
        db.session.commit()
        return redirect(url_for('appointments'))
    return render_template('add_appointment.html', princesses=princesses, hairstyles=hairstyles)


@app.route('/complete_appointment/<int:id>')
def complete_appointment(id):
    appointment = Appointment.query.get(id)
    appointment.completed = True  # Use 'completed' instead of 'status'
    db.session.commit()
    return redirect(url_for('appointments'))


@app.route('/delete_appointment/<int:id>')
def delete_appointment(id):
    appointment = Appointment.query.get(id)
    db.session.delete(appointment)
    db.session.commit()
    return redirect(url_for('appointments'))


@app.route('/delete_princess/<int:id>')
def delete_princess(id):
    princess = Princess.query.get(id)
    db.session.delete(princess)
    db.session.commit()
    return redirect(url_for('princesses'))


@app.route('/delete_hairstyle/<int:id>')
def delete_hairstyle(id):
    hairstyle = Hairstyle.query.get(id)
    db.session.delete(hairstyle)
    db.session.commit()
    return redirect(url_for('hairstyles'))


@app.route('/edit_princess/<int:id>', methods=['GET', 'POST'])
def edit_princess(id):
    princess = Princess.query.get_or_404(id)
    if request.method == 'POST':
        princess.name = request.form['name']
        princess.movie = request.form['movie']
        princess.is_animated = request.form.get('is_animated') == 'on'

        movie = princess.movie
        movie_encoded = movie.replace(" ", "+")
        response = requests.get(f"{OMDB_BASE_URL}?t={movie_encoded}&apikey={OMDB_API_KEY}")
        data = response.json()

        if data.get("Response") == "True":
            try:
                release_date_str = data.get('Released', 'Unknown')
                if release_date_str != "Unknown":
                    release_date = datetime.strptime(release_date_str, "%d %b %Y")
                else:
                    release_date = None
            except ValueError:
                release_date = None
            rating = data.get('imdbRating', 'N/A')
            poster = data.get('Poster')
            genre = data.get('Genre')
        else:
            release_date = None
            rating = None
            poster = None
            genre = None

        princess.release_date = release_date
        princess.poster = poster
        princess.rating = rating
        princess.genre = genre

        db.session.commit()
        return redirect(url_for('princesses'))
    return render_template('edit_princess.html', princess=princess)

@app.route('/edit_hairstyle/<int:id>', methods=['GET', 'POST'])
def edit_hairstyle(id):
    hairstyle = Hairstyle.query.get_or_404(id)
    if request.method == 'POST':
        hairstyle.name = request.form['name']
        hairstyle.description = request.form['description']
        hairstyle.duration = int(request.form['duration'])
        hairstyle.price = float(request.form['price'])

        db.session.commit()
        return redirect(url_for('hairstyles'))
    return render_template('edit_hairstyle.html', hairstyle=hairstyle)


@app.route('/edit_appointment/<int:id>', methods=['GET', 'POST'])
def edit_appointment(id):
    appointment = Appointment.query.get(id)
    princesses = Princess.query.all()
    hairstyles = Hairstyle.query.all()
    if request.method == 'POST':
        appointment.princess_id = int(request.form['princess_id'])
        appointment.hairstyle_id = int(request.form['hairstyle_id'])
        appointment_time_str = request.form['appointment_time']
        appointment.appointment_time = datetime.strptime(appointment_time_str, "%Y-%m-%dT%H:%M")

        db.session.commit()
        return redirect(url_for('appointments'))
    return render_template('edit_appointment.html', princesses=princesses, hairstyles=hairstyles, appointment=appointment)
def get_movie_rating(title):
    try:
        response = requests.get(f"{OMDB_BASE_URL}?t={title}&apikey={OMDB_API_KEY}")
        data = response.json()
        if data.get('Response') == 'True':
            return {
                'title': data.get('Title', title),
                'rating': data.get('imdbRating', 'N/A'),
                'poster': data.get('Poster', ''),
                'year': data.get('Year', ''),
                'genre': data.get('Genre', 'N/A')
            }
    except Exception as e:
        print("OMDb error: ", e)
    return None


if __name__ == '__main__':
    app.run(debug=True)
