from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from models import db, Princess, Hairstyle, Appointment
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'dev'
db.init_app(app)

API_KEY = 'your_openweathermap_api_key'
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

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

    # Paginate appointments and hairstyles
    appointment_pagination = Appointment.query.paginate(page=page, per_page=10)
    hairstyle_pagination = Hairstyle.query.paginate(page=page, per_page=10)

    return render_template('index.html',
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
    princess_pagination = query.paginate(page=page, per_page=10)

    return render_template('princesses.html', princesses=princess_pagination.items, pagination=princess_pagination)


@app.route('/hairstyles', methods=['GET'])
def hairstyles():
    page = request.args.get('page', 1, type=int)
    hairstyle_pagination = Hairstyle.query.paginate(page=page, per_page=10)

    return render_template('hairstyles.html', hairstyles=hairstyle_pagination.items, pagination=hairstyle_pagination)


@app.route('/appointments', methods=['GET'])
def appointments():
    page = request.args.get('page', 1, type=int)
    appointment_pagination = Appointment.query.paginate(page=page, per_page=10)

    return render_template('appointments.html', appointments=appointment_pagination.items, pagination=appointment_pagination)


@app.route('/add_princess', methods=['GET', 'POST'])
def add_princess():
    if request.method == 'POST':
        try:
            name = request.form['name']
            movie = request.form['movie']
            release_date = datetime.strptime(request.form['release_date'], "%Y-%m-%d")
            is_animated = request.form.get('is_animated') == 'on'
            rating = float(request.form['rating'])

            new_princess = Princess(
                name=name,
                movie=movie,
                release_date=release_date,
                is_animated=is_animated,
                rating=rating
            )

            db.session.add(new_princess)
            db.session.commit()
            return redirect(url_for('princesses'))
        except Exception as e:
            # This will print the error to your terminal
            print("ERROR:", e)
            return f"<h3>Something went wrong: {e}</h3>", 500

    return render_template('add_princess.html')



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
        new_appointment = Appointment(princess_id=princess_id, hairstyle_id=hairstyle_id, appointment_time=appointment_time)
        db.session.add(new_appointment)
        db.session.commit()
        return redirect(url_for('appointments'))
    return render_template('add_appointment.html', princesses=princesses, hairstyles=hairstyles)


@app.route('/complete_appointment/<int:id>')
def complete_appointment(id):
    appointment = Appointment.query.get(id)
    appointment.completed = True  # Use 'completed' instead of 'status'
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete_appointment/<int:id>')
def delete_appointment(id):
    appointment = Appointment.query.get(id)
    db.session.delete(appointment)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/weather', methods=['GET', 'POST'])
def weather():
    city = request.args.get('city', 'London')  # Default city is London
    if request.method == 'POST':
        city = request.form['city']

    # Fetch weather data from OpenWeatherMap API
    try:
        response = requests.get(f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric")
        data = response.json()

        # Check if the response contains valid data
        if data.get("cod") != 200:
            return render_template('weather.html', error="City not found or invalid API key.")

        # Parse weather data
        weather = {
            'city': data['name'],
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
        }
        return render_template('weather.html', weather=weather)

    except Exception as e:
        return render_template('weather.html', error="Failed to retrieve weather data.")


if __name__ == '__main__':
    app.run(debug=True)
