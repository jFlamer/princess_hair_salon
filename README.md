# Princess Hair Salon App

This is a web-based appointment and management system for a princess-themed hair salon, built with **Python**, **Flask**, **SQLite**, and **SQLAlchemy**. The application allows users to manage princesses, hairstyles, and their associated appointments. It also fetches dynamic data (movie details) from the **OMDb API**.

---

## 🫧 Features

### Functional Coverage:

- **Entity Management**:
  - Princesses
  - Hairstyles
  - Appointments

- **CRUD Operations**:
  - Add, Edit, Delete for all entities

- **Database Usage**:
  - SQLite (via SQLAlchemy ORM)

- **Data Types Used**:
  - `String`: Names, movie titles
  - `Date`: Appointment times, release dates
  - `Boolean`: Is the movie animated?
  - `Number`: Prices, durations, ratings

- **Unique Identifier**:
  - All entities use auto-incrementing integer primary keys (`id`)

- **External Data Integration**:
  - OMDb API is used to fetch and store:
    - Movie release dates
    - Ratings
    - Genres
    - Poster URLs

- **Search**:
  - Search princesses by name

- **Sorting**:
  - Sort princesses by any field (default: ID)

- **Pagination**:
  - Pagination for princesses, hairstyles, and appointments

---

## 🫐 Additional Cool Features

- **Dynamic Poster Fetching**:
  - Princess movie posters are pulled and displayed via OMDb

- **Movie Ratings Display**:
  - IMDb ratings and genre breakdowns shown on homepage

- **Clean, Simple UI**:
  - HTML + CSS interface with consistent layout

---

## ⚙️ Setup Instructions
## Prerequisites
- Python 3.7+
- Pip
- (Optional) conda

### 1. Clone the repository
```bash
git clone https://github.com/jFlamer/princess_hair_salon.git
cd princess-hairsalon
```

### 2. Create and activate virtual environment suing conda (recommended)
```bash
conda create -n myenv
conda activate myenv
```

### 3. Install dependencies
```bash
pip install Flask
pip install Flask-SQLAlchemy
pip install requests
```

### 4. Run the application
```bash
python app.py
```
or using flask:
```bash
flask run
```

Visit `http://127.0.0.1:5000` in your browser.

---

## 🌐 Technologies Used
- Python 3
- Flask
- SQLAlchemy (SQLite backend)
- HTML / CSS
- OMDb API

---

## License
MIT License

---

## ✨ Maintainer ✨
**Jagoda Flejmer**  
[GitHub Profile](https://github.com/jFlamer)

