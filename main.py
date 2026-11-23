"""
CareerHub — SQLite деректер базасымен жұмыс істейтін жұмыс іздеу жүйесі.
Бар кестелерді қолданады. CREATE TABLE және DROP TABLE сұраныстары жоқ.
Іске қосу: python main.py
"""
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "database" / "vacancies.db"

TABLES = {
    "Users", "Companies", "Vacancies", "Skills",
    "User_Skills", "Vacancy_Skills", "Applications"
}


def db_connect():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Деректер базасы табылмады: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    names = {r["name"] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )}
    missing = TABLES - names
    if missing:
        conn.close()
        raise RuntimeError("Кестелер табылмады: " + ", ".join(sorted(missing)))
    return conn


class CareerHubApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CareerHub — жұмыс орындарын іздеу жүйесі")
        self.root.geometry("1180x720")
        self.root.minsize(900, 580)
        self.current_rows = []
        self.setup_style()
        self.build_ui()
        self.refresh_all()

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Arial", 19, "bold"))
        style.configure("Sub.TLabel", font=("Arial", 10))
        style.configure("Treeview", rowheight=29, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Accent.TButton", font=("Arial", 10, "bold"), padding=7)

    def build_ui(self):
        header = ttk.Frame(self.root, padding=(18, 14))
        header.pack(fill="x")
        ttk.Label(header, text="CareerHub", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Бос жұмыс орындарын іздеу және өтінімдерді басқару жүйесі",
            style="Sub.TLabel"
        ).pack(anchor="w", pady=(3, 0))

        self.stats_var = tk.StringVar(value="Деректер базасы жүктелуде...")
        ttk.Label(self.root, textvariable=self.stats_var,
                  padding=(18, 4)).pack(fill="x")

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=15, pady=10)

        self.vacancy_tab = ttk.Frame(self.tabs, padding=10)
        self.company_tab = ttk.Frame(self.tabs, padding=10)
        self.users_tab = ttk.Frame(self.tabs, padding=10)
        self.skills_tab = ttk.Frame(self.tabs, padding=10)
        self.apps_tab = ttk.Frame(self.tabs, padding=10)

        self.tabs.add(self.vacancy_tab, text="Вакансиялар")
        self.tabs.add(self.company_tab, text="Компаниялар")
        self.tabs.add(self.users_tab, text="Пайдаланушылар")
        self.tabs.add(self.skills_tab, text="Дағдылар")
        self.tabs.add(self.apps_tab, text="Өтінімдер")

        self.build_vacancies_tab()
        self.build_simple_tab(self.company_tab, "companies")
        self.build_simple_tab(self.users_tab, "users")
        self.build_simple_tab(self.skills_tab, "skills")
        self.build_simple_tab(self.apps_tab, "applications")

        footer = ttk.Frame(self.root, padding=(15, 4, 15, 12))
        footer.pack(fill="x")
        ttk.Label(footer, text=f"SQLite деректер базасы: {DB_PATH.name}").pack(side="left")
        ttk.Button(footer, text="Барлық кестені жаңарту",
                   command=self.refresh_all).pack(side="right")

    def make_tree(self, parent, columns, headings, widths=None):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, pady=(8, 0))
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        for i, col in enumerate(columns):
            tree.heading(col, text=headings[i])
            tree.column(col, width=(widths[i] if widths else 140),
                        minwidth=80, anchor="w")
        return tree

    def build_vacancies_tab(self):
        search = ttk.LabelFrame(self.vacancy_tab, text="Вакансияларды іздеу", padding=10)
        search.pack(fill="x")
        ttk.Label(search, text="Атауы немесе компания:").grid(row=0, column=0, sticky="w")
        self.query_var = tk.StringVar()
        query = ttk.Entry(search, textvariable=self.query_var, width=28)
        query.grid(row=1, column=0, padx=(0, 10), pady=5, sticky="ew")
        ttk.Label(search, text="Қала:").grid(row=0, column=1, sticky="w")
        self.city_var = tk.StringVar()
        self.city_box = ttk.Combobox(search, textvariable=self.city_var,
                                     state="readonly", width=18)
        self.city_box.grid(row=1, column=1, padx=(0, 10), pady=5, sticky="ew")
        ttk.Label(search, text="Ең төменгі жалақы (₸):").grid(row=0, column=2, sticky="w")
        self.salary_var = tk.StringVar()
        ttk.Entry(search, textvariable=self.salary_var, width=16).grid(
            row=1, column=2, padx=(0, 10), pady=5, sticky="ew")
        ttk.Label(search, text="Тәжірибе (жылға дейін):").grid(row=0, column=3, sticky="w")
        self.exp_var = tk.StringVar()
        ttk.Entry(search, textvariable=self.exp_var, width=12).grid(
            row=1, column=3, padx=(0, 10), pady=5, sticky="ew")
        ttk.Button(search, text="Іздеу", style="Accent.TButton",
                   command=self.load_vacancies).grid(row=1, column=4, padx=4)
        ttk.Button(search, text="Тазарту", command=self.reset_filters).grid(
            row=1, column=5, padx=4)
        for col in range(4):
            search.columnconfigure(col, weight=1)

        self.vacancy_tree = self.make_tree(
            self.vacancy_tab,
            ("id", "title", "company", "city", "salary", "experience", "skills"),
            ("ID", "Лауазым", "Компания", "Қала", "Жалақы (₸)", "Тәжірибе", "Қажетті дағдылар"),
            (55, 190, 170, 110, 115, 90, 240)
        )
        self.vacancy_tree.bind("<<TreeviewSelect>>", self.show_selected_vacancy)

        details = ttk.LabelFrame(self.vacancy_tab, text="Вакансия туралы ақпарат", padding=9)
        details.pack(fill="x", pady=(9, 0))
        self.detail_var = tk.StringVar(value="Толық ақпаратты көру үшін вакансияны таңдаңыз.")
        ttk.Label(details, textvariable=self.detail_var, wraplength=1000).pack(anchor="w")
        ttk.Button(details, text="Таңдалған вакансияға өтінім беру",
                   style="Accent.TButton", command=self.open_application_form).pack(
                       anchor="e", pady=(7, 0))

    def build_simple_tab(self, parent, kind):
        configs = {
            "companies": (("id", "name", "industry", "city", "email"),
                          ("ID", "Компания", "Сала", "Қала", "Email"),
                          (60, 230, 160, 130, 220)),
            "users": (("id", "name", "email", "phone", "city", "experience"),
                      ("ID", "Аты-жөні", "Email", "Телефон", "Қала", "Тәжірибе"),
                      (60, 190, 220, 150, 130, 100)),
            "skills": (("id", "name", "category"),
                       ("ID", "Дағды", "Санат"), (60, 240, 220)),
            "applications": (("id", "user", "vacancy", "date", "status"),
                             ("ID", "Үміткер", "Вакансия", "Күні", "Мәртебесі"),
                             (60, 200, 260, 130, 150))
        }
        cols, heads, widths = configs[kind]
        tree = self.make_tree(parent, cols, heads, widths)
        setattr(self, kind + "_tree", tree)

    def refresh_all(self):
        try:
            self.load_vacancies()
            self.load_companies()
            self.load_users()
            self.load_skills()
            self.load_applications()
            with db_connect() as conn:
                vacancies = conn.execute("SELECT COUNT(*) FROM Vacancies").fetchone()[0]
                companies = conn.execute("SELECT COUNT(*) FROM Companies").fetchone()[0]
                users = conn.execute("SELECT COUNT(*) FROM Users").fetchone()[0]
                applications = conn.execute("SELECT COUNT(*) FROM Applications").fetchone()[0]
                cities = [r[0] for r in conn.execute(
                    "SELECT DISTINCT city FROM Vacancies WHERE city IS NOT NULL ORDER BY city"
                )]
            self.city_box["values"] = [""] + cities
            self.stats_var.set(
                f"Вакансиялар: {vacancies}    Компаниялар: {companies}    "
                f"Пайдаланушылар: {users}    Өтінімдер: {applications}"
            )
        except Exception as exc:
            messagebox.showerror("Деректер базасының қатесі", str(exc))

    def load_vacancies(self):
        sql = """
            SELECT v.vacancy_id, v.title, c.company_name, v.city, v.salary,
                   v.experience_years,
                   GROUP_CONCAT(s.skill_name, ', ') AS skills,
                   v.description, c.industry
            FROM Vacancies v
            LEFT JOIN Companies c ON c.company_id = v.company_id
            LEFT JOIN Vacancy_Skills vs ON vs.vacancy_id = v.vacancy_id
            LEFT JOIN Skills s ON s.skill_id = vs.skill_id
            WHERE 1=1
        """
        values = []
        q = self.query_var.get().strip()
        city = self.city_var.get().strip()
        salary = self.salary_var.get().strip()
        exp = self.exp_var.get().strip()
        if q:
            sql += " AND (v.title LIKE ? OR c.company_name LIKE ? OR v.description LIKE ?)"
            values.extend([f"%{q}%"] * 3)
        if city:
            sql += " AND v.city = ?"
            values.append(city)
        if salary:
            try:
                values.append(float(salary))
            except ValueError:
                messagebox.showwarning("Ескерту", "Жалақыны санмен енгізіңіз.")
                return
            sql += " AND v.salary >= ?"
        if exp:
            try:
                values.append(int(exp))
            except ValueError:
                messagebox.showwarning("Ескерту", "Тәжірибені бүтін санмен енгізіңіз.")
                return
            sql += " AND v.experience_years <= ?"
        sql += " GROUP BY v.vacancy_id ORDER BY v.salary DESC"
        with db_connect() as conn:
            rows = conn.execute(sql, values).fetchall()
        self.vacancy_tree.delete(*self.vacancy_tree.get_children())
        self.current_rows = [dict(r) for r in rows]
        for r in rows:
            self.vacancy_tree.insert("", "end", values=(
                r["vacancy_id"], r["title"], r["company_name"] or "",
                r["city"] or "", f'{r["salary"]:,.0f}' if r["salary"] is not None else "",
                r["experience_years"] if r["experience_years"] is not None else "",
                r["skills"] or ""
            ))

    def show_selected_vacancy(self, _event=None):
        selected = self.vacancy_tree.selection()
        if not selected:
            return
        values = self.vacancy_tree.item(selected[0], "values")
        vacancy_id = int(values[0])
        row = next((r for r in self.current_rows if r["vacancy_id"] == vacancy_id), None)
        if row:
            self.detail_var.set(
                f'{row["title"]} | {row["company_name"] or "Компания"} | '
                f'{row["city"] or "Қала көрсетілмеген"}\n'
                f'{row["description"] or "Сипаттама жоқ"}\n'
                f'Сала: {row["industry"] or "Көрсетілмеген"} | '
                f'Дағдылар: {row["skills"] or "Көрсетілмеген"}'
            )

    def reset_filters(self):
        self.query_var.set("")
        self.city_var.set("")
        self.salary_var.set("")
        self.exp_var.set("")
        self.load_vacancies()

    def open_application_form(self):
        selected = self.vacancy_tree.selection()
        if not selected:
            messagebox.showinfo("Ақпарат", "Алдымен вакансияны таңдаңыз.")
            return
        vacancy_id = int(self.vacancy_tree.item(selected[0], "values")[0])
        win = tk.Toplevel(self.root)
        win.title("Вакансияға өтінім беру")
        win.geometry("420x350")
        win.resizable(False, False)
        frame = ttk.Frame(win, padding=18)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Өтінім беруші туралы мәлімет",
                  font=("Arial", 13, "bold")).pack(anchor="w", pady=(0, 12))
        entries = {}
        for key, label in [
            ("name", "Аты-жөні *"), ("email", "Email *"),
            ("phone", "Телефон"), ("city", "Қала")
        ]:
            ttk.Label(frame, text=label).pack(anchor="w")
            entry = ttk.Entry(frame)
            entry.pack(fill="x", pady=(2, 8))
            entries[key] = entry

        def save():
            name = entries["name"].get().strip()
            email = entries["email"].get().strip()
            phone = entries["phone"].get().strip()
            city = entries["city"].get().strip()
            if not name or not email or "@" not in email:
                messagebox.showwarning("Ескерту", "Аты-жөні мен дұрыс email енгізіңіз.", parent=win)
                return
            try:
                with db_connect() as conn:
                    exists = conn.execute(
                        "SELECT user_id FROM Users WHERE email = ? ORDER BY user_id LIMIT 1",
                        (email,)
                    ).fetchone()
                    if exists:
                        user_id = exists["user_id"]
                    else:
                        cur = conn.execute(
                            """INSERT INTO Users
                               (full_name, email, phone, city, experience_years)
                               VALUES (?, ?, ?, ?, ?)""",
                            (name, email, phone, city, 0)
                        )
                        user_id = cur.lastrowid

                    duplicate = conn.execute(
                        """SELECT application_id FROM Applications
                           WHERE user_id = ? AND vacancy_id = ?""",
                        (user_id, vacancy_id)
                    ).fetchone()
                    if duplicate:
                        messagebox.showinfo("Ақпарат", "Сіз бұл вакансияға өтінім жібергенсіз.", parent=win)
                        return
                    conn.execute(
                        """INSERT INTO Applications
                           (user_id, vacancy_id, application_date, status)
                           VALUES (?, ?, ?, ?)""",
                        (user_id, vacancy_id, date.today().isoformat(), "Қаралуда")
                    )
                    conn.commit()
                win.destroy()
                self.refresh_all()
                messagebox.showinfo("Сәтті", "Өтінім SQLite базасына сақталды.")
            except Exception as exc:
                messagebox.showerror("Қате", str(exc), parent=win)

        ttk.Button(frame, text="Өтінімді сақтау", style="Accent.TButton",
                   command=save).pack(fill="x", pady=(8, 0))

    def load_companies(self):
        with db_connect() as conn:
            rows = conn.execute(
                "SELECT company_id, company_name, industry, city, email FROM Companies ORDER BY company_name"
            ).fetchall()
        self.fill_tree(self.companies_tree, rows)

    def load_users(self):
        with db_connect() as conn:
            rows = conn.execute(
                """SELECT user_id, full_name, email, phone, city, experience_years
                   FROM Users ORDER BY full_name"""
            ).fetchall()
        self.fill_tree(self.users_tree, rows)

    def load_skills(self):
        with db_connect() as conn:
            rows = conn.execute(
                "SELECT skill_id, skill_name, category FROM Skills ORDER BY skill_name"
            ).fetchall()
        self.fill_tree(self.skills_tree, rows)

    def load_applications(self):
        with db_connect() as conn:
            rows = conn.execute(
                """SELECT a.application_id, u.full_name, v.title,
                          a.application_date, a.status
                   FROM Applications a
                   LEFT JOIN Users u ON u.user_id = a.user_id
                   LEFT JOIN Vacancies v ON v.vacancy_id = a.vacancy_id
                   ORDER BY a.application_id DESC"""
            ).fetchall()
        self.fill_tree(self.applications_tree, rows)

    @staticmethod
    def fill_tree(tree, rows):
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", "end", values=tuple(row))


def main():
    try:
        with db_connect() as conn:
            count = conn.execute("SELECT COUNT(*) FROM Vacancies").fetchone()[0]
        root = tk.Tk()
        app = CareerHubApp(root)
        root.mainloop()
    except Exception as exc:
        messagebox.showerror("Іске қосу қатесі", str(exc))
        raise


if __name__ == "__main__":
    main()
