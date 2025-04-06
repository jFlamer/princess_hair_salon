from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from models import db, Princess, Hairstyle, Appointment
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'dev'
db.init_app(app)

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


@app.route('/add_princess', methods=['GET', 'POST'])
def add_princess():
    if request.method == 'POST':
        name = request.form['name']
        movie = request.form['movie']
        release_date = datetime.strptime(request.form['release_date'], "%Y-%m-%d")
        is_animated = request.form['is_animated']
        rating = request.form['rating']
        new_princess = Princess(name=name, movie=movie, release_date=release_date, is_animated=is_animated,
                                rating=rating)
        db.session.add(new_princess)
        db.session.commit()
        return redirect(url_for('index'))
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
        return redirect(url_for('index'))
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
        return redirect(url_for('index'))
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


if __name__ == '__main__':
    app.run(debug=True)
