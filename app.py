from __future__ import annotations
import os
import sqlite3
from datetime import date
from pathlib import Path
from flask import Flask, abort, flash, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB = BASE_DIR / "vacancies.db"
DB_PATH = Path(os.environ.get("DB_PATH", str(DEFAULT_DB)))
REQUIRED_TABLES = {"Users", "Companies", "Vacancies", "Skills", "User_Skills", "Vacancy_Skills", "Applications"}

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "careerhub-demo-change-this-key")


def get_db():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"SQLite деректер базасы табылмады: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def check_database():
    with get_db() as conn:
        names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        missing = REQUIRED_TABLES - names
        if missing:
            raise RuntimeError("Деректер базасында кестелер жетіспейді: " + ", ".join(sorted(missing)))


def get_stats():
    with get_db() as conn:
        return {
            "vacancies": conn.execute("SELECT COUNT(*) FROM Vacancies").fetchone()[0],
            "companies": conn.execute("SELECT COUNT(*) FROM Companies").fetchone()[0],
            "users": conn.execute("SELECT COUNT(*) FROM Users").fetchone()[0],
            "applications": conn.execute("SELECT COUNT(*) FROM Applications").fetchone()[0],
        }


def vacancy_query(search="", city="", min_salary="", max_experience=""):
    sql = """
        SELECT v.vacancy_id, v.title, v.description, v.city, v.salary,
               v.experience_years, c.company_name, c.industry,
               GROUP_CONCAT(DISTINCT s.skill_name) AS skills
        FROM Vacancies v
        LEFT JOIN Companies c ON c.company_id = v.company_id
        LEFT JOIN Vacancy_Skills vs ON vs.vacancy_id = v.vacancy_id
        LEFT JOIN Skills s ON s.skill_id = vs.skill_id
        WHERE 1=1
    """
    params = []
    if search:
        sql += " AND (v.title LIKE ? OR c.company_name LIKE ? OR v.description LIKE ?)"
        params.extend([f"%{search}%"] * 3)
    if city:
        sql += " AND v.city = ?"
        params.append(city)
    if min_salary:
        try:
            salary_value = float(min_salary)
            if salary_value < 0: raise ValueError
        except ValueError:
            raise ValueError("Ең төменгі жалақыны дұрыс санмен енгізіңіз.")
        sql += " AND v.salary >= ?"
        params.append(salary_value)
    if max_experience:
        try:
            exp_value = int(max_experience)
            if exp_value < 0: raise ValueError
        except ValueError:
            raise ValueError("Тәжірибені нөлден кем емес бүтін санмен енгізіңіз.")
        sql += " AND v.experience_years <= ?"
        params.append(exp_value)
    sql += " GROUP BY v.vacancy_id ORDER BY v.salary DESC, v.title"
    with get_db() as conn:
        rows = conn.execute(sql, params).fetchall()
        cities = [r[0] for r in conn.execute("SELECT DISTINCT city FROM Vacancies WHERE city IS NOT NULL AND city <> '' ORDER BY city")]
    return rows, cities


@app.context_processor
def inject_globals():
    return {"site_name": "CareerHub", "stats": get_stats()}


@app.route("/")
def index():
    rows, _ = vacancy_query()
    return render_template("index.html", vacancies=rows[:6])


@app.route("/vacancies")
def vacancies():
    search = request.args.get("q", "").strip()
    city = request.args.get("city", "").strip()
    min_salary = request.args.get("salary", "").strip()
    max_experience = request.args.get("experience", "").strip()
    try:
        rows, cities = vacancy_query(search, city, min_salary, max_experience)
        error = None
    except ValueError as exc:
        rows, cities, error = [], [], str(exc)
    return render_template("vacancies.html", vacancies=rows, cities=cities,
                           q=search, selected_city=city, salary=min_salary,
                           experience=max_experience, error=error)


@app.route("/vacancy/<int:vacancy_id>")
def vacancy_detail(vacancy_id):
    with get_db() as conn:
        row = conn.execute("""
            SELECT v.*, c.company_name, c.industry, c.email AS company_email,
                   GROUP_CONCAT(DISTINCT s.skill_name) AS skills
            FROM Vacancies v
            LEFT JOIN Companies c ON c.company_id = v.company_id
            LEFT JOIN Vacancy_Skills vs ON vs.vacancy_id = v.vacancy_id
            LEFT JOIN Skills s ON s.skill_id = vs.skill_id
            WHERE v.vacancy_id = ? GROUP BY v.vacancy_id
        """, (vacancy_id,)).fetchone()
    if row is None:
        abort(404)
    return render_template("vacancy_detail.html", vacancy=row)


@app.route("/apply/<int:vacancy_id>", methods=["POST"])
def apply(vacancy_id):
    name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    phone = request.form.get("phone", "").strip()
    city = request.form.get("city", "").strip()
    if not name or not email or "@" not in email or "." not in email.split("@")[-1]:
        flash("Аты-жөніңізді және дұрыс email мекенжайын енгізіңіз.", "error")
        return redirect(url_for("vacancy_detail", vacancy_id=vacancy_id) + "#apply")
    try:
        with get_db() as conn:
            vacancy = conn.execute("SELECT vacancy_id FROM Vacancies WHERE vacancy_id=?", (vacancy_id,)).fetchone()
            if not vacancy:
                abort(404)
            user = conn.execute("SELECT user_id FROM Users WHERE lower(email)=? ORDER BY user_id LIMIT 1", (email,)).fetchone()
            if user:
                user_id = user["user_id"]
            else:
                cur = conn.execute("""INSERT INTO Users (full_name, email, phone, city, experience_years)
                                      VALUES (?, ?, ?, ?, ?)""", (name, email, phone, city, 0))
                user_id = cur.lastrowid
            duplicate = conn.execute("SELECT application_id FROM Applications WHERE user_id=? AND vacancy_id=?", (user_id, vacancy_id)).fetchone()
            if duplicate:
                flash("Сіз бұл вакансияға өтінімді бұрын жібергенсіз.", "error")
                return redirect(url_for("vacancy_detail", vacancy_id=vacancy_id))
            conn.execute("""INSERT INTO Applications (user_id, vacancy_id, application_date, status)
                            VALUES (?, ?, ?, ?)""", (user_id, vacancy_id, date.today().isoformat(), "Қаралуда"))
            conn.commit()
        flash("Өтініміңіз сәтті қабылданды! Рақмет.", "success")
        return redirect(url_for("vacancies"))
    except sqlite3.Error as exc:
        flash(f"Өтінімді сақтау кезінде қате пайда болды: {exc}", "error")
        return redirect(url_for("vacancy_detail", vacancy_id=vacancy_id))


@app.route("/companies")
def companies():
    with get_db() as conn:
        rows = conn.execute("""SELECT c.company_id, c.company_name, c.industry, c.city,
                                      COUNT(v.vacancy_id) AS vacancy_count
                               FROM Companies c LEFT JOIN Vacancies v ON v.company_id=c.company_id
                               GROUP BY c.company_id ORDER BY c.company_name""").fetchall()
    return render_template("companies.html", companies=rows)


@app.route("/skills")
def skills():
    with get_db() as conn:
        rows = conn.execute("""SELECT s.skill_id, s.skill_name, s.category,
                                      COUNT(DISTINCT vs.vacancy_id) AS vacancy_count
                               FROM Skills s LEFT JOIN Vacancy_Skills vs ON vs.skill_id=s.skill_id
                               GROUP BY s.skill_id ORDER BY s.category, s.skill_name""").fetchall()
    return render_template("skills.html", skills=rows)


@app.route("/applications")
def applications():
    # Applicant names and contact details are intentionally not exposed on the public website.
    with get_db() as conn:
        rows = conn.execute("""SELECT a.application_id, v.title AS vacancy_title,
                                      a.application_date, a.status
                               FROM Applications a LEFT JOIN Vacancies v ON v.vacancy_id=a.vacancy_id
                               ORDER BY a.application_id DESC""").fetchall()
    return render_template("applications.html", applications=rows)


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


check_database()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
