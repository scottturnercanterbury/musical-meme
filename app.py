from __future__ import annotations

import os
import sqlite3
from decimal import Decimal, InvalidOperation

from flask import Flask, abort, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")

DB_PATH = os.path.join(os.path.dirname(__file__), "payroll.db")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                salary_gbp_pence INTEGER NOT NULL CHECK (salary_gbp_pence >= 0)
            )
            """
        )
        conn.commit()


def parse_gbp_to_pence(raw: str) -> int:
    """
    Accepts inputs like:
      "1234.56", "1,234.56", "£1234.56", "1234", "0.99"
    Returns integer pence.
    """
    if raw is None:
        raise ValueError("Salary is required.")

    cleaned = raw.strip().replace("£", "").replace(",", "")
    if cleaned == "":
        raise ValueError("Salary is required.")

    try:
        value = Decimal(cleaned)
    except InvalidOperation as e:
        raise ValueError("Salary must be a valid number.") from e

    if value < 0:
        raise ValueError("Salary must be zero or greater.")

    # Round to nearest penny (2 dp)
    value = value.quantize(Decimal("0.01"))
    pence = int(value * 100)
    return pence


def format_pence_as_gbp(pence: int) -> str:
    pounds = Decimal(pence) / Decimal(100)
    return f"£{pounds:,.2f}"


@app.context_processor
def inject_helpers():
    return {"format_gbp": format_pence_as_gbp}


@app.route("/")
def index():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, name, salary_gbp_pence FROM employees ORDER BY id DESC"
        ).fetchall()
    return render_template("index.html", employees=rows)


@app.route("/employees/add", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        salary_raw = request.form.get("salary") or ""

        if not name:
            flash("Name is required.", "error")
            return render_template("add.html", name=name, salary=salary_raw), 400

        try:
            salary_pence = parse_gbp_to_pence(salary_raw)
        except ValueError as e:
            flash(str(e), "error")
            return render_template("add.html", name=name, salary=salary_raw), 400

        with get_db() as conn:
            conn.execute(
                "INSERT INTO employees (name, salary_gbp_pence) VALUES (?, ?)",
                (name, salary_pence),
            )
            conn.commit()

        flash("Employee record added.", "success")
        return redirect(url_for("index"))

    return render_template("add.html", name="", salary="")


@app.route("/employees/<int:emp_id>")
def view_employee(emp_id: int):
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, name, salary_gbp_pence FROM employees WHERE id = ?",
            (emp_id,),
        ).fetchone()

    if row is None:
        abort(404)

    return render_template("view.html", employee=row)


@app.route("/employees/<int:emp_id>/edit", methods=["GET", "POST"])
def edit_employee(emp_id: int):
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, name, salary_gbp_pence FROM employees WHERE id = ?",
            (emp_id,),
        ).fetchone()

    if row is None:
        abort(404)

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        salary_raw = request.form.get("salary") or ""

        if not name:
            flash("Name is required.", "error")
            return render_template(
                "edit.html",
                employee=row,
                name=name,
                salary=salary_raw,
            ), 400

        try:
            salary_pence = parse_gbp_to_pence(salary_raw)
        except ValueError as e:
            flash(str(e), "error")
            return render_template(
                "edit.html",
                employee=row,
                name=name,
                salary=salary_raw,
            ), 400

        with get_db() as conn:
            conn.execute(
                "UPDATE employees SET name = ?, salary_gbp_pence = ? WHERE id = ?",
                (name, salary_pence, emp_id),
            )
            conn.commit()

        flash("Employee record updated.", "success")
        return redirect(url_for("view_employee", emp_id=emp_id))

    # Pre-fill form
    salary_prefill = str(Decimal(row["salary_gbp_pence"]) / Decimal(100))
    return render_template(
        "edit.html",
        employee=row,
        name=row["name"],
        salary=salary_prefill,
    )


@app.route("/employees/<int:emp_id>/delete", methods=["POST"])
def delete_employee(emp_id: int):
    with get_db() as conn:
        cur = conn.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
        conn.commit()

    if cur.rowcount == 0:
        abort(404)

    flash("Employee record deleted.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)